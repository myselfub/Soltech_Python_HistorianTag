import re
from datetime import datetime

from PyQt6.QtCore import QRegularExpression, QStringListModel, Qt
from PyQt6.QtGui import QRegularExpressionValidator, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QTabWidget, QWidget, QPushButton, QLabel, \
    QLineEdit, QFormLayout, QHBoxLayout, QTableView, QVBoxLayout, QListView, QProgressBar

from app_config import ConfigUtil, LogUtil


class Tab2UI:
    __historian_main_ui = None
    __tab_widget: QTabWidget = None
    __left_max_width: int = 320
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
        _tab_name: str = 'Tag Search'
        _back_widget: QWidget = QWidget()

        _hbox_layout: QHBoxLayout = QHBoxLayout()
        self._create_left_area(hbox_layout=_hbox_layout)
        self._create_right_area(hbox_layout=_hbox_layout)

        _back_widget.setLayout(_hbox_layout)
        self.__tab_widget.addTab(_back_widget, _tab_name)

    def _create_left_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 좌측 영역 생성
        :param hbox_layout: (QHBoxLayout) 배경레이아웃
        :return None
        """
        _left_vbox_layout: QVBoxLayout = QVBoxLayout()
        self._create_left_form(vbox_layout=_left_vbox_layout)
        # self._create_left_progress_bar(vbox_layout=_left_vbox_layout)
        self._create_left_list(vbox_layout=_left_vbox_layout)

        hbox_layout.addLayout(_left_vbox_layout)

    def _create_left_form(self, vbox_layout: QVBoxLayout) -> None:
        """ 좌측 폼 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 배경 설정 """
        _left_form_widget: QWidget = QWidget()
        _left_form_widget.setMaximumWidth(self.__left_max_width)
        _left_form_layout: QFormLayout = QFormLayout()
        _left_form_layout.setSpacing(15)

        """ 태그 입력창 설정 """
        _tag_edit: QLineEdit = QLineEdit()
        _tag_edit.setFont(ConfigUtil().get_default_font())
        _tag_edit.setPlaceholderText('Historian Tag')
        _tag_edit.returnPressed.connect(self.search_event)
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
        _end_date_edit.returnPressed.connect(lambda: self.dict_ui.get('_search_button').setFocus())
        self.dict_ui['_end_date_edit'] = _end_date_edit
        _end_date_label: QLabel = QLabel('End Date :')
        _end_date_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_end_date_label, _end_date_edit)

        self.set_placeholder('yyyy-mm-dd hh24:mm:ss')

        """ 검색 버튼 설정 """
        _search_hbox_layout: QHBoxLayout = QHBoxLayout()
        _search_button: QPushButton = QPushButton('Search')
        _search_button.setFont(ConfigUtil().get_default_font())
        _search_button.setMaximumWidth(75)
        _search_button.clicked.connect(self.search_event)
        self.dict_ui['_search_button'] = _search_button
        _search_hbox_layout.addStretch()
        _search_hbox_layout.addWidget(_search_button)
        _left_form_layout.addRow(None, _search_hbox_layout)

        """ 레이아웃 추가 """
        _left_form_widget.setLayout(_left_form_layout)
        vbox_layout.addWidget(_left_form_widget)

    def _create_left_progress_bar(self, vbox_layout: QVBoxLayout) -> None:
        """ 좌측 프로그레스바 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 프로그레스바 설정 """
        _hbox_layout = QHBoxLayout()
        _left_progress_bar = QProgressBar()
        self.dict_ui['_left_progress_bar'] = _left_progress_bar
        _left_progress_bar.setRange(0, 0)
        _left_progress_bar.setMaximumWidth(250)
        _left_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _left_progress_bar.setVisible(False)
        _hbox_layout.addWidget(_left_progress_bar)
        vbox_layout.addLayout(_hbox_layout)

    def _create_left_list(self, vbox_layout: QVBoxLayout) -> None:
        """ 좌측 리스트 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 리스트뷰 설정 """
        _left_list_view: QListView = QListView()
        _left_list_view.setFont(ConfigUtil().get_default_font(11))
        _left_list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        _left_list_view.setMaximumWidth(self.__left_max_width)

        """ 리스트뷰 데이터 설정 """
        _list_model: QStringListModel = QStringListModel()
        self.dict_ui['_list_model'] = _list_model
        _left_list_view.setModel(_list_model)

        vbox_layout.addWidget(_left_list_view)

    def _create_right_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 우측 영역 생성
        :param hbox_layout: (QHBoxLayout) 배경레이아웃
        :return None
        """
        """ 테이블뷰 설정 """
        _table_view: QTableView = QTableView()
        _table_view.setFont(ConfigUtil().get_default_font(10))
        _table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        """ 테이블뷰 데이터 설정 """
        _table_model: QStandardItemModel = QStandardItemModel()
        self.dict_ui['_table_model'] = _table_model
        _table_model.setHorizontalHeaderLabels(ConfigUtil().get_result_column())
        _model_data = []

        for _row in _model_data:
            _items: list = [QStandardItem(str(_item)) for _item in _row]
            _table_model.appendRow(_items)
        _table_view.setModel(_table_model)

        """ 테이블뷰 컬럼 크기 설정 """
        _table_view.setColumnWidth(0, 130)
        _table_view.setColumnWidth(1, 140)
        _table_view.setColumnWidth(2, 150)
        _table_view.setColumnWidth(3, 60)

        hbox_layout.addWidget(_table_view)

    def set_placeholder(self, text: str = 'yyyy-mm-dd hh24:mm:ss') -> None:
        self.dict_ui.get('_start_date_edit').setPlaceholderText(text)
        self.dict_ui.get('_end_date_edit').setPlaceholderText(text)

    def search_event(self) -> None:
        """ 검색버튼 클릭 이벤트
        :return None
        """
        try:
            _table_model: QStandardItemModel = self.dict_ui.get('_table_model')
            while _table_model.rowCount() > 0:
                _table_model.removeRow(0)
            if self.__historian_main_ui.historian is not None and self.__historian_main_ui.historian.is_connected:
                _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
                _str_end_date: str = self.dict_ui.get('_end_date_edit').text()
                if _str_start_date in self.__historian_main_ui.none_values:
                    self._search_event_req_values()
                else:
                    time_format = self.__historian_main_ui.dict_ui.get('time_format')
                    if time_format == '%m/%d/%Y %I:%M:%S %p':
                        _reg = r'^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20|21|22|23|24|25|26|27|28|29)\d\d ([01][0-9]|12):([0-5][0-9]):([0-5][0-9]) (AM|PM)$'
                    else:
                        _reg = r'^(19|20|21|22|23|24|25|26|27|28|29)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
                    if (not re.fullmatch(_reg, _str_start_date) or (
                            _str_end_date not in self.__historian_main_ui.none_values
                            and not re.fullmatch(_reg, _str_end_date))
                    ):
                        self.__historian_main_ui.common_message('date_format_error')
                    else:
                        self._search_event_fetch_values()
            else:
                self.__historian_main_ui.common_message('not_connect')
        except Exception as e:
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.search_event Error: {e}'
            )

    def _search_event_req_values(self) -> None:
        """ 검색버튼 클릭 이벤트(최근값 조회)
        :return None
        """
        _str_tag: str = self.dict_ui.get('_tag_edit').text()

        self.dict_ui.get('_list_model').setStringList([])
        _model_data: list = [_str_tag]

        _list_result: list = self.__historian_main_ui.historian.req_values(list_tag=_model_data)
        _list_search_result = []
        if _list_result:
            self.dict_ui.get('_list_model').setStringList(_model_data)
            for _result in _list_result:
                _list_search_result_row = []
                for _column_name in ConfigUtil().get_result_column():
                    _data: str = _result.get(_column_name)
                    if _data is None:
                        _data = ''
                    if 'quality' in _column_name.lower() or 'conf' in _column_name.lower():
                        _data = 'Good' if _data == 100 else 'Bad'
                    _list_search_result_row.append(_data)
                _list_search_result.append(_list_search_result_row)
            for _row in _list_search_result:
                _items: list = [QStandardItem(str(_item)) for _item in _row]
                self.dict_ui.get('_table_model').appendRow(_items)

    def _search_event_fetch_values(self) -> None:
        """ 검색버튼 클릭 이벤트(기간 조회)
        :return None
        """
        _str_tag: str = self.dict_ui.get('_tag_edit').text()
        _str_start_date: str = self.dict_ui.get('_start_date_edit').text()
        _str_end_date: str = self.dict_ui.get('_end_date_edit').text()
        if _str_end_date in self.__historian_main_ui.none_values:
            time_format = self.__historian_main_ui.dict_ui.get('time_format')
            _str_end_date = datetime.now().strftime(time_format)

        self.dict_ui.get('_list_model').setStringList([])
        _model_data: list = [_str_tag]

        _params = {
            'tagList': _model_data,
            'start': _str_start_date,
            'end': _str_end_date
        }
        _list_req_result: list = self.__historian_main_ui.historian.req_values(list_tag=_model_data)
        if _list_req_result:
            self.dict_ui.get('_list_model').setStringList(_model_data)
            _list_result: list = self.__historian_main_ui.historian.fetch_values(dict_tag=_params)
            _list_search_result = []
            for _result in _list_result:
                _list_search_result_row = []
                for _column_name in ConfigUtil().get_result_column():
                    _data: str = _result.get(_column_name)
                    if _data in self.__historian_main_ui.none_values:
                        _data = ''
                    if 'quality' in _column_name.lower() or 'conf' in _column_name.lower():
                        _data = 'Good' if _data == 100 else 'Bad'
                    _list_search_result_row.append(_data)
                _list_search_result.append(_list_search_result_row)
            for _row in _list_search_result:
                _items: list = [QStandardItem(str(_item)) for _item in _row]
                self.dict_ui.get('_table_model').appendRow(_items)
