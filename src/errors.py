import src.logger as logger


class LoggedRuntimeError(Exception):
    def __init__(self, tag, message):
        self.message = message
        logger.e(tag, self.message)
