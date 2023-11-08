import json
import sys

import client

USAGE_STR = 'USAGE: python manual.py [sample_sources|get_articles]'
NUM_ARGS = 1

USAGE_STR_SAMPLE_SOURCES = 'USAGE: python manual.py sample_sources [country] [newskey_path] [awskey_path] [output]'
NUM_ARGS_SAMPLE_SOURCES = 4

USAGE_STR_GET_ARTICLES = 'USAGE: python manual.py get_articles [country] [language] [year] [month] [query] [max] [newskey_path] [awskey_path] [output]'
NUM_ARGS_GET_ARTICLES = 9


def build_query_facade(news_key_path, aws_key_path):
    with open(news_key_path) as f:
        news_key = f.read().strip()

    with open(aws_key_path) as f:
        aws_key = json.load(f)

    return client.QueryFacade(news_key, aws_key)


def main_sample_sources(args):
    if len(args) != NUM_ARGS_SAMPLE_SOURCES:
        print(USAGE_STR_SAMPLE_SOURCES)
        sys.exit(1)

    country = args[0].lower().strip()
    news_key_path = args[1]
    aws_key_path = args[2]
    output_path = args[3]

    facade = build_query_facade(news_key_path, aws_key_path)

    results = facade.sample_sources(country)

    with open(output_path, 'w') as f:
        payload = {
            'sources': [x.to_dict() for x in results]
        }
        json.dump(payload, f)


def main_get_articles(args):
    if len(args) != NUM_ARGS_GET_ARTICLES:
        print(USAGE_STR_GET_ARTICLES)
        sys.exit(1)

    country = args[0].lower().strip()
    language = args[1].lower().strip()
    year = int(args[2].strip())
    month = int(args[3].strip())
    query = args[4]
    max_count = int(args[5].strip())
    news_key_path = args[6]
    aws_key_path = args[7]
    output_path = args[8]

    facade = build_query_facade(news_key_path, aws_key_path)

    results = facade.get_articles(
        country=country,
        language=language,
        year=year,
        month=month,
        query=query,
        max_count=max_count
    )

    with open(output_path, 'w') as f:
        payload = {
            'articles': [x.to_dict() for x in results]
        }
        json.dump(payload, f)


def main():
    if len(sys.argv) < NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    command = sys.argv[1]
    additional_args = sys.argv[2:]

    if command == 'sample_sources':
        main_sample_sources(additional_args)
    elif command == 'get_articles':
        main_get_articles(additional_args)
    else:
        print('Unknown command: ' + command)
        sys.exit(1)


if __name__ == '__main__':
    main()
