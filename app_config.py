import logging
import logging.handlers
from datetime import datetime

from PyQt6.QtGui import QFont


class ConfigUtil:
    """ 설정 클래스 """
    _instance = None
    __inited: bool = False
    __list_none_value: list = [None, '', 'None', 'NULL']
    __result_column: list = ['Tagname', 'Timestamp', 'Value', 'Quality']

    def __new__(cls, *args, **kwargs) -> _instance:
        if cls._instance is None:
            cls._instance = super(ConfigUtil, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_file_name: str = None) -> None:
        if not self.__inited:
            self.__inited = True

    def get_none_values(self) -> list:
        return self.__list_none_value

    def get_result_column(self) -> list:
        return self.__result_column

    def get_csv_field(self) -> list:
        return self.__result_column[:-1]

    def get_default_font(self, font_size: int = 12) -> QFont:
        return QFont('Nanum Gothic', font_size, QFont.Weight.Light)


class LogUtil:
    """ 로그관련 클래스 """
    _instance = None
    __inited: bool = False
    __logger: logging.Logger = None

    def __new__(cls, *args, **kwargs) -> _instance:
        if cls._instance is None:
            cls._instance = super(LogUtil, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self.__inited:
            self.__inited = True
            self.__logger = logging.getLogger(name=__name__)
            _log_format: str = '[%(asctime)s-%(levelname)s] >> %(message)s'
            _log_formatter: logging.Formatter = logging.Formatter(fmt=_log_format)
            _file_max_bytes: int = 100 * 1024 * 1024
            _file_name_prefix: str = datetime.now().strftime('%y%m%d')
            _file_name: str = f'historianTag.log'

            _log_file_handler: logging.handlers.TimedRotatingFileHandler = logging.handlers.TimedRotatingFileHandler(
                filename=f'./{_file_name}',
                when='midnight',
                interval=1,
                backupCount=20,
                encoding='utf-8'
            )
            _log_file_handler.prefix = _file_name_prefix
            _log_file_handler.setFormatter(fmt=_log_formatter)

            self.__logger.propagate = False
            self.__logger.setLevel(level=logging.INFO)
            self.__logger.addHandler(hdlr=_log_file_handler)

    def get_logger(self) -> logging.Logger:
        """ 로거 가져오기
            Returns:
                self.__logger (logging.Logger): 로거
        """
        return self.__logger

    def info(self, message: str) -> None:
        """ 인포로그 기록
            Args:
                message (str): 표시할 메세지
        """
        self.__logger.log(level=logging.INFO, msg=message)

    def error(self, message: str) -> None:
        """ 에러로그 기록
            Args:
                message (str): 표시할 메세지
        """
        self.__logger.log(level=logging.ERROR, msg=message)
