class Cache:
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.cache = {}

    def __getitem__(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            raise KeyError(key + " not found in cache")

    def __setitem__(self, key, value):
        if len(self.cache) >= self.maxsize:
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value

    def __contains__(self, key):
        return key in self.cache
