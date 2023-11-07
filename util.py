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
