import random
import re
import traceback
from datetime import datetime, timedelta

from PyQt6.QtCore import QRegularExpression, QStringListModel
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QTabWidget, QWidget, QPushButton, QLabel, \
    QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, QListView, QRadioButton

from app_config import ConfigUtil, LogUtil


class Tab3UI:
    __historian_main_ui = None
    __tab_widget: QTabWidget = None
    __left_max_width: int = 320
    __max_tag_count: int = 30
    __max_value_count: int = 100
    dict_ui: dict = {}

    def __init__(self, historian_main_ui, tab_widget: QTabWidget) -> None:
        from main import HistorianMainUI
        super().__init__()
        self.__historian_main_ui: HistorianMainUI = historian_main_ui
        self.__tab_widget = tab_widget
        self.__create_tab()

    def __create_tab(self) -> None:
        """ 탭 생성
        :return None
        """
        _tab_name: str = 'Tag Write'
        _back_widget: QWidget = QWidget()

        _hbox_layout: QHBoxLayout = QHBoxLayout()
        self._create_left_area(hbox_layout=_hbox_layout)
        self._create_mid_area(hbox_layout=_hbox_layout)
        self._create_right_area(hbox_layout=_hbox_layout)

        _back_widget.setLayout(_hbox_layout)
        self.__tab_widget.addTab(_back_widget, _tab_name)

    def _create_left_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 좌측 영역 레이아웃 생성
        :param hbox_layout: (QHBoxLayout) 배경레이아웃
        :return None
        """
        _vbox_layout: QVBoxLayout = QVBoxLayout()

        """ 배경 설정 """
        _left_form_widget: QWidget = QWidget()
        _left_form_widget.setMaximumWidth(self.__left_max_width)
        _left_form_layout: QFormLayout = QFormLayout()
        _left_form_layout.setSpacing(15)

        """ 태그 입력창 설정 """
        _tag_edit: QLineEdit = QLineEdit()
        _tag_edit.setFont(ConfigUtil().get_default_font())
        _tag_edit.setPlaceholderText('Historian Tag')
        _tag_edit.returnPressed.connect(self.add_tag_event)
        self.dict_ui['_tag_edit'] = _tag_edit
        _tag_label: QLabel = QLabel('TAG :')
        _tag_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_tag_label, _tag_edit)

        """ 날짜 유효성 검사 """
        _datetime_regex: QRegularExpression = QRegularExpression(r'^\s*[0-9-/]+\s*[0-9:]+\s*(AM|PM)?$')
        _datetime_validator: QRegularExpressionValidator = QRegularExpressionValidator(_datetime_regex)

        """ 시작날짜 입력창 설정 """
        _start_date_edit: QLineEdit = QLineEdit()
        _start_date_edit.setFont(ConfigUtil().get_default_font())
        _start_date_edit.setValidator(_datetime_validator)
        _start_date_edit.setMaxLength(22)
        _start_date_edit.returnPressed.connect(lambda: self.dict_ui.get('_end_date_edit').setFocus())
        self.dict_ui['_start_date_edit'] = _start_date_edit
        _start_date_label: QLabel = QLabel('Start Date :')
        _start_date_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_start_date_label, _start_date_edit)

        """ 종료날짜 입력창 설정 """
        _end_date_edit: QLineEdit = QLineEdit()
        _end_date_edit.setFont(ConfigUtil().get_default_font())
        _end_date_edit.setValidator(_datetime_validator)
        _end_date_edit.setMaxLength(22)
        _end_date_edit.returnPressed.connect(lambda: self.dict_ui.get('_value_edit').setFocus())
        self.dict_ui['_end_date_edit'] = _end_date_edit
        _end_date_label: QLabel = QLabel('End Date :')
        _end_date_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_end_date_label, _end_date_edit)

        self.set_placeholder('yyyy-mm-dd hh24:mm:ss')

        """ 값 입력창 설정 """
        _value_edit: QLineEdit = QLineEdit()
        _value_edit.setFont(ConfigUtil().get_default_font())
        _value_edit.setPlaceholderText('0.0')
        _value_regex: QRegularExpression = QRegularExpression(r'^-?\d+(\.\d+)?$')
        _value_validator: QRegularExpressionValidator = QRegularExpressionValidator(_value_regex)
        _value_edit.setValidator(_value_validator)
        _value_edit.returnPressed.connect(self.add_value_event)
        self.dict_ui['_value_edit'] = _value_edit
        _value_label: QLabel = QLabel('Value :')
        _value_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_value_label, _value_edit)

        """ 주기 라디오버튼 설정 """
        _period_hbox_layout: QHBoxLayout = QHBoxLayout()
        _period_sec_radio = QRadioButton('Sec')
        _period_sec_radio.setFont(ConfigUtil().get_default_font(10))
        _period_sec_radio.setChecked(True)
        self.dict_ui['_period_value'] = 's'
        _period_sec_radio.toggled.connect(self.period_radio_event)
        self.dict_ui['_period_sec_radio'] = _period_sec_radio
        _period_hbox_layout.addWidget(_period_sec_radio)

        _period_min_radio = QRadioButton('Min')
        _period_min_radio.setFont(ConfigUtil().get_default_font(10))
        _period_min_radio.toggled.connect(self.period_radio_event)
        self.dict_ui['_period_min_radio'] = _period_min_radio
        _period_hbox_layout.addWidget(_period_min_radio)

        _period_hour_radio = QRadioButton('Hour')
        _period_hour_radio.setFont(ConfigUtil().get_default_font(10))
        _period_hour_radio.toggled.connect(self.period_radio_event)
        self.dict_ui['_period_hour_radio'] = _period_hour_radio
        _period_hbox_layout.addWidget(_period_hour_radio)

        _period_label: QLabel = QLabel('Period :')
        _period_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_period_label, _period_hbox_layout)

        """ 쓰기 버튼 설정 """
        _write_hbox_layout: QHBoxLayout = QHBoxLayout()
        _write_button: QPushButton = QPushButton('Write')
        _write_button.setFont(ConfigUtil().get_default_font())
        _write_button.setMaximumWidth(75)
        _write_button.clicked.connect(self.write_event)
        self.dict_ui['_write_button'] = _write_button

        """
        _random_write_button: QPushButton = QPushButton('Random Write')
        _random_write_button.setFont(ConfigUtil().get_default_font())
        _random_write_button.setMaximumWidth(140)
        _random_write_button.clicked.connect(self.random_write_event)
        self.dict_ui['_random_write_button'] = _random_write_button

        _write_hbox_layout.addWidget(_random_write_button)
        """
        _write_hbox_layout.addStretch()
        _write_hbox_layout.addWidget(_write_button)
        _left_form_layout.addRow(None, _write_hbox_layout)

        """ 레이아웃 추가 """
        _left_form_widget.setLayout(_left_form_layout)
        _vbox_layout.addWidget(_left_form_widget)
        hbox_layout.addLayout(_vbox_layout)

    def _create_mid_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 중간 영역 레이아웃 생성
        :param hbox_layout: (QHBoxLayout) 배경레이아웃
        :return None
        """
        """ 중간 배경 레이아웃 설정 """
        _vbox_layout: QVBoxLayout = QVBoxLayout()
        _hbox_layout: QHBoxLayout = QHBoxLayout()

        """ 태그 라벨 설정 """
        _tag_label: QLabel = QLabel('TAG')
        _tag_label.setFont(ConfigUtil().get_default_font())
        _hbox_layout.addWidget(_tag_label)

        """ 태그 추가 버튼 설정 """
        _tag_add_button: QPushButton = QPushButton('Add')
        _tag_add_button.setFont(ConfigUtil().get_default_font())
        _tag_add_button.setMaximumWidth(75)
        _tag_add_button.clicked.connect(self.add_tag_event)
        self.dict_ui['_tag_add_button'] = _tag_add_button
        _hbox_layout.addWidget(_tag_add_button)

        """ 태그 삭제 버튼 설정 """
        _delete_button: QPushButton = QPushButton('Delete')
        _delete_button.setFont(ConfigUtil().get_default_font())
        _delete_button.setMaximumWidth(75)
        _delete_button.clicked.connect(self.delete_tag_event)
        _hbox_layout.addWidget(_delete_button)

        """ 태그 라벨/버튼 레이아웃 추가 """
        _vbox_layout.addLayout(_hbox_layout)

        """ 태그 목록 설정 """
        _tag_list_view: QListView = QListView()
        _tag_list_view.setMaximumWidth(240)
        _tag_list_view.setFont(ConfigUtil().get_default_font(11))
        _tag_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        _tag_list_view.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.dict_ui['_tag_list_view'] = _tag_list_view

        """ 태그 목록 데이터 설정 """
        _tag_list_model: QStringListModel = QStringListModel()
        self.dict_ui['_tag_list_model'] = _tag_list_model
        _tag_list_view.setModel(_tag_list_model)

        """ 레이아웃 추가 """
        _vbox_layout.addWidget(_tag_list_view)
        hbox_layout.addLayout(_vbox_layout)

    def _create_right_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 우측 영역 레이아웃 생성
        :param hbox_layout: (QHBoxLayout) 배경레이아웃
        :return None
        """
        """ 오른쪽 배경 레이아웃 설정 """
        _vbox_layout: QVBoxLayout = QVBoxLayout()
        _hbox_layout: QHBoxLayout = QHBoxLayout()

        """ 값 라벨 설정 """
        _tag_label: QLabel = QLabel('Value')
        _tag_label.setFont(ConfigUtil().get_default_font())
        _hbox_layout.addWidget(_tag_label)

        """ 값 추가 버튼 설정 """
        _value_add_button: QPushButton = QPushButton('Add')
        _value_add_button.setFont(ConfigUtil().get_default_font())
        _value_add_button.setMaximumWidth(75)
        _value_add_button.clicked.connect(self.add_value_event)
        self.dict_ui['_value_add_button'] = _value_add_button
        _hbox_layout.addWidget(_value_add_button)

        """ 값 삭제 버튼 설정 """
        _delete_button: QPushButton = QPushButton('Delete')
        _delete_button.setFont(ConfigUtil().get_default_font())
        _delete_button.setMaximumWidth(75)
        _delete_button.clicked.connect(self.delete_value_event)
        _hbox_layout.addWidget(_delete_button)

        """ 값 라벨/버튼 레이아웃 추가 """
        _vbox_layout.addLayout(_hbox_layout)

        """ 값 목록 설정 """
        _value_list_view: QListView = QListView()
        _value_list_view.setMaximumWidth(240)
        _value_list_view.setFont(ConfigUtil().get_default_font(11))
        _value_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        _value_list_view.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.dict_ui['_value_list_view'] = _value_list_view

        """ 값 목록 데이터 설정 """
        _value_list_model: QStringListModel = QStringListModel()
        self.dict_ui['_value_list_model'] = _value_list_model
        _value_list_view.setModel(_value_list_model)

        """ 레이아웃 추가 """
        _vbox_layout.addWidget(_value_list_view)
        hbox_layout.addLayout(_vbox_layout)

    def set_placeholder(self, text: str = 'yyyy-mm-dd hh24:mm:ss') -> None:
        self.dict_ui.get('_start_date_edit').setPlaceholderText(text)
        self.dict_ui.get('_end_date_edit').setPlaceholderText(text)

    def write_event(self) -> None:
        """ 쓰기버튼 클릭 이벤트
        :return None
        """
        try:
            if self.__historian_main_ui.historian is not None and self.__historian_main_ui.historian.is_connected:
                _tag_list_model: QStringListModel = self.dict_ui.get('_tag_list_model')
                _tag_list_datas: list = _tag_list_model.stringList()
                _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
                _str_end_date: str = self.dict_ui.get('_end_date_edit').text()
                _value_list_model: QStringListModel = self.dict_ui.get('_value_list_model')
                _value_list_datas: list = _value_list_model.stringList()
                if len(_tag_list_datas) < 1:
                    self.__historian_main_ui.common_message('empty_tag')
                    return
                else:
                    time_format = self.__historian_main_ui.dict_ui.get('time_format')
                    if time_format == '%m/%d/%Y %I:%M:%S %p':
                        _reg = r'^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20|21|22|23|24|25|26|27|28|29)\d\d ([0-9]|0[0-9]|1[0-9]):([0-5][0-9]):([0-5][0-9]) (AM|PM)$'
                    else:
                        _reg = r'^(19|20|21|22|23|24|25|26|27|28|29)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
                    if _str_start_date in self.__historian_main_ui.none_values:
                        self.__historian_main_ui.common_message('empty_start_date')
                    elif (not re.fullmatch(_reg, _str_start_date) or (
                            _str_end_date not in self.__historian_main_ui.none_values
                            and not re.fullmatch(_reg, _str_end_date))
                    ):
                        self.__historian_main_ui.common_message('date_format_error')
                    else:
                        if len(_value_list_datas) < 1:
                            self.__historian_main_ui.common_message('empty_value')
                            return
                        else:
                            self._write_event()
            else:
                self.__historian_main_ui.common_message('not_connect')
        except Exception as e:
            traceback.print_exc()
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.write_event Error: {e}'
            )

    def _write_event(self) -> None:
        """ 쓰기버튼 클릭 이벤트 로직
        :return None
        """
        _tag_list_model: QStringListModel = self.dict_ui.get('_tag_list_model')
        _tag_list_datas: list = _tag_list_model.stringList()
        _value_list_model: QStringListModel = self.dict_ui.get('_value_list_model')
        _value_list_datas: list = _value_list_model.stringList()
        _period_value = self.dict_ui.get('_period_value')

        _params: list = []
        _str_time_format: str = self.__historian_main_ui.dict_ui.get('time_format')
        _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
        _str_end_date: str = self.dict_ui.get('_end_date_edit').text()
        if _str_end_date in self.__historian_main_ui.none_values:
            _str_end_date = _str_start_date
        for _tag_name in _tag_list_datas:
            _list_values: list = []

            if _period_value.lower().startswith('m'):
                _add_time: timedelta = timedelta(minutes=1)
                if not _str_start_date.endswith(':00'):
                    _str_start_date = _str_start_date[:-2] + '00'
                if not _str_end_date.endswith(':00'):
                    _str_end_date = _str_end_date[:-2] + '00'
            elif _period_value.lower().startswith('h'):
                _add_time: timedelta = timedelta(hours=1)
                if not _str_start_date.endswith(':00:00'):
                    _str_start_date = _str_start_date[:-5] + '00:00'
                if not _str_end_date.endswith(':00:00'):
                    _str_end_date = _str_end_date[:-5] + '00:00'
            else:
                _add_time: timedelta = timedelta(seconds=1)

            _dt_start: datetime = datetime.strptime(_str_start_date, _str_time_format)
            _dt_end: datetime = datetime.strptime(_str_end_date, _str_time_format)
            while _dt_start <= _dt_end:
                _str_value: str = random.choice(_value_list_datas)
                _dict_values: dict = {
                    'time': _dt_start.strftime(_str_time_format),
                    'val': _str_value,
                    'type': 'float'
                }
                _list_values.append(_dict_values)
                _dt_start += _add_time

            _param = {
                'name': _tag_name,
                'values': _list_values
            }
            _params.append(_param)
        """
            [
            {
                "name": "TEST01",
                "values": [
                    {
                        "time": "2024-09-11 16:14:00",
                        "val": "27.0",
                        "type": "float"
                    },
                    {
                        "time": "2024-09-11 16:14:10",
                        "val": "27.0",
                        "type": "float"
                    }
                ]
            },
            ]
        """
        _list_req_result: list = self.__historian_main_ui.historian.req_values(list_tag=_tag_list_datas)
        if _list_req_result:
            _list_result: list = self.__historian_main_ui.historian.write_data(list_tag=_params)
            _list_tags: list = []
            for _result in _list_result:
                _name = _result.get('name')
                _value = _result.get('value', 'FAILED')
                if _name is not None and _value == 'OK':
                    self.__historian_main_ui.common_message('write_success')

    r"""
    def random_write_event(self) -> None:
        try:
            if self.__historian_main_ui.historian is not None and self.__historian_main_ui.historian.is_connected:
                _str_tag: str = self.dict_ui.get('_tag_edit').text()
                _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
                _str_end_date: str = self.dict_ui.get('_end_date_edit').text()
                _str_value: str = self.dict_ui.get('_value_edit').text()
                if _str_tag in self.__historian_main_ui.none_values:
                    self.__historian_main_ui.common_message('empty_tag')
                else:
                    time_format = self.__historian_main_ui.dict_ui.get('time_format')
                    if time_format == '%m/%d/%Y %I:%M:%S %p':
                        _reg = r'^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20|21|22|23|24|25|26|27|28|29)\d\d ([0-9]|0[0-9]|1[0-9]):([0-5][0-9]):([0-5][0-9]) (AM|PM)$'
                    else:
                        _reg = r'^(19|20|21|22|23|24|25|26|27|28|29)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
                    if _str_start_date in self.__historian_main_ui.none_values:
                        self.__historian_main_ui.common_message('empty_start_date')
                    elif (not re.fullmatch(_reg, _str_start_date) or (
                            _str_end_date not in self.__historian_main_ui.none_values
                            and not re.fullmatch(_reg, _str_end_date))
                    ):
                        self.__historian_main_ui.common_message('date_format_error')
                    else:
                        self._random_write_event()
            else:
                self.__historian_main_ui.common_message('not_connect')
        except Exception as e:
            traceback.print_exc()
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.write_event Error: {e}'
            )

    def _random_write_event(self) -> None:
        _str_tag: str = self.dict_ui.get('_tag_edit').text()
        _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
        _str_end_date: str = self.dict_ui.get('_end_date_edit').text()

        self.dict_ui.get('_value_list_model').setStringList([])
        _model_data: list = [_str_tag]

        _list_values: list = []
        _str_time_format: str = self.__historian_main_ui.dict_ui.get('time_format')
        _add_second: timedelta = timedelta(seconds=1)
        if _str_end_date in self.__historian_main_ui.none_values:
            _str_end_date = _str_start_date

        _dt_start: datetime = datetime.strptime(_str_start_date, _str_time_format)
        _dt_end: datetime = datetime.strptime(_str_end_date, _str_time_format)
        while _dt_start <= _dt_end:
            # TODO: 랜덤값 목록
            _str_value: str = random.choice([None, '0.1', None, '0.5', None, '0.9', None])
            _dict_values: dict = {
                'time': _dt_start.strftime(_str_time_format),
                'val': _str_value,
                'type': 'float'
            }
            _list_values.append(_dict_values)
            _dt_start += _add_second

        _params: list = []
        for _tag_name in _model_data:
            _param = {
                'name': _tag_name,
                'values': _list_values
            }
            _params.append(_param)
        _list_req_result: list = self.__historian_main_ui.historian.req_values(list_tag=_model_data)
        if _list_req_result:
            self.dict_ui.get('_value_list_model').setStringList(_model_data)
            _list_result: list = self.__historian_main_ui.historian.write_data(list_tag=_params)
            _list_tags: list = []
            for _result in _list_result:
                _name = _result.get('name')
                _value = _result.get('value', 'FAILED')
                if _name is not None and _value == 'OK':
                    self.__historian_main_ui.common_message('write_success')
    """

    def period_radio_event(self) -> None:
        """ 주기 토글 이벤트
        :return None
        """
        if self.dict_ui.get('_period_min_radio').isChecked():
            self.dict_ui['_period_value'] = 'm'
        elif self.dict_ui.get('_period_hour_radio').isChecked():
            self.dict_ui['_period_value'] = 'h'
        else:
            self.dict_ui['_period_value'] = 's'

    def add_tag_event(self) -> None:
        """ 태그추가 버튼 클릭 이벤트
        :return None
        """
        _str_tag: str = self.dict_ui.get('_tag_edit').text()
        _tag_list_model: QStringListModel = self.dict_ui.get('_tag_list_model')
        _model_data: list = _tag_list_model.stringList()
        if self.__max_tag_count <= len(_model_data):
            """ 태그 추가 최대수 유효성검사 """
            self.__historian_main_ui.info_message(title='Information', text=f'TAG max count is {self.__max_tag_count}')
            return
        if _str_tag not in self.__historian_main_ui.none_values and _str_tag not in _model_data:
            _model_data.append(_str_tag)
            self.dict_ui.get('_tag_list_model').setStringList(_model_data)
        self.dict_ui.get('_tag_edit').setFocus()

    def delete_tag_event(self) -> None:
        """ 태그삭제 버튼 클릭 이벤트
        :return None
        """
        _tag_list_view: QListView = self.dict_ui.get('_tag_list_view')
        _tag_list_model: QStringListModel = self.dict_ui.get('_tag_list_model')
        _selected_list: list = [_tag_list_model.data(idx) for idx in _tag_list_view.selectedIndexes()]
        _deleted_tag_list = [_item for _item in _tag_list_model.stringList() if _item not in _selected_list]
        self.dict_ui.get('_tag_list_model').setStringList(_deleted_tag_list)

    def add_value_event(self) -> None:
        """ 값추가 버튼 클릭 이벤트
        :return None
        """
        _str_value: str = self.dict_ui.get('_value_edit').text()
        _value_list_model: QStringListModel = self.dict_ui.get('_value_list_model')
        _model_data: list = _value_list_model.stringList()
        if self.__max_value_count <= len(_model_data):
            """ 값 추가 최대수 유효성검사 """
            self.__historian_main_ui.info_message(
                title='Information', text=f'Value max count is {self.__max_value_count}'
            )
            return
        if _str_value in self.__historian_main_ui.none_values:
            _str_value = 'None'
        _model_data.append(_str_value)
        self.dict_ui.get('_value_list_model').setStringList(_model_data)
        self.dict_ui.get('_value_edit').setFocus()

    def delete_value_event(self) -> None:
        """ 값삭제 버튼 클릭 이벤트
        :return None
        """
        _value_list_view: QListView = self.dict_ui.get('_value_list_view')
        _value_list_model: QStringListModel = self.dict_ui.get('_value_list_model')
        _selected_rows: list = sorted(set(idx.row() for idx in _value_list_view.selectedIndexes()), reverse=True)
        for _row in _selected_rows:
            _value_list_model.removeRow(_row)
        _value_list_view.clearSelection()
