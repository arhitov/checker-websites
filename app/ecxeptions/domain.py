class DomainError(RuntimeError):
    def __init__(self, message, domain: str, original_exception=None):
        super().__init__(message)
        self.domain = domain
        if original_exception is not None:
            self.original_exception = original_exception


class DomainPortError(DomainError):
    def __init__(self, message, domain: str, port: int, original_exception=None):
        super().__init__(message, domain, original_exception)
        self.port = port
