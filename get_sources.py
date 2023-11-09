import itertools
import sys

import util

USAGE_STR = 'python get_sources.py [newskey_path] [awskey_path] [countries] [output]'
NUM_ARGS = 4
OUTPUT_COLUMNS = ['name', 'url', 'categories', 'language', 'country']


def simplify_record(record):
    return {
        'name': record['name'],
        'url': record['url'],
        'categories': ';'.join(record['categories']),
        'language': record['language'],
        'country': record['country']
    }


def main():
    if len(sys.argv) != NUM_ARGS + 1:
        print(USAGE_STR)
        sys.exit(1)

    news_key_path = sys.argv[1]
    aws_key_path = sys.argv[2]
    countries_loc = sys.argv[3]
    output_loc = sys.argv[4]

    facade = util.build_query_facade(news_key_path, aws_key_path)
    country_codes = util.load_country_codes(countries_loc)

    sources_by_country = map(lambda country: facade.sample_sources(country), country_codes)
    sources_flat = itertools.chain(*sources_by_country)
    sources_dict = map(lambda record: record.to_dict(), sources_flat)
    sources_dict_simple = map(simplify_record, sources_dict)

    with open(output_loc, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(sources_dict_simple)


if __name__ == '__main__':
    main()
