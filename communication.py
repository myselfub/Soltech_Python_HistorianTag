import asyncio
import ctypes
import json
import os
import platform
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from multiprocessing.pool import worker

import clr

import app_config


class Historian:
    """ 히스토리안 클래스 """
    is_connected: bool = False
    __disposed_value: bool = False
    __list_none_value: list = None
    __local_time: bool or int = False
    __time_format: str = ''
    __server = None
    __ihuApi = None
    __ihuErrEnum = None
    __ihuDataEnum = None
    __ihuQualityEnum = None
    __ihuTagPropertiesEnum = None
    __ihuDataSample = None
    __cConvert = None
    __cDateTime = None
    __cEnum = None
    __apiServer = None
    __apiConnectionProperties = None
    __apiServerConnection = None
    __apiTagQueryParams = None

    def __init__(self, ip: str = '', user: str = '', password: str = '', local_time: str = '-9', time_format: str = '%Y-%m-%d %H:%M:%S') -> None:
        self.__list_none_value = app_config.ConfigUtil().get_none_values()

        if getattr(sys, 'frozen', False):
            _this_path: str = os.path.dirname(sys.executable)
        else:
            _this_path: str = os.path.dirname(os.path.abspath(__file__))

        self.__ip: str = ip
        self.__user: str = user
        self.__password: str = password
        if local_time.lower() == 'true':
            self.__local_time: bool = True
        elif local_time.lower() == 'false':
            self.__local_time: bool = False
        elif re.fullmatch(r'^-?[0-9]$', local_time):
            self.__local_time: int = int(local_time)
        self.__time_format: str = time_format
        _num: str = ''.join(re.findall(r'\d+', platform.architecture()[0]))
        if _num == '32':
            _dll_ihuapi: str = 'IHUAPI_32.dll'
            _dll_utilities: str = 'Utilities_32.dll'
            _dll_client_access: str = 'Proficy.Historian.ClientAccess.API.dll'
        else:
            _dll_ihuapi: str = 'IHUAPI.dll'
            _dll_utilities: str = 'Utilities.dll'
            _dll_client_access: str = 'Proficy.Historian.ClientAccess.API.dll'
        ctypes.CDLL(os.path.join(_this_path, 'dll', _dll_ihuapi))
        clr.AddReference(os.path.join(_this_path, 'dll', _dll_utilities))
        clr.AddReference(os.path.join(_this_path, 'dll', _dll_client_access))
        from Proficy.Historian.UserAPI import (
            IHUAPI,
            ihuErrorCode,
            ihuDataType,
            ihuQualityStatus,
            IHU_DATA_SAMPLE,
            IHU_RAW_QUALITY,
            ihuTagProperties
        )
        from Proficy.Historian.ClientAccess.API import (
            ConnectionProperties,
            ServerConnection,
            TagQueryParams,
            CertificateValidationMode
        )
        from System import DateTime as CDateTime, Convert as CConvert, Enum as CEnum, Single as CSingle, Double as CDouble
        self.__ihuApi: Proficy.Historian.userapi.IHUAPI = IHUAPI
        self.__ihuErrEnum: Proficy.Historian.userapi.ihuErrorCode = ihuErrorCode
        self.__ihuDataEnum: Proficy.Historian.userapi.ihuDataType = ihuDataType
        self.__ihuQualityEnum: Proficy.Historian.userapi.ihuQualityStatus = ihuQualityStatus
        self.__ihuTagPropertiesEnum: Proficy.Historian.userapi.ihuTagProperties = ihuTagProperties
        self.__ihuDataSample: Proficy.Historian.userapi.IHU_DATA_SAMPLE = IHU_DATA_SAMPLE
        self.__ihuRawQuality: Proficy.Historian.userapi.IHU_RAW_QUALITY = IHU_RAW_QUALITY
        self.__cDateTime: System.DateTime = CDateTime
        self.__cConvert: System.Convert = CConvert
        self.__cEnum: System.Enum = CEnum
        self.__cSingle: System.Single = CSingle
        self.__cDouble: System.Double = CDouble
        self.__apiConnectionProperties: Proficy.Historian.ClientAccess.API.ConnectionProperties = ConnectionProperties
        self.__apiServerConnection: Proficy.Historian.ClientAccess.API.ServerConnection = ServerConnection
        self.__apiTagQueryParams: Proficy.Historian.ClientAccess.API.TagQueryParams = TagQueryParams
        self.__apiCertificateValidationMode: Proficy.Historian.ClientAccess.API.CertificateValidationMode = CertificateValidationMode

    def connect(self) -> bool:
        self.is_connected = self.__connect()
        return self.is_connected

    def __connect(self) -> bool:
        _connect_result: tuple = self.__ihuApi.ihuConnect(self.__ip, self.__user, self.__password)
        _err_code: Proficy.Historian.userapi.ihuErrorCode = _connect_result[0]
        self.__server: int = _connect_result[1]
        """
        try:
            _apiConnectionProperties = self.__apiConnectionProperties()
            _apiConnectionProperties.ServerHostName = self.__ip
            _apiConnectionProperties.ServerCertificateValidationMode = self.__cEnum.GetValues(self.__apiCertificateValidationMode)[0]
            _apiConnectionProperties.Username = self.__user
            _apiConnectionProperties.Password = self.__password
            self.__apiServer = self.__apiServerConnection(_apiConnectionProperties)
            self.__apiServer.Connect()
        except Exception as e:
            print(e)
        return True
        """
        return _err_code == self.__ihuErrEnum.OK

    def disposed(self) -> None:
        self.is_connected = False
        return self.__disposed(True)

    def __disposed(self, disposing: bool) -> None:
        if not self.__disposed_value:
            if disposing:
                self.__disconnect()
            self.__disposed_value = True

    def __disconnect(self) -> None:
        self.__ihuApi.ihuDisconnect(self.__server)

    def req_values(self, list_tag: list or str) -> list[dict]:
        _list_result: list[dict] = []
        if list_tag in self.__list_none_value:
            return _list_result
        elif type(list_tag) == str:
            list_tag = json.loads(list_tag)

        if self.is_connected:
            """_list_result = self.__req_values(list_tag=list_tag)"""
            with ThreadPoolExecutor(max_workers=5) as _thread_executor:
                _futures: list = [_thread_executor.submit(self.__req_values, list_tag)]
                try:
                    for _future in as_completed(_futures):
                        for _result in _future.result():
                            _list_result.append(_result)
                except Exception as e:
                    app_config.LogUtil().error(
                        message=f'{self.__module__}.{self.__class__.__name__}.req_values Error: {e}'
                    )
                finally:
                    _thread_executor.shutdown(wait=True)

        return _list_result

    def __req_values(self, list_tag: list[str]) -> list[dict]:
        _read_value_result: tuple = self.__ihuApi.ihuReadCurrentValue(self.__server, list_tag)
        _err_code_read_value_result: Proficy.Historian.userapi.ihuErrorCode = _read_value_result[0]
        _p_data: (
                Proficy.Historian.userapi.IHU_DATA_SAMPLE or
                list[Proficy.Historian.userapi.IHU_DATA_SAMPLE]
        ) = _read_value_result[1]
        _p_err: (
                Proficy.Historian.userapi.ihuErrorCode or
                list[Proficy.Historian.userapi.ihuErrorCode]
        ) = _read_value_result[2]

        _list_result: list[dict] = []
        if _p_data is not None:
            for _idx, _value in enumerate(_p_data):
                _dict_result: dict = {}
                if _p_err[_idx] != self.__ihuErrEnum.INVALID_TAGNAME:
                    _switch: dict = {
                        self.__ihuDataEnum.Undefined: str(_value.Value.Integer),
                        self.__ihuDataEnum.Short: str(_value.Value.Integer),
                        self.__ihuDataEnum.Integer: str(_value.Value.Integer),
                        self.__ihuDataEnum.Float: str(_value.Value.Float),
                        self.__ihuDataEnum.DoubleFloat: str(_value.Value.Float)
                    }
                    _str_value: str = _switch.get(_value.ValueDataType, str(_value.Value.Integer))
                    _timestamp_result: tuple = self.__ihuApi.IHU_TIMESTAMP_ToParts(_value.TimeStamp)
                    _err_code_timestamp: Proficy.Historian.userapi.ihuErrorCode = _timestamp_result[0]
                    _dt_time_before: str = _timestamp_result[1].ToString()
                    if self.__time_format == '%m/%d/%Y %I:%M:%S %p':
                        time_format = '%m/%d/%Y %I:%M:%S %p'
                    else:
                        time_format = '%Y-%m-%d %p %I:%M:%S'
                    _dt_time_before: str = _dt_time_before.replace('오전', 'AM').replace('오후', 'PM')
                    _dt: datetime = datetime.strptime(_dt_time_before, time_format)
                    _result_column: list = app_config.ConfigUtil().get_result_column()
                    for _column_name in _result_column:
                        if 'name' in _column_name.lower():
                            _dict_result[_column_name]: str = _value.Tagname
                        elif 'time' in _column_name.lower():
                            _dict_result[_column_name]: str = _dt.strftime(self.__time_format)
                        elif 'val' in _column_name.lower():
                            _dict_result[_column_name]: str = _str_value
                        elif 'quality' in _column_name.lower() or 'conf' in _column_name.lower():
                            _dict_result[_column_name]: int = \
                                100 if _value.Quality.ToString() == self.__ihuQualityEnum.OPCGood.ToString() else 0
                    _list_result.append(_dict_result)

        return _list_result

    def fetch_values(self, dict_tag: dict or str) -> list[dict]:
        _list_result: list[dict] = []
        if dict_tag in self.__list_none_value:
            return _list_result
        elif type(dict_tag) == str:
            dict_tag = json.loads(dict_tag)

        _str_start: str = dict_tag.get('start')
        if self.__time_format == '%m/%d/%Y %I:%M:%S %p':
            _str_dt_format = '%m/%d/%Y %I:%M:%S %p'
        else:
            _str_dt_format = '%Y-%m-%d %H:%M:%S'
        _str_start = (datetime.strptime(_str_start, _str_dt_format) - timedelta(seconds=1)).strftime(_str_dt_format)
        _str_end: str = dict_tag.get('end')
        _list_tag: list = dict_tag.get('tagList')

        if self.is_connected:
            """_list_result = self.__fetch_values(list_tag=_list_tag, str_start=_str_start, str_end=_str_end)"""
            with ThreadPoolExecutor(max_workers=5) as _thread_executor:
                _futures: list = [_thread_executor.submit(self.__fetch_values, _list_tag, _str_start, _str_end)]
                try:
                    for _future in as_completed(_futures):
                        for _result in _future.result():
                            _list_result.append(_result)
                except Exception as e:
                    app_config.LogUtil().error(
                        message=f'{self.__module__}.{self.__class__.__name__}.fetch_values Error: {e}'
                    )
                finally:
                    _thread_executor.shutdown(wait=True)

        return _list_result

    def __fetch_values(self, list_tag: list[str], str_start: str, str_end: str) -> list:
        _result: list[dict] = []
        try:
            if type(self.__local_time) == bool:
                if self.__local_time:
                    _dt_start: System.DateTime = self.__cConvert.ToDateTime(str_start).ToLocalTime()
                    _dt_end: System.DateTime = self.__cConvert.ToDateTime(str_end).ToLocalTime()
                else:
                    _dt_start: System.DateTime = self.__cConvert.ToDateTime(str_start)
                    _dt_end: System.DateTime = self.__cConvert.ToDateTime(str_end)
            else:
                _dt_start: System.DateTime = self.__cConvert.ToDateTime(str_start).AddHours(self.__local_time)
                _dt_end: System.DateTime = self.__cConvert.ToDateTime(str_end).AddHours(self.__local_time)
        except Exception as e:
            app_config.LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.fetch_value Error: {e}'
            )
            return _result
        _start_time_result: tuple = self.__ihuApi.IHU_TIMESTAMP_FromParts(_dt_start)
        _end_time_result: tuple = self.__ihuApi.IHU_TIMESTAMP_FromParts(_dt_end)
        _err_code_start: Proficy.Historian.userapi.ihuErrorCode = _start_time_result[0]
        _timestamp_start: Proficy.Historian.UserAPI.IHU_TIMESTAMP = _start_time_result[1]
        _err_code_end: Proficy.Historian.userapi.ihuErrorCode = _end_time_result[0]
        _timestamp_end: Proficy.Historian.UserAPI.IHU_TIMESTAMP = _end_time_result[1]

        _list_result: list[dict] = []
        for _tag in list_tag:
            _read_raw_result: tuple = self.__ihuApi.ihuReadRawDataByTime(
                self.__server, _tag, _timestamp_start, _timestamp_end
            )
            _p_err: Proficy.Historian.userapi.ihuErrorCode = _read_raw_result[0]
            _p_data: (
                    Proficy.Historian.userapi.IHU_DATA_SAMPLE or
                    list[Proficy.Historian.userapi.IHU_DATA_SAMPLE]
            ) = _read_raw_result[1]
            if _p_data is not None:
                for _value in _p_data:
                    _dict_result_: dict = {}
                    if _p_err != self.__ihuErrEnum.INVALID_TAGNAME:
                        _switch: dict = {
                            self.__ihuDataEnum.Short: str(_value.Value.Integer),
                            self.__ihuDataEnum.Integer: str(_value.Value.Integer),
                            self.__ihuDataEnum.Float: str(_value.Value.Float),
                            self.__ihuDataEnum.DoubleFloat: str(_value.Value.Float)
                        }
                        _str_value: str = _switch.get(_value.ValueDataType, str(_value.Value.Integer))
                        _timestamp_result: tuple = self.__ihuApi.IHU_TIMESTAMP_ToParts(_value.TimeStamp)
                        _timestamp_err_code: Proficy.Historian.userapi.ihuErrorCode = _timestamp_result[0]
                        _dt_time_before: str = _timestamp_result[1].ToString()
                        if self.__time_format == '%m/%d/%Y %I:%M:%S %p':
                            time_format = '%m/%d/%Y %I:%M:%S %p'
                        else:
                            time_format = '%Y-%m-%d %p %I:%M:%S'
                        _dt_time_before: str = _dt_time_before.replace('오전', 'AM').replace('오후', 'PM')
                        _dt: datetime = datetime.strptime(_dt_time_before, time_format)
                        _result_column: list = app_config.ConfigUtil().get_result_column()
                        for _column_name in _result_column:
                            if 'name' in _column_name.lower():
                                _dict_result_[_column_name]: str = _tag
                            elif 'time' in _column_name.lower():
                                _dict_result_[_column_name]: str = _dt.strftime(self.__time_format)
                            elif 'val' in _column_name.lower():
                                _dict_result_[_column_name]: str = _str_value
                            elif 'quality' in _column_name.lower() or 'conf' in _column_name.lower():
                                _dict_result_[_column_name]: int = \
                                    100 if _value.Quality.ToString() == self.__ihuQualityEnum.OPCGood.ToString() else 0
                    _list_result.append(_dict_result_)

        return _list_result

    def write_data(self, list_tag: list[dict] or str) -> list[dict]:
        _result: list[dict] = []
        if list_tag in self.__list_none_value:
            return _result
        elif type(list_tag) == str:
            list_tag = json.loads(list_tag)

        if self.is_connected:
            _result = asyncio.run(self.__write_data(list_data=list_tag))

        return _result

    async def __write_data(self, list_data: list[dict]) -> list[dict]:
        _list_result_err_code: list = []
        for _data in list_data:
            _tag_name: str = _data.get('name')
            _tag_values: list[dict] = _data.get('values')
            if _tag_name in self.__list_none_value:
                continue

            _list_data_sample: Proficy.Historian.userapi.IHU_DATA_SAMPLE = []
            _list_err_code: Proficy.Historian.userapi.ihuErrorCode = []
            for _tag_value in _tag_values:
                _time: str = _tag_value.get('time')
                _val: str = _tag_value.get('val')
                _type: str = _tag_value.get('type')
                _switch_type: dict = {
                    'short': self.__ihuDataEnum.Short,
                    'int': self.__ihuDataEnum.Integer,
                    'float': self.__ihuDataEnum.Float,
                    'doubleFloat': self.__ihuDataEnum.DoubleFloat
                }
                _switch_object: dict = {
                    'short': self.__cConvert.ToSingle,
                    'int': self.__cConvert.ToSingle,
                    'float': self.__cConvert.ToSingle,
                    'doubleFloat': self.__cConvert.ToDouble
                }
                if _time in self.__list_none_value or _val in self.__list_none_value:
                    continue
                try:
                    if type(self.__local_time) == bool:
                        if self.__local_time:
                            _dt_time: System.DateTime = self.__cConvert.ToDateTime(_time).ToLocalTime()
                        else:
                            _dt_time: System.DateTime = self.__cConvert.ToDateTime(_time)
                    else:
                        _dt_time: System.DateTime = self.__cConvert.ToDateTime(_time).AddHours(self.__local_time)
                except Exception as e:
                    app_config.LogUtil().error(
                        message=f'{self.__module__}.{self.__class__.__name__}.fetch_value Error: {e}'
                    )
                    return _list_result_err_code
                data_sample: Proficy.Historian.userapi.IHU_DATA_SAMPLE = self.__ihuDataSample()
                _time_result: tuple = self.__ihuApi.IHU_TIMESTAMP_FromParts(_dt_time)
                _time_err_code: Proficy.Historian.userapi.ihuErrorCode = _time_result[0]
                _timestamp: Proficy.Historian.UserAPI.IHU_TIMESTAMP = _time_result[1]
                data_sample.Tagname = _tag_name
                data_sample.TimeStamp = _timestamp
                data_sample.ValueDataType = _switch_type.get(_type, self.__ihuDataEnum.Integer)
                if re.fullmatch(r'^-?\d+(\.\d+)?$', _val):
                    _float_val = float(_val)
                else:
                    _float_val = _val
                data_sample.ValueObject = _switch_object.get(_type, self.__cConvert.ToSingle)(_float_val)
                #self.__cDouble.Parse(str(_float_val))
                _raw_quality: Proficy.Historian.userapi.IHU_RAW_QUALITY = self.__ihuRawQuality()
                _raw_quality.QualityStatus = self.__ihuQualityEnum.OPCGood
                data_sample.Quality = _raw_quality
                _list_data_sample.append(data_sample)

            _result_err_code = self.__ihuApi.ihuWriteData(
                self.__server, _list_data_sample, _list_err_code, False, False
            )
            _dict_result: dict = {
                'name': _tag_name,
                'value': _result_err_code.ToString()
            }
            _list_result_err_code.append(_dict_result)

        return _list_result_err_code
