# coding=utf-8

import os
import sys
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui


class LoginWindow(QtWidgets.QMainWindow):
    """

       PySide2 GUI 응용 프로그램의 로그인 창을 나타내는 클래스입니다.

       LoginWindow 클래스는 QMainWindow의 하위 클래스이며 사용자를 초기화합니다
       QtUiLoader를 사용하여 .ui 파일에서 인터페이스합니다. 세 개의 QLineEdit 개체를 정의합니다
       사용자가 로그인 정보("Host_Box", "ID_Box" 및 "PW_Box")를 입력할 수 있습니다.

       Attributes:
           - user_list_start (None): 나중에 사용할 자리 표시자 속성
           - host_box (QLineEdit): Host 입력 필드에 해당하는 QLineEdit 개체
           - id_box (QLineEdit): "ID" 입력 필드에 해당하는 QLineEdit 개체
           - pw_box (QLineEdit): 암호 입력 필드에 해당하는 QLineEdit 개체

       Methods:
           - __init__(): 클래스 속성을 초기화하고 .ui 파일에서 UI를 로드하는 생성자 메서드

       Usage:
           1. LoginWindow 인스턴스 만들기
           2. host_box, id_box 및 pw_box 특성을 사용하여 로그인 창에서 사용자 입력을 검색합니다.

       Note:
           이 클래스는 사용자 인증이 필요한 더 큰 GUI 애플리케이션을 구축하기 위한 시작점으로 사용됩니다.
           LoginWindow 클래스는 사용자 입력 확인, 원격 서버와 통신하여 사용자를 인증하거나
           오류 메시지를 표시하는 등의 추가 기능을 포함하도록 확장할 수 있습니다.

       """

    def __init__(self):
        """

        UI 파일을 로드하고 입력 상자를 설정하며 창을 화면 가운데에 정렬하여 로그인 창을 초기화합니다.

        """

        super(LoginWindow, self).__init__()

        self.user_list_start = None

        # 현재 작업 디렉토리 경로를 가져옴
        cwd = os.path.dirname(os.path.abspath(__file__))
        # ui 파일 경로 생성
        ui_path = os.path.join(cwd, 'UI_design', 'Login.ui')
        # ui 파일이 존재하는지 확인
        if not os.path.exists(ui_path):
            raise Exception("UI file not found at: {0}".format(ui_path))

        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        self.ui.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.ui.size(),
                QtGui.QGuiApplication.primaryScreen().availableGeometry(),
            ),
        )

    # ----------------------------------------------------------------------------------------------
        # 입력 상자 설정
        self.host_box = self.ui.findChild(QtWidgets.QLineEdit, "Host_Box")
        self.id_box = self.ui.findChild(QtWidgets.QLineEdit, "ID_Box")
        self.pw_box = self.ui.findChild(QtWidgets.QLineEdit, "PW_Box")

# ----------------------------------------------------------------------------------------------


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    try:
        app = QtWidgets.QApplication().instance()
    except TypeError:
        app = QtWidgets.QApplication(sys.argv)
    myapp = LoginWindow()
    myapp.ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
