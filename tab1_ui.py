from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import QTabWidget, QWidget, QPushButton, QLabel, \
    QLineEdit, QVBoxLayout, QFormLayout, QHBoxLayout, QRadioButton

from app_config import ConfigUtil, LogUtil
from communication import Historian


class Tab1UI:
    __historian_main_ui = None
    __tab_widget: QTabWidget = None
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
        _tab_name: str = 'Connection'
        _back_widget: QWidget = QWidget()

        _vbox_layout: QVBoxLayout = QVBoxLayout()
        self._create_title(vbox_layout=_vbox_layout)
        self._create_form(vbox_layout=_vbox_layout)
        self._create_button(vbox_layout=_vbox_layout)

        _back_widget.setLayout(_vbox_layout)
        self.__tab_widget.addTab(_back_widget, _tab_name)

    def _create_title(self, vbox_layout: QVBoxLayout) -> None:
        """ 타이틀 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 타이틀 라벨 설정 """
        _title_label: QLabel = QLabel('Setting Connect Historian')
        _title_label.setFont(ConfigUtil().get_default_font(14))
        _title_label.setMaximumHeight(40)
        _title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        """ 레이아웃 추가 """
        vbox_layout.addWidget(_title_label)

    def _create_form(self, vbox_layout: QVBoxLayout) -> None:
        """ 접속정보 폼 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 폼 배경 레이아웃 설정 """
        _form_hbox_layout: QHBoxLayout = QHBoxLayout()
        _form_widget: QWidget = QWidget()
        _form_widget.setMaximumWidth(450)
        _form_layout: QFormLayout = QFormLayout()
        _form_layout.setSpacing(15)

        """ 아이피 입력창 설정 """
        _ip_edit: QLineEdit = QLineEdit()
        _ip_edit.setFont(ConfigUtil().get_default_font())
        _ip_edit.setPlaceholderText('IP')
        _ip_regex: QRegularExpression = QRegularExpression(
            r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        )
        _ip_validator: QRegularExpressionValidator = QRegularExpressionValidator(_ip_regex)
        _ip_edit.setValidator(_ip_validator)
        self.dict_ui['_ip_edit'] = _ip_edit
        _ip_label: QLabel = QLabel('Historian IP :')
        _ip_label.setFont(ConfigUtil().get_default_font())
        _form_layout.addRow(_ip_label, _ip_edit)

        """ 유저 입력창 설정 """
        _user_edit: QLineEdit = QLineEdit()
        _user_edit.setFont(ConfigUtil().get_default_font())
        _user_edit.setPlaceholderText('USER')
        self.dict_ui['_user_edit'] = _user_edit
        _user_label: QLabel = QLabel('Historian USER :')
        _user_label.setFont(ConfigUtil().get_default_font())
        _form_layout.addRow(_user_label, _user_edit)

        """ 비밀번호 입력창 설정 """
        _password_edit: QLineEdit = QLineEdit()
        _password_edit.setFont(ConfigUtil().get_default_font())
        _password_edit.setPlaceholderText('Password')
        self.dict_ui['_password_edit'] = _password_edit
        _password_label: QLabel = QLabel('Historian Password :')
        _password_label.setFont(ConfigUtil().get_default_font())
        _form_layout.addRow(_password_label, _password_edit)

        """ 로컬타임 입력창 설정 """
        _local_time_edit: QLineEdit = QLineEdit()
        _local_time_edit.setFont(ConfigUtil().get_default_font())
        _local_time_edit.setPlaceholderText('LocalTime')
        _local_time_edit.setText('-9')
        _local_time_validator: QIntValidator = QIntValidator(-24, 24)
        _local_time_edit.setValidator(_local_time_validator)
        self.dict_ui['_local_time_edit'] = _local_time_edit
        _local_time_label: QLabel = QLabel('Historian LocalTime :')
        _local_time_label.setFont(ConfigUtil().get_default_font())
        _form_layout.addRow(_local_time_label, _local_time_edit)

        """ 타임포맷 입력창 설정 """
        _time_format_vbox_layout: QVBoxLayout = QVBoxLayout()
        _time_format_radio_1 = QRadioButton('%Y-%m-%d %H:%M:%S')
        _time_format_radio_1.setFont(ConfigUtil().get_default_font(10))
        _time_format_radio_1.setChecked(True)
        self.dict_ui['_time_format_radio_1'] = _time_format_radio_1
        _time_format_vbox_layout.addWidget(_time_format_radio_1)
        _time_format_radio_2 = QRadioButton('%m/%d/%Y %I:%M:%S %p')
        _time_format_radio_2.setFont(ConfigUtil().get_default_font(10))
        self.dict_ui['_time_format_radio_2'] = _time_format_radio_2
        _time_format_vbox_layout.addWidget(_time_format_radio_2)
        _local_time_label: QLabel = QLabel('Historian TimeFormat :')
        _local_time_label.setFont(ConfigUtil().get_default_font())
        _form_layout.addRow(_local_time_label, _time_format_vbox_layout)

        """ 레이아웃 추가 """
        _form_widget.setLayout(_form_layout)
        _form_hbox_layout.addWidget(_form_widget)
        vbox_layout.addLayout(_form_hbox_layout)
        # TODO: 삭제
        self.test()

    def _create_button(self, vbox_layout: QVBoxLayout) -> None:
        """ 연결/해제 버튼 생성
        :param vbox_layout: (QVBoxLayout) 배경레이아웃
        :return None
        """
        """ 버튼 배경 레이아웃 설정 """
        _button_hbox_layout: QHBoxLayout = QHBoxLayout()
        _button_hbox_layout.addStretch()
        _button_hbox_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        """ 연결 버튼 설정 """
        _connect_button: QPushButton = QPushButton('Connect')
        _connect_button.setFont(ConfigUtil().get_default_font())
        self.dict_ui['_connect_button'] = _connect_button
        _connect_button.clicked.connect(self._connect_event)
        _button_hbox_layout.addWidget(_connect_button)

        """ 연결 해제 버튼 설정 """
        _disconnect_button: QPushButton = QPushButton('Disconnect')
        _disconnect_button.setFont(ConfigUtil().get_default_font())
        self.dict_ui['_disconnect_button'] = _disconnect_button
        _disconnect_button.clicked.connect(self._disconnect_event)

        self._change_button()
        """ 레이아웃 추가 """
        _button_hbox_layout.addWidget(_disconnect_button)
        vbox_layout.addLayout(_button_hbox_layout)

    def _change_button(self) -> None:
        """ 연결/해제 버튼 활성화 변경
        :return None
        """
        if self.__historian_main_ui.is_connect:
            _connect_button: QPushButton = self.dict_ui.get('_connect_button')
            _disconnect_button: QPushButton = self.dict_ui.get('_disconnect_button')
            self._set_disabled(True)
            if _connect_button is not None:
                _connect_button.setDisabled(True)
            if _disconnect_button is not None:
                _disconnect_button.setDisabled(False)
        else:
            _connect_button: QPushButton = self.dict_ui.get('_connect_button')
            _disconnect_button: QPushButton = self.dict_ui.get('_disconnect_button')
            self._set_disabled(False)
            if _connect_button is not None:
                _connect_button.setDisabled(False)
            if _disconnect_button is not None:
                _disconnect_button.setDisabled(True)

    def _connect_event(self) -> None:
        """ 연결 버튼 클릭 이벤트
        :return None
        """
        try:
            _str_ip: str = self.dict_ui.get('_ip_edit').text()
            _str_user: str = self.dict_ui.get('_user_edit').text()
            _str_password: str = self.dict_ui.get('_password_edit').text()
            _str_local_time: str = self.dict_ui.get('_local_time_edit').text()
            if self.dict_ui.get('_time_format_radio_2').isChecked():
                self.__historian_main_ui.dict_ui['time_format'] = '%m/%d/%Y %I:%M:%S %p'
                self.__historian_main_ui.dict_ui['_tab2_ui'].set_placeholder('MM/dd/yyyy hh:mm:ss a')
                self.__historian_main_ui.dict_ui['_tab3_ui'].set_placeholder('MM/dd/yyyy hh:mm:ss a')
            else:
                self.__historian_main_ui.dict_ui['time_format'] = '%Y-%m-%d %H:%M:%S'
                self.__historian_main_ui.dict_ui['_tab2_ui'].set_placeholder('yyyy-MM-dd HH:mm:ss')
                self.__historian_main_ui.dict_ui['_tab3_ui'].set_placeholder('yyyy-MM-dd HH:mm:ss')
            _str_time_format = self.__historian_main_ui.dict_ui['time_format']
            self.__historian_main_ui.historian = Historian(
                ip=_str_ip, user=_str_user, password=_str_password, local_time=_str_local_time, time_format=_str_time_format
            )
            self.__historian_main_ui.is_connect = self.__historian_main_ui.historian.connect()
            if self.__historian_main_ui.is_connect:
                self.__historian_main_ui.common_message('connect_success')
            else:
                self.__historian_main_ui.common_message('connect_fail')
            self._change_button()
        except Exception as e:
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.disconnect_event Error: {e}'
            )

    def _disconnect_event(self) -> None:
        """ 해제 버튼 클릭 이벤트
        :return None
        """
        try:
            self.__historian_main_ui.historian.disposed()
            self.__historian_main_ui.historian = None
            self.__historian_main_ui.is_connect = False
            self._change_button()
            self.__historian_main_ui.common_message('disconnect')
        except Exception as e:
            LogUtil().error(
                message=f'{self.__module__}.{self.__class__.__name__}.disconnect_event Error: {e}'
            )

    def _set_disabled(self, is_disabled: bool = True) -> None:
        self.dict_ui.get('_ip_edit').setDisabled(is_disabled)
        self.dict_ui.get('_user_edit').setDisabled(is_disabled)
        self.dict_ui.get('_password_edit').setDisabled(is_disabled)
        self.dict_ui.get('_local_time_edit').setDisabled(is_disabled)
        self.dict_ui.get('_time_format_radio_1').setDisabled(is_disabled)
        self.dict_ui.get('_time_format_radio_2').setDisabled(is_disabled)

    def test(self) -> None:
        _ip = '[HISTORIANIP]'
        _user = '[HISTORIANUSER]'
        _pw = '[HISTORIANPASSWORD]'
        self.dict_ui.get('_ip_edit').setText(_ip)
        self.dict_ui.get('_user_edit').setText(_user)
        self.dict_ui.get('_password_edit').setText(_pw)
