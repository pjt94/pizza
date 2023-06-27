# coding=utf-8

import os
import sys

from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui


class Save(QtWidgets.QMainWindow):
    """
    이 클래스는 작업한 내용을 퍼블리시 하기 위한 기능을 실행시키는 UI를 생성하는 뷰이다.
    """
    def __init__(self):
        """
        UI파일을 불러오고 mainWindow를 상속받으며, 현재 UI를 화면 중앙에 띄운다.
        사용할 기능에 대한 instance를 만들고 버튼을 연결해준다.
        """
        super(Save, self).__init__()

        # 현재 작업 디렉토리 경로를 가져옴
        cwd = os.path.dirname(os.path.abspath(__file__))
        # ui 파일 경로 생성
        ui_path = os.path.join(cwd, 'UI_design', 'Save.ui')
        # ui 파일이 존재하는지 확인
        if not os.path.exists(ui_path):
            raise Exception("UI file not found at: {0}".format(ui_path))

        self.ui_file = QtCore.QFile(ui_path)
        self.ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.ui_file)
        self.ui_file.close()
        self.ui.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.ui.size(),
                QtGui.QGuiApplication.primaryScreen().availableGeometry(),
            ),
        )

# ----------------------------------------------------------------------------------------------


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    try:
        app = QtWidgets.QApplication().instance()
    except TypeError:
        app = QtWidgets.QApplication().instance()
    myapp = Save()
    myapp.ui.show()
    sys.exit(app.exec_())


# ----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
