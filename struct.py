class TranslatedText:
    
    def __init__(self, original, original_lang, translated, translated_lang):
        self._original = original
        self._original_lang = original_lang
        self._translated = translated
        self._translated_lang = translated_lang
    
    def get_original(self):
        return self._original
    
    def get_original_lang(self):
        return self._original_lang
    
    def get_translated(self):
        return self._translated
    
    def get_translated_lang(self):
        return self._translated_lang
    
    def to_dict(self):
        return {
            'original': {
                'language': self.get_original_lang(),
                'body': self.get_original()
            },
            'translated': {
                'language': self.get_translated_lang(),
                'body': self.get_translated()
            }
        }


class Locale:
    
    def __init__(self, country, language):
        self._country = country
        self._language = language
    
    def get_country(self):
        return self._country
    
    def get_language(self):
        return self._language
    
    def to_dict(self):
        return {
            'country': self.get_country(),
            'language': self.get_language()
        }


class Source:
    
    def __init__(self, name, url, categories, language, country):
        self._name = name
        self._url = url
        self._categories = categories
        self._language = language
        self._country = country
    
    def get_name(self):
        return self._name
    
    def get_url(self):
        return self._url
    
    def get_categories(self):
        return self._categories
    
    def get_language(self):
        return self._language
    
    def get_country(self):
        return self._country
    
    def to_dict(self):
        return {
            'name': self.get_name(),
            'url': self.get_url(),
            'categories': self.get_categories(),
            'language': self.get_language(),
            'country': self.get_country()
        }


class Article:
    
    def __init__(self, url, title, keywords, creator, content, publish_datetime,
        category, locale):
        self._url = url
        self._title = title
        self._keywords = keywords
        self._creator = creator
        self._content = content
        self._publish_datetime = publish_datetime
        self._category = category
        self._locale = locale
    
    def get_url(self):
        return self._url
    
    def get_title(self):
        return self._title
    
    def get_keywords(self):
        return self._keywords
    
    def get_creator(self):
        return self._creator
    
    def get_content(self):
        return self._content
    
    def get_publish_datetime(self):
        return self._publish_datetime
    
    def get_category(self):
        return self._category
    
    def get_locale(self):
        return self._locale
    
    def to_dict(self):
        return {
            'url': self.get_url(),
            'title': self.get_title().to_dict(),
            'content': self.get_content().to_dict(),
            'keywords': self.get_keywords(),
            'creator': self.get_creator(),
            'published': self.get_publish_datetime(),
            'category': self.get_category(),
            'locale': self.get_locale().to_dict()
        }

