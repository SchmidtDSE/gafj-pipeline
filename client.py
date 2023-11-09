import csv
import datetime
import dateutil.relativedelta
import json
import os
import queue
import random
import time
import urllib.parse

import boto3
import requests

import record_struct
import util


class NewsDataIterable:

    def __init__(self, url, params, max_count=None):
        self._url = url
        self._params = params
        self._max_count = max_count
        self._has_limit = self._max_count is not None

        self._count = 0
        self._next_page = None
        self._done = False
        self._waiting_results = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        if self._waiting_results.empty():
            self._make_internal_request()
        
        exceeded_limit = self._has_limit and self._count > self._max_count
        if self._done or exceeded_limit:
            raise StopIteration()

        assert not self._waiting_results.empty()

        self._count += 1
        return self._waiting_results.get()

    def _make_internal_request(self, retry=True):
        if self._next_page:
            self._params['page'] = self._next_page

        response = requests.get(
            self._url,
            params=self._params
        )

        if response.status_code != 200:
            if 'TooManyRequests' in response.text and retry:
                time.sleep(random.randint(30, 90))
                return self._make_internal_request(retry=False)
            else:
                raise RuntimeError('Error (%d): %s' % (response.status_code, response.text))

        results_json = response.json()
        results = results_json['results']

        if len(results) == 0:
            self._done = True
        else:
            self._next_page = results_json['nextPage']

        for result in results:
            self._waiting_results.put(result)


class LanguageCodeGetter:

    def __init__(self, path=None):
        if path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, 'samples', 'docs_languages.csv')

        with open(path) as f:
            records = csv.DictReader(f)
            records_sanitized = map(
                lambda x: (
                    x['Language'].lower().strip(),
                    x['Language Code'].lower().strip()
                ),
                records
            )
            self._indexed_languages = dict(records_sanitized)

    def lookup(self, full_name):
        full_name_safe = full_name.lower().strip()
        return self._indexed_languages[full_name_safe]


class QueryFacade:
    
    def __init__(self, news_data_key, aws_key, news_data_endpoint=None, aws_region=None):
        self._translate_cache = {}
        
        self._news_data_key = news_data_key
        self._aws_key = aws_key
        
        if news_data_endpoint is None:
            news_data_endpoint = 'https://newsdata.io/api/1/'
        
        self._news_data_endpoint = news_data_endpoint
        
        if aws_region is None:
            aws_region = 'us-east-2'
        
        self._aws_region = aws_region
        
        self._translate_client = self._build_translate_client()
    
    def sample_sources(self, country, max_count=100):
        language_code_getter = LanguageCodeGetter()

        def parse_record(record):
            name = record['source_id']
            url = urllib.parse.urlparse(record['link']).netloc
            categories = record['category']
            language = language_code_getter.lookup(record['language'])
            return record_struct.Source(name, url, categories, language, country)
        
        def get_for_priority(priority, top=True):
            url = self._news_data_endpoint + 'news'
            params = {
                'prioritydomain': priority,
                'country': country,
                'apikey': self._news_data_key
            }
            
            if top:
                params['category'] = 'top'
            
            raw_results = NewsDataIterable(url, params, max_count=max_count)
            parsed_results = map(lambda record: parse_record(record), raw_results)
            
            output_names = set()
            output_records = []
            for result in parsed_results:
                if result.get_name() not in output_names:
                    output_names.add(result.get_name())
                    output_records.append(result)
            
            return output_records
        
        sources = get_for_priority('top', top=True)
        
        if len(sources) < 5:
            sources += get_for_priority('medium', top=True)
        
        if len(sources) < 5:
            sources += get_for_priority('top', top=False)
        
        if len(sources) < 5:
            sources += get_for_priority('medium', top=False)
        
        return sources
    
    def get_articles(self, country='gb', language='en', year=2023, month=6,
        query='Food', domain=None, priority='top', max_count=None):
        from_date = datetime.date(year, month, 1)
        to_date_exclusive = from_date + dateutil.relativedelta.relativedelta(months=1)
        to_date = to_date_exclusive + dateutil.relativedelta.relativedelta(days=-1)
        query_translated = self.translate(query, to=language, cache=True)

        url = self._news_data_endpoint + 'archive'
        params = {
            'country': country,
            'language': language,
            'from_date': from_date,
            'to_date': to_date,
            'qInTitle': query_translated.get_translated(),
            'apikey': self._news_data_key,
            'prioritydomain': priority
        }
        
        if domain:
            params['domainurl'] = domain

        results = NewsDataIterable(url, params, max_count=max_count)

        locale = record_struct.Locale(country, language)

        def parse_result(record):
            url = record['link']
            keywords = record['keywords']
            creator = record['creator']
            publish_datetime = record['pubDate']
            category = record['category']

            title_untranslated = record['title']

            content_pieces = [
                record['content'],
                record['description']
            ]
            content_pieces_valid = filter(
                lambda x: x != None,
                content_pieces
            )
            content_untranslated = ' '.join(content_pieces_valid)

            title = self.translate(title_untranslated, source=language)
            content = self.translate(content_untranslated, source=language)

            return record_struct.Article(
                url,
                title,
                keywords,
                creator,
                content,
                publish_datetime,
                category,
                locale
            )

        parsed_results = map(parse_result, results)
        return parsed_results
    
    def translate(self, target, source='en', to='en', cache=False):
        if source == to:
            return record_struct.TranslatedText(target, source, target, to)

        if not cache:
            return self._translate_force(target, source=source, to=to)
        
        assert 'en' in [source, to]

        if target not in self._translate_cache:
            self._translate_cache[target] = {}

        if to not in self._translate_cache[target]:
            translated = self._translate_force(target, source=source, to=to)
            self._translate_cache[target][to] = translated

        return self._translate_cache[target][to]
    
    def _build_translate_client(self):
        return boto3.client(
            service_name='translate',
            region_name=self._aws_region,
            use_ssl=True,
            aws_access_key_id=self._aws_key['access'],
            aws_secret_access_key=self._aws_key['secret']
        )
    
    def _translate_force(self, target, source='en', to='en'):
        chunker = util.TranslateChunker()
        
        for char in target:
            chunker.process(char)
        
        chunker.finish()
        
        pieces = list(chunker.get_chunks())
        
        def translate_piece(piece):
            response = self._translate_client.translate_text(
                Text=piece, 
                SourceLanguageCode=source,
                TargetLanguageCode=to,
            )
            return response
        
        pieces_responses = map(translate_piece, pieces)
        pieces_translated = map(lambda x: x['TranslatedText'], pieces_responses)
        translated = ' '.join(pieces_translated)
        
        return record_struct.TranslatedText(
            target,
            source,
            translated,
            to
        )
