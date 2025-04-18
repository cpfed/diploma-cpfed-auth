class MessageCache:
    _instance = None
    languages = ['kk', 'en', 'ru']

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageCache, cls).__new__(cls)
            cls._instance.messages = {lang: {} for lang in cls.languages}
            cls._instance.load_messages()
        return cls._instance

    def load_messages(self):
        try:
            from .models import TelegramMessage
            messages = TelegramMessage.objects.all()

            for lang in self.languages:
                self.messages[lang].clear()

            for msg in messages.iterator():
                for lang in self.languages:
                    self.messages[lang][msg.code] = getattr(msg, f'data_{lang}')
        except Exception as e:
            pass

    def refresh(self):
        self.load_messages()

    def get_message(self, lang, code):
        if lang in self.messages and code in self.messages[lang]:
            return self.messages[lang][code]

        for other_lang in self.languages:
            if code in self.messages[other_lang]:
                return self.messages[other_lang][code]

        return f"No '{code}' found"

    def matches(self, text, code):
        for lang in self.languages:
            if text.startswith(self.messages[lang][code]):
                return True


message_cache = MessageCache()
