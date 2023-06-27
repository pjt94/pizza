# coding=utf-8

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QTableView, QHeaderView

from PizzaMaya.code.filter import Filter


class HorizontalHeader(QtWidgets.QHeaderView):
    """
    헤더에 콤보박스를 추가하는 클래스이다.
    """

    def __init__(self, table):
        """
        변수들을 정의하고 모듈의 인스턴스를 생성하고 sort버튼의 값을 생성한다.
        """
        super(HorizontalHeader, self).__init__(QtCore.Qt.Horizontal)
        self.setSectionsMovable(False)
        self.combo = None
        self.proj_index = 0
        self.proxy_model = None
        self.table = table
        self.model = self.table.model()
        self.ft = Filter()

        # 헤더 셀렉션 옵션 설정
        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setStretchLastSection(True)
        self.setSectionsMovable(False)
        self.setSectionsClickable(True)

    def showEvent(self, event):
        """
        생성한 콤보박스를 보여주는 메서드
        ft.collect_info_task 이 함수를 통해 콤보박스의 요소를 불러온다.
        """
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)

        _, _, proj_set = self.ft.collect_info_task()
        self.combo = QtWidgets.QComboBox(self)
        if proj_set:
            proj_set.sort()
        self.combo.addItems(['Project'] + proj_set)
        self.combo.setStyleSheet("font-family: Arial; font-size: 10pt; font-weight: bold;")
        self.combo.currentTextChanged.connect(self.combobox_changed)
        self.combo.setGeometry(self.sectionViewportPosition(0), 0, self.sectionSize(0) - 0, self.height())
        self.combo.show()

        super(HorizontalHeader, self).showEvent(event)

    def combobox_changed(self, option):
        """
        콤보박스1의 선택사항이 달려졌음을 알려주는 메서드
        그에따라 프록시모델로 테이블뷰1의 내용을 변경한다.
        """
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        if option != 'Project':
            self.proj_index = self.combo.currentIndex()
            self.proxy_model.setFilterRegExp('^{}$'.format(option))
            self.proxy_model.setFilterKeyColumn(0)
            self.table.setModel(self.proxy_model)
        else:
            self.proj_index = 0
            self.proxy_model = None
            self.table.setModel(self.model)


class Table(QTableView):
    """
    프로젝트와 시퀀스 분류에 따라 task를 선택하는 TableView
    """
    def __init__(self):
        """
        헤더와 스타일을 설정한다.
        """
        QTableView.__init__(self)

        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)

        self.setSortingEnabled(True)
        self.vertical_header = self.verticalHeader()
        self.horizontal_header = self.horizontalHeader()
        self.vertical_header.setDefaultAlignment(Qt.AlignVCenter)
        self.horizontal_header.setDefaultAlignment(Qt.AlignHCenter)

        self.vertical_header.setMinimumSectionSize(50)
        self.horizontal_header.setMinimumSectionSize(50)
        self.vertical_header.setSectionResizeMode(QHeaderView.Fixed)
        self.horizontal_header.setFont(font)  # 헤더에 폰트 설정
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignCenter)

        self.setStyleSheet("background-color: #353535; selection-background-color: gray;")
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.horizontal_header.setSectionsClickable(True)
        self.horizontal_header.setSortIndicatorShown(True)
        self.horizontal_header.setStretchLastSection(True)


class Table2(QtWidgets.QTableView):
    """
    테스크가 주어진 레이아웃어셋에 캐스팅된 asset 중 작업파일에 임포트 할 asset을 선택하는 TableView
    """
    def __init__(self, corner=False):
        """
        헤더와 스타일을 설정한다.
        데이터를 설정해준다.
        """
        super(Table2, self).__init__()

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        self.corner = corner

        # QTableView Headers
        self.vertical_header = self.verticalHeader()
        self.horizontal_header = self.horizontalHeader()

        # 고정된 헤더 모드 설정
        self.vertical_header.setSectionResizeMode(QHeaderView.Fixed)
        self.horizontal_header.setSectionResizeMode(QHeaderView.Fixed)

        self.horizontal_header.setFont(font)  # 헤더에 폰트 설정
        self.horizontal_header.setDefaultAlignment(QtCore.Qt.AlignCenter)

        self.vertical_header.setMinimumSectionSize(100)
        self.horizontal_header.setMinimumSectionSize(100)
        self.horizontal_header.setStretchLastSection(True)

        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        if self.corner:
            self.setStyleSheet(
                "background-color: #353535; selection-background-color: gray;};")
            corner_button = self.findChild(QtWidgets.QAbstractButton)
            corner_button.setStyleSheet("background-color: #ABABAB; color: black;")
