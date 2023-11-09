import csv
import json

import client


class TranslateChunker:
    
    def __init__(self, max_size=950):
        self._current_word = ''
        self._current_chunk = ''
        self._chunks = []
        self._max_size = max_size
        self._finished = False
    
    def process(self, char):
        assert not self._finished
        
        if char == ' ':
            self._accept_current_word()
        else:
            self._current_word += char
    
    def finish(self):
        assert not self._finished
        self._accept_current_word()
        self._accept_current_chunk()
        self._finished = True
    
    def get_chunks(self):
        assert self._finished
        
        def is_ok_size(target):
            length = len(target)
            return length > 0 and length < self._max_size
        
        return filter(is_ok_size, self._chunks)
    
    def _accept_current_chunk(self):
        self._chunks.append(self._current_chunk.strip())
        self._current_chunk = ''
    
    def _accept_current_word(self):
        if len(self._current_word) > self._max_size:
            self._current_word = self._current_word[:self._max_size]
        
        possible_size = len(self._current_chunk) + len(self._current_word) + 1
        if possible_size > self._max_size:
            self._accept_current_chunk()
        
        self._current_chunk = self._current_chunk + ' ' + self._current_word
        self._current_word = ''


def build_query_facade(news_key_path, aws_key_path):
    with open(news_key_path) as f:
        news_key = f.read().strip()

    with open(aws_key_path) as f:
        aws_key = json.load(f)

    return client.QueryFacade(news_key, aws_key)


def load_country_codes(countries_loc):
    with open(countries_loc) as f:
        countries_reader = csv.DictReader(f)
        country_codes = map(lambda x: x['Country Code'], countries_reader)
        country_codes_clean = map(lambda x: x.strip().lower(), country_codes)
        return list(country_codes_clean)
