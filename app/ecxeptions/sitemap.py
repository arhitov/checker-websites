class SitemapError(RuntimeError):
    def __init__(self, message, url: str, original_exception=None):
        super().__init__(message)
        self.url = url
        if original_exception is not None:
            self.original_exception = original_exception
