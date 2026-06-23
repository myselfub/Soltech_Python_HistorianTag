import sys

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget, QMenu

from app_config import ConfigUtil
from communication import Historian
from tab1_ui import Tab1UI
from tab2_ui import Tab2UI
from tab3_ui import Tab3UI
from tab4_ui import Tab4UI


class HistorianMainUI(QMainWindow):
    historian: Historian or None = None
    is_connect: bool = False
    none_values: list = ConfigUtil().get_none_values()
    dict_ui: dict = {}

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.__window_ui()
        self.__tab_ui()

    def __window_ui(self):
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(850, 525)
        self.setWindowTitle('Historian Tag')
        _menu_bar: QMainWindow.menuBar = self.menuBar()
        _menu_help: QMenu = _menu_bar.addMenu('Help')
        _action_help: QAction = QAction('Info', self)
        _action_help.triggered.connect(self.info_clicked)
        _menu_help.addAction(_action_help)

    def __tab_ui(self):
        _tab_widget: QTabWidget = QTabWidget()
        # self._create_tab(_tab_widget, 'TagImport')
        self.dict_ui['_tab1_ui'] = Tab1UI(historian_main_ui=self, tab_widget=_tab_widget)
        self.dict_ui['_tab2_ui'] = Tab2UI(historian_main_ui=self, tab_widget=_tab_widget)
        self.dict_ui['_tab3_ui'] = Tab3UI(historian_main_ui=self, tab_widget=_tab_widget)
        self.dict_ui['_tab4_ui'] = Tab4UI(historian_main_ui=self, tab_widget=_tab_widget)
        for _idx in range(_tab_widget.count()):
            _tab_widget.tabBar().setFont(ConfigUtil().get_default_font(10))

        self.setCentralWidget(_tab_widget)

    def info_clicked(self):
        message = 'Version: 1.1\n' \
                  'Create Date: 2024.09.30\n' \
                  'Last Update Date: 2024.10.31\n' \
                  'E-Mail : myselfub@gmail.com\n' \
                  'Made by 김유빈'
        self.info_message(title='Information', text=message)

    def info_message(self, title: str, text: str) -> None:
        """ 정보 메세지 포맷
        :param
            title: (str) 제목
            text: (str) 메세지
        :return None
        """
        _message_box: QMessageBox = QMessageBox()
        _message_box.setWindowTitle(title)
        _message_box.setText(text)
        _message_box.setIcon(QMessageBox.Icon.Information)
        _message_box.setStandardButtons(QMessageBox.StandardButton.Close)
        _message_box.exec()

    def critical_message(self, title: str, text: str) -> None:
        """ 크리티컬 메세지 포맷
        :param
            title: (str) 제목
            text: (str) 메세지
        :return None
        """
        _message_box: QMessageBox = QMessageBox()
        _message_box.setWindowTitle(title)
        _message_box.setText(text)
        _message_box.setFont(ConfigUtil().get_default_font(10))
        _message_box.setIcon(QMessageBox.Icon.Critical)
        _message_box.setStandardButtons(QMessageBox.StandardButton.Close)
        _message_box.exec()

    def common_message(self, msg_kind: str) -> None:
        """ 공통 메세지
        :param
            msg_kind: (str) 메세지 종류
        :return None
        """
        _switch: dict = {
            'connect_success': [0, 'Information', 'Connection success'],  # 연결 성공 메세지
            'connect_fail': [0, 'Information', 'Connection failed'],  # 연결 실패 메세지
            'disconnect': [0, 'Information', 'Disconnected'],  # 연결 종료 메세지
            'not_connect': [0, 'Information', 'Please connect Historian'],  # 히스토리안 연결 요청 메세지
            'date_format_error': [0, 'Information', 'The datetime format is different'],  # 날짜 포맷 확인 요청 메세지
            'empty_tag': [0, 'Information', 'Please add TAG'],  # 태그 추가 요청 메세지
            'empty_value': [0, 'Information', 'Please add Value'],  # 값 추가 요청 메세지
            'empty_start_date': [0, 'Information', 'Please enter Start Date'],  # 시작 날짜 입력 요청 메세지
            'write_success': [0, 'Information', 'Write success'],  # 시작 날짜 입력 요청 메세지
            'write_fail': [0, 'Information', 'Write failed'],  # 시작 날짜 입력 요청 메세지
            'file_check': [1, 'Error', 'Please checking File'],  # CSV 파일 확인 요청 메세지
            'field_check': [1, 'Error', f'Please checking Field name\n{ConfigUtil().get_csv_field()}'], # CSV 파일 컬럼명 확인 요청 메세지
            'empty_csv_data': [1, 'Information', f'Please add datas'],  # CSV 파일 컬럼명 확인 요청 메세지
        }

        _ttl_msg_type: list = _switch.get(msg_kind.lower())
        if _ttl_msg_type[0] == 0:
            self.info_message(_ttl_msg_type[1], _ttl_msg_type[2])
        else:
            self.critical_message(_ttl_msg_type[1], _ttl_msg_type[2])


if __name__ == '__main__':
    _app = QApplication(sys.argv)
    _historianTagUI = HistorianMainUI()
    _historianTagUI.show()
    sys.exit(_app.exec())
