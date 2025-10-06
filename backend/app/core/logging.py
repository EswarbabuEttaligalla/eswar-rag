import structlog


def get_logger(name: str | None = None):
    return structlog.get_logger(name)
