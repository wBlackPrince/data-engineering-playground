import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

class AppLogger:
    def __init__(self) -> None:
        self._logger = logging.getLogger('app_logger')

    def log_debug(self, message: str) -> None:
        self._logger.debug(message)

    def log_info(self, message: str) -> None:
        self._logger.info(message)

    def log_error(self, message: str) -> None:
        self._logger.error(message)

    def log_critical(self, message: str) -> None:
        self._logger.critical(message)