import traceback

import pandas
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QTabWidget, QWidget, QPushButton, QLabel, \
    QLineEdit, QFormLayout, QHBoxLayout, QVBoxLayout, QTableView, QFileDialog

from app_config import ConfigUtil, LogUtil


class Tab4UI:
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
        _tab_name: str = 'Tag Import'
        _back_widget: QWidget = QWidget()
        self.dict_ui['_back_widget'] = _back_widget
        self.dict_ui['_table_column'] = ConfigUtil().get_csv_field()

        _hbox_layout: QHBoxLayout = QHBoxLayout()
        self._create_left_area(hbox_layout=_hbox_layout)
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

        """ 경로 입력창 설정 """
        _path_edit: QLineEdit = QLineEdit()
        _path_edit.setFont(ConfigUtil().get_default_font())
        _path_edit.setPlaceholderText('CSV File Path')
        _path_edit.returnPressed.connect(self.import_event)
        self.dict_ui['_path_edit'] = _path_edit
        _path_label: QLabel = QLabel('Path :')
        _path_label.setFont(ConfigUtil().get_default_font())
        _left_form_layout.addRow(_path_label, _path_edit)

        """ 가져오기 버튼 배경 """
        _import_hbox_layout: QHBoxLayout = QHBoxLayout()
        _import_hbox_layout.addStretch()

        """ 파일 선택버튼 설정 """
        _browse_button: QPushButton = QPushButton('Browse...')
        _browse_button.setFont(ConfigUtil().get_default_font())
        _browse_button.setMaximumWidth(80)
        _browse_button.clicked.connect(self.browse_event)
        self.dict_ui['_browse_button'] = _browse_button

        """ 가져오기 버튼 설정 """
        _import_button: QPushButton = QPushButton('Import')
        _import_button.setFont(ConfigUtil().get_default_font())
        _import_button.setMaximumWidth(80)
        _import_button.clicked.connect(self.import_event)
        self.dict_ui['_import_button'] = _import_button

        _import_hbox_layout.addWidget(_browse_button)
        _import_hbox_layout.addWidget(_import_button)
        _left_form_layout.addRow(None, _import_hbox_layout)

        """ 쓰기 버튼 배경 """
        _write_hbox_layout: QHBoxLayout = QHBoxLayout()
        _write_hbox_layout.addStretch()

        """ 쓰기 버튼 설정 """
        _write_button: QPushButton = QPushButton('Write')
        _write_button.setFont(ConfigUtil().get_default_font())
        _write_button.setMaximumWidth(80)
        _write_button.clicked.connect(self.write_event)
        self.dict_ui['_write_button'] = _write_button
        _write_hbox_layout.addWidget(_write_button)
        _left_form_layout.addRow(None, _write_hbox_layout)

        """ 레이아웃 추가 """
        _left_form_widget.setLayout(_left_form_layout)
        _vbox_layout.addWidget(_left_form_widget)
        hbox_layout.addLayout(_vbox_layout)

    def _create_right_area(self, hbox_layout: QHBoxLayout) -> None:
        """ 우측 영역 레이아웃 생성
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
        _table_model.setHorizontalHeaderLabels(self.dict_ui.get('_table_column'))
        _model_data: list = []

        for _row in _model_data:
            _items: list = [QStandardItem(str(_item)) for _item in _row]
            _table_model.appendRow(_items)
        _table_view.setModel(_table_model)

        """ 테이블뷰 컬럼 크기 설정 """
        _table_view.setColumnWidth(0, 170)
        _table_view.setColumnWidth(1, 160)
        _table_view.setColumnWidth(2, 150)

        """ 레이아웃 추가 """
        hbox_layout.addWidget(_table_view)

    def browse_event(self) -> None:
        """ 찾아보기버튼 이벤트
        :return None
        """
        _file_name, _ = QFileDialog.getOpenFileName(
            self.dict_ui.get('_back_widget'), 'Open CSV File', '', 'CSV Files (*.csv);;All Files (*)'
        )

        if _file_name:
            self.dict_ui.get('_path_edit').setText(_file_name)
            self.import_event()

    def import_event(self) -> None:
        """ 테이블에 가져오기 이벤트
        :return None
        """
        _file_name: str = self.dict_ui.get('_path_edit').text()
        if not _file_name:
            return
        try:
            _data_frame: pandas.core.frame.DataFrame = pandas.read_csv(_file_name)
            _table_model: QStandardItemModel = self.dict_ui.get('_table_model')
            while _table_model.rowCount() > 0:
                _table_model.removeRow(0)

            _column_list: list = [_column.lower() for _column in self.dict_ui.get('_table_column')]
            _field_list: list = []
            """ 전체 빈값 유효성 검사 """
            """
            if _data_frame.isnull().values.any():
                self.__historian_main_ui.common_message('file_check')
                return
            """
            for _field in _data_frame.columns:
                _lower_field: str = _field.lower()
                """ 필드명 유효성 검사 """
                if _lower_field not in _column_list:
                    self.__historian_main_ui.common_message('field_check')
                    return
                if _lower_field.startswith('tag') or _lower_field.startswith('name'):
                    if not pandas.api.types.is_object_dtype(_data_frame.get(_field)):
                        """ 데이터 타입 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                    elif _data_frame.get(_field).isnull().values.any():
                        """ 데이터 널체크 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                elif _lower_field.startswith('time') or _lower_field.startswith('date'):
                    if not pandas.api.types.is_object_dtype(_data_frame.get(_field)):
                        """ 데이터 타입 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                    elif _data_frame.get(_field).isnull().values.any():
                        """ 데이터 널체크 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                elif _lower_field.startswith('val'):
                    if not pandas.api.types.is_numeric_dtype(_data_frame.get(_field)):
                        """ 데이터 타입 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                    elif _data_frame.get(_field).isnull().values.any():
                        """ 데이터 널체크 검사 """
                        self.__historian_main_ui.common_message('file_check')
                        return
                _field_list.append(_lower_field)

            for _row in range(_data_frame.shape[0]):
                # _items: list = [QStandardItem(str(_data_frame.iat[_row, _column])) for _column in range(_data_frame.shape[1])]
                _dict_item: dict = {}
                for _field in range(_data_frame.shape[1]):
                    _dict_item[_field_list[_field]] = QStandardItem(str(_data_frame.iat[_row, _field]))
                _table_model.appendRow([
                    _dict_item.get(_column_list[0]),
                    _dict_item.get(_column_list[1]),
                    _dict_item.get(_column_list[2])
                ])
        except (pandas.errors.EmptyDataError, pandas.errors.ParserError, Exception) as ede:
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.display_event Error: {ede}'
            )
            self.__historian_main_ui.common_message('file_check')

    def write_event(self) -> None:
        """ 쓰기버튼 클릭 이벤트
        :return None
        """
        try:
            if self.__historian_main_ui.historian is not None and self.__historian_main_ui.historian.is_connected:
                _table_model: QStandardItemModel = self.dict_ui.get('_table_model')
                while _table_model.rowCount() < 1:
                    self.__historian_main_ui.common_message('empty_csv_data')
                    return
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
        _column_list: list = [_column.lower() for _column in self.dict_ui.get('_table_column')]
        _table_model: QStandardItemModel = self.dict_ui.get('_table_model')
        _dict_table_datas: dict = {}
        for _row in range(_table_model.rowCount()):
            _dict_row_data: dict = {}
            _temp_tag: str = ''
            for _column, _column_name in enumerate(_column_list):
                if _column_name.startswith('tag') or _column_name.startswith('name'):
                    _temp_tag = _table_model.item(_row, _column).text()
                    if not _dict_table_datas.get(_temp_tag):
                        _dict_table_datas[_temp_tag] = []
                elif _column_name.startswith('time') or _column_name.startswith('date'):
                    _dict_row_data['time'] = _table_model.item(_row, _column).text()
                elif _column_name.startswith('val'):
                    _dict_row_data['val'] = _table_model.item(_row, _column).text()
            _dict_row_data['type'] = 'float'
            _dict_table_datas.get(_temp_tag, []).append(_dict_row_data)

        _list_param: list = []
        for _key in _dict_table_datas.keys():
            _dict_param: dict = {
                'name': _key,
                'values': _dict_table_datas.get(_key)
            }
            _list_param.append(_dict_param)

        _list_result: list = self.__historian_main_ui.historian.write_data(list_tag=_list_param)
        _is_success: bool = False
        for _result in _list_result:
            _name = _result.get('name')
            _value = _result.get('value', 'FAILED')
            if _name is not None and _value == 'OK':
                _is_success = _is_success or True

        if _is_success:
            self.__historian_main_ui.common_message('write_success')
        else:
            self.__historian_main_ui.common_message('write_fail')
