class AppException(Exception):
    pass


class NotFoundError(AppException):
    pass


class UnauthorizedError(AppException):
    pass


class BadRequestError(AppException):
    pass
