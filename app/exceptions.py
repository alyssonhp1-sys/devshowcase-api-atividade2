class AppError(Exception):
    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)


class BadRequestError(AppError):
    def __init__(self, message: str):
        super().__init__(400, "Bad Request", message)


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(404, "Not Found", message)


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(409, "Conflict", message)
