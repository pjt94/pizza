# coding=utf-8

import os
import sys

import gazu
import pprint as pp

from PizzaMaya.code.login import LogIn
from PizzaMaya.code.logger import Logger
from PizzaMaya.code.filter import Filter
from PizzaMaya.code.usemaya import MayaThings
from PizzaMaya.code.publish import PublishThings
from PizzaMaya.code.thumbnail import thumbnail_control

from PizzaMaya.ui.UI_view_publish import Save
from PizzaMaya.ui.UI_view_login import LoginWindow
from PizzaMaya.ui.UI_view_table import Table
from PizzaMaya.ui.UI_view_table import Table2
from PizzaMaya.ui.UI_view_table import HorizontalHeader
from PizzaMaya.ui.UI_model import CustomTableModel

from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui
from PySide2.QtWidgets import QMainWindow, QMessageBox
from PySide2.QtGui import QPixmap, QPixmapCache
from PySide2.QtCore import Qt


class MainWindow(QMainWindow):
    """
    프로그램의 메인윈도우를 정의하는 클래스이다.
    """
    def __init__(self, values=None, parent=None, size_policy=None):
        """
        변수를 정의하고 인스턴스를 생성하며 메인윈도우에 필요한 기능을 버튼과 연결해준다.
        테이블 뷰 생성 후 모델을 추가한다.
        프로그램 시작 시 auto login이 체크되어 있는지 확인하며, 체크되어 있으면 바로 main window 띄어준다.
        """
        super(MainWindow, self).__init__()

        # 현재 작업 디렉토리 경로를 가져옴
        self.task = None
        self.my_task = None
        self.task_info = None
        self.preview_pixmap = None
        self.undi_info_list = None
        self.camera_info_list = None
        self.casting_info_list = None
        self.undi_thumbnail_list = None
        self.asset_thumbnail_list = None
        self.shot_list = None
        self.user_name = None
        self.is_logged_in = False
        self.my_shot_index_list = []
        self.selected_index_list = []  # 선택한 에셋들의 인덱스 번호
        self.shot_dict_list = None
        self.custom_camera = None
        self.all_assets = None
        self.old_or_not = dict()

        # ----------------------------------------------------------------------------------------------

        # 메인 ui 설정
        cwd = os.path.dirname(os.path.abspath(__file__))
        # ui 파일 경로 생성
        ui_path = os.path.join(cwd, 'UI_design', 'Main.ui')
        # ui 파일이 존재하는지 확인
        if not os.path.exists(ui_path):
            raise Exception("UI file not found at: {0}".format(ui_path))
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()

        # ui가 화면 중앙에 뜨도록 설정
        self.ui.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight,
                QtCore.Qt.AlignCenter,
                self.ui.size(),
                QtGui.QGuiApplication.primaryScreen().availableGeometry(),
            ),
        )
        # 메인 윈도우의 레이아웃에 TableView 3개 추가
        self.table = Table()
        self.table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.ui.verticalLayout2.addWidget(self.table, 0)

        self.table2 = Table2(corner=True)
        self.ui.verticalLayout.addWidget(self.table2, 0)

        self.table3 = Table2()
        self.table3.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        self.ui.verticalLayout3.addWidget(self.table3, 0)

        # TableView에 모델 설정
        self.table1_model = CustomTableModel()
        self.table1_model.column_count = 3
        self.table1_model.header_data = ["Project", "Seq", "DueDate"]
        self.table.setModel(self.table1_model)
        self.horizontal_header = HorizontalHeader(self.table)
        self.table.setHorizontalHeader(self.horizontal_header)

        self.table2_model = CustomTableModel()
        self.table2_model.column_count = 3
        self.table2_model.header_data = ["Thumbnail", "Name", "Type"]
        self.table2.setModel(self.table2_model)

        self.table3_model = CustomTableModel()
        self.table3_model.column_count = 2
        self.table3_model.header_data = ["Thumbnail", "Select Shot to Load Camera"]
        self.table3.setModel(self.table3_model)

        # ----------------------------------------------------------------------------------------------

        # 프로그램 시작 시 auto login이 체크되어 있는지 확인하며, 체크되어 있으면 바로 main window 띄움
        self.login_window = LoginWindow()
        self.log = Logger()
        self.login = LogIn()

        value = self.login.load_setting()
        if value and value['auto_login'] and value['valid_host'] and value['valid_user'] is True:
            self.login.host = value['host']
            self.login.user_id = value['user_id']
            self.login.user_pw = value['user_pw']
            self.login.auto_login = value['auto_login']
            self.login.connect_host()
            _, self.user_name = self.login.log_in()
            text = 'User: ' + self.user_name
            self.ui.User_Name.setText(text.encode('utf-8'))
            self.is_logged_in = True

            self.save = Save()
            # Save 버튼, Back 버튼 연결
            self.save.ui.Final_Save_Button.clicked.connect(self.final_save_button)
            self.save.ui.Back_Button.clicked.connect(self.back_button)

            self.ft = Filter()
            self.ma = MayaThings()
            self.pub = PublishThings()
            self.shot_dict_list, self.custom_camera, self.all_assets = self.ma.get_working_task()

            # table1에 데이터 로드
            self.table1_model.load_data(self.read_data())
            self.table1_model.layoutChanged.emit()

            self.scene_open_check()
            self.ui.show()
        else:
            self.login_window.ui.show()

        # ----------------------------------------------------------------------------------------------

        # Login 버튼, Logout 버튼 연결
        self.login_window.ui.Login_Button.clicked.connect(self.login_button)
        self.ui.Logout_Button.clicked.connect(self.logout_button)

        # TableView 3개 연결
        self.table.clicked.connect(self.table_clicked)
        self.table2.clicked.connect(self.table_clicked2)
        self.table3.clicked.connect(self.table_clicked3)

        # table2에 에셋 여러개 선택 가능하게 설정
        self.table2.selectionModel().selectionChanged.connect(self.selection_changed)
        QPixmapCache.setCacheLimit(500 * 1024)

        # Save 클릭시 Save ui로 전환, Load 클릭시 로드됨
        self.ui.Save_Button.clicked.connect(self.save_button)
        self.ui.Load_Button.clicked.connect(self.load_button)

    # ----------------------------------------------------------------------------------------------

    def scene_open_check(self):
        """
        현재 씬에 import된 파일이 있을 경우 작업중인 task와 로드된 asset, camera, undistortion img를 판별하는 함수
        """
        self.shot_dict_list, self.custom_camera, self.all_assets = self.ma.get_working_task()
        if len(self.custom_camera) != 0:
            seq = gazu.shot.get_sequence_from_shot(self.shot_dict_list[0])
            proj = gazu.project.get_project(seq['project_id'])
            for index, item in enumerate(self.task_info):
                if seq['name'] == item['sequence_name'] and proj['name'] == item['project_name']:
                    self.my_task = self.task[index]
                    print('{0} task가 씬에 존재하여 자동 선택되었습니다.'.format(seq['name']))
                    self.table.selectRow(index)
                    self.table_clicked(None, index)
        if len(self.all_assets) != 0:
            old_asset_list = []
            for asset in self.all_assets:
                asset_rn = '_'.join(asset.split('_')[:-2]) + 'RN'
                asset_name = asset.split('_')[2]
                revision = int((asset.split('_')[4]).split('v')[1])
                proj = gazu.project.get_project_by_name(asset.split('_')[0])
                output_type = gazu.files.get_output_type_by_name('FBX')
                task_type = gazu.task.get_task_type_by_name('Modeling')
                kitsu_asset = gazu.asset.get_asset_by_name(proj, asset_name.title())
                if kitsu_asset:
                    output_file = gazu.files.get_last_output_files_for_entity(kitsu_asset, output_type, task_type)
                    kitsu_revision = output_file[0]['revision']
                    print('A', kitsu_revision)
                    print('B', revision)
                    if revision < kitsu_revision:
                        old_asset_list.append(asset)
                        ask = QMessageBox()
                        ask.setText(
                            '현재 씬에 존재하는 {0}에셋이 최신 파일이 아닙니다. 최신 파일을 로드하시겠습니까?'.format(str(old_asset_list)))
                        ask.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        ask.setWindowTitle("Old File Exists")
                        reply = ask.exec_()
                        if reply == QMessageBox.Yes:
                            print("현재 레퍼런스된 파일을 새 파일로 교체합니다.")
                            self.ma.update_reference(kitsu_asset, asset_rn, kitsu_revision, output_type, task_type)

    # ----------------------------------------------------------------------------------------------

    # 정보 입력 후 로그인 버튼을 클릭하면 Kitsu에 로그인을 하고, 오토로그인이 체크되어있는지 판별
    # 로그아웃 버튼 클릭 시 Kitsu에서 로그아웃을 하고, 메인 윈도우 hide한 뒤 로그인 윈도우 띄움

    def login_button(self):
        """
        자동로그인이 선택되지 않았을 시에 로그인에 대한 뷰가 띄어졌을 경우에 해당 뷰에 동작을 관할하는 메서드
        사용자가 호스트 박스, ID박스, PW박스에 입력한 정보를 기반으로 키츄에 로그인한다.
        """
        # 사용자가 입력한 텍스트를 받아서 변수에 저장하고, 오토로그인 체크 여부 갱신
        host_box = self.login_window.ui.Host_Box
        id_box = self.login_window.ui.ID_Box
        pw_box = self.login_window.ui.PW_Box
        self.login.host = host_box.text()
        self.login.user_id = id_box.text()
        self.login.user_pw = pw_box.text()
        self.login.auto_login = self.login_window.ui.Auto_Login_Check.isChecked()

        # 로그인 진행
        tf1 = self.login.connect_host()
        tf2, self.user_name = self.login.log_in()
        text = 'User: ' + self.user_name
        self.ui.User_Name.setText(text.encode('utf-8'))
        self.is_logged_in = True

        if tf1 and tf2 and self.is_logged_in:
            self.save = Save()
            # Save 버튼, Back 버튼 연결
            self.save.ui.Final_Save_Button.clicked.connect(self.final_save_button)
            self.save.ui.Back_Button.clicked.connect(self.back_button)

            self.ft = Filter()
            self.ma = MayaThings()
            self.pub = PublishThings()

            # table1에 데이터 로드
            self.table1_model.load_data(self.read_data())
            self.table1_model.layoutChanged.emit()

            self.scene_open_check()

            # 로그인 ui 숨기고 메인 ui 띄움
            self.login_window.ui.hide()
            self.ui.show()

    def logout_button(self):
        """
        키츄에서 로그아웃하고 메인 윈도우를 닫은 뒤 로그인 윈도우를 띄운다.
        """
        self.login.log_out()
        self.ui.hide()
        self.login_window.ui.show()

    # ----------------------------------------------------------------------------------------------

    # 퍼블리시 윈도우에서 버튼을 클릭 시 동작하는 내용

    def final_save_button(self):
        """
        최종 퍼블리시 승인 버튼이다.
        이  버튼을 클릭하면 현재 작업하는 씬에 존재하는 카메라의 목록을 불러와 리스트에 추가하고 그 리스트에서 디폴트
        카메라를 제외한 유저가 작업한 샷의 카메라만 남겨서 pub.save_publish_previews()에 넘겨준다.
        text박스 안에 작성한 문장은 퍼블리시하는 파일들의 comment로 작성된다.
        또한 카메라의 이름으로부터 시퀀스의 정보들을 얻어낸다.
        pub.save_publish_real_data 이 함수를 통해 작업한 파일들을 실제로 폴더안에 저장한다.
        이때 사용하는 my task 변수는 UI컨트롤러에서 정보를 받아온다.
        """
        comment = self.save.ui.Save_Path_View_2.toPlainText()
        shot_dict_list, custom_camera, _ = self.ma.get_working_task()
        self.pub.save_publish_real_data(self.my_task, comment)
        self.pub.save_publish_previews(shot_dict_list, custom_camera, comment)
        self.ui.hide()  # 메인 윈도우 숨김
        self.save.ui.close()
        # 퍼블리시 완료 팝업
        completed = QMessageBox()
        completed.setText("퍼블리시가 완료되었습니다!")
        completed.setStandardButtons(QMessageBox.Ok)
        completed.setWindowTitle("Completed")
        self.log.save_output_file_log(self.my_task['entity_name'])

        completed.exec_()

    def back_button(self):
        """
        퍼블리시를 취소하고 뒤로 돌아간다.
        """
        self.save.ui.close()

    # ----------------------------------------------------------------------------------------------

    # save 또는 load 버튼 누르면 save 또는 load 윈도우를 호출

    def save_button(self):
        """
        선택한 테스크에 대한 작업내용을 퍼블리시하는 버튼 클릭 시 save ui를 띄우고, my_task의 정보를 넘긴다.
        """
        self.shot_dict_list, self.custom_camera, self.all_assets = self.ma.get_working_task()
        if len(self.custom_camera) == 0 and len(self.all_assets) == 0:
            warning = QMessageBox()
            warning.setText("⚠ 비어있는 씬은 퍼블리시할 수 없습니다.")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setWindowTitle("Error")
            warning.exec_()
        elif len(self.custom_camera) == 0 and len(self.all_assets) != 0:
            warning = QMessageBox()
            warning.setText("⚠ 카메라가 존재하지 않는 씬은 퍼블리시할 수 없습니다.")
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setWindowTitle("Error")
            warning.exec_()
        else:
            seq = gazu.shot.get_sequence_from_shot(self.shot_dict_list[0])['name']
            asset = gazu.asset.get_asset(self.my_task['entity_id'])
            warning = QMessageBox()
            warning.setText("작업물({0}, 이름: {1})을 퍼블리시하는 것이 맞습니까?".format(seq, asset['name']))
            warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            warning.setWindowTitle("Publish Check")
            reply = warning.exec_()
            if reply == QMessageBox.Yes:
                self.save.ui.show()

    def load_button(self):
        """
        선택한 어셋과 카메라와 언디스토션 이미지를 현재작업 영역에 임포트하는 메서드
        """
        if not self.my_task:
            return
        else:
            ask = QMessageBox()
            ask.setText(
                "{0}개의 에셋과 {1}개의 샷을 로드하시겠습니까?".format(len(self.selected_index_list), len(self.my_shot_index_list)))
            ask.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ask.setDefaultButton(QMessageBox.NoButton)
            ask.setWindowTitle("Load Check")
            reply = ask.exec_()

            if reply == QMessageBox.Yes:
                my_layout_asset = gazu.asset.get_asset(self.my_task['entity_id'])
                self.ma.import_casting_asset(my_layout_asset, self.selected_index_list)
                for index in self.my_shot_index_list:
                    shot_list = gazu.casting.get_asset_cast_in(self.my_task['entity_id'])
                    self.ma.import_cam_seq(shot_list[index])
                # 메인 윈도우 닫음
                self.ui.close()
                # 로드 완료 팝업
                completed = QMessageBox()
                completed.setText("로드되었습니다!")
                completed.setStandardButtons(QMessageBox.Ok)
                completed.setWindowTitle("Completed")
                self.log.load_file_log(self.selected_index_list)

                completed.exec_()

    # ----------------------------------------------------------------------------------------------

    # TableView의 항목을 클릭하면 항목의 정보를 프린트 해줌

    def selection_changed(self):
        """
        사용자가 선택한 어셋의 인덱스 번호를 수집하는 메서드
        """
        selection_model = self.table2.selectionModel()
        selected_rows = selection_model.selectedRows()
        selected_indexes = selection_model.selectedIndexes()
        row_count = self.table2_model.row_count

        sel_asset_ids = set()
        for sel_idx in selected_indexes:
            sel_asset_ids.add(sel_idx.row())
        self.selected_index_list = sel_asset_ids
        self.ui.Selection_Lable.setText('Selected Files %d / %d' % (len(selected_rows), row_count))

        # 현재 클릭한 인덱스 번호와 몇개를 클릭했는지 출력
        print(self.ui.Selection_Lable.text())

    def no_data_no_click(self, model):
        """
        table2에 썸네일 None이면 선택 안되게 설정

        Args:
            model: QTableView에 SetModel 한 QTableModel
        """
        asset_rows = model.rowCount()
        for index in range(asset_rows):
            png_index = model.index(index, 0)
            data = model.data(png_index)
            if data == None:
                print("{0}번 항목은 로드할 데이터가 없어 선택할 수 없습니다.".format(index))

    def already_loaded_no_click(self, item, model):
        shot_dict_list, custom_camera, all_assets = self.ma.get_working_task()

        if item == "asset":
            for index in range(len(self.casting_info_list)):
                for asset in all_assets:
                    scene_asset_name = self.casting_info_list[index]['asset_name'].lower()
                    if scene_asset_name in asset:
                        print('{0} 에셋은 이미 로드되어 선택할 수 없습니다.'.format(self.casting_info_list[index]['asset_name']))
                        model.asset_name = self.casting_info_list[index]['asset_name']

        elif item == "shot":
            for index in range(len(self.camera_info_list)):
                for cam in custom_camera:
                    if self.camera_info_list[index][0]['shot_name'] and \
                            self.camera_info_list[index][0]['shot_name'] in cam:
                        print('{0} 샷은 이미 로드되어 선택할 수 없습니다.'.format(self.camera_info_list[index][0]['shot_name']))
                        model.asset_name = self.camera_info_list[index][0]['shot_name']

    def table_clicked(self, event, index=None):
        """
        테스크 목록이 띄워져있는 테이블뷰를 클릭하였을 때 동작하는 메서드
        선택한 테스크에 기반하여 파일 임포트 할 때와 테이블뷰2, 테이블뷰3에 필요한 정보를 받아온다.
        """
        if index:
            task_clicked_index = index
        else:
            task_clicked_index = event.row()

        clicked_asset = self.table.model().data(self.table.model().index(task_clicked_index, 1))
        self.my_task, task_info, self.casting_info_list, \
            self.undi_info_list, self.camera_info_list = self.ft.select_task(self.horizontal_header.proj_index,
                                                                             task_clicked_index, clicked_asset)
        tup, self.asset_thumbnail_list, self.undi_thumbnail_list, self.shot_list = \
            thumbnail_control(self.my_task, task_clicked_index, self.casting_info_list, self.undi_info_list)
        png = bytes(tup)

        self.preview_pixmap = QPixmap()
        self.preview_pixmap.loadFromData(png)
        label = self.ui.Preview
        label.setPixmap(self.preview_pixmap.scaled(label.size(), Qt.KeepAspectRatio))
        self.ui.InfoTextBox.setPlainText('Project Name: {}'.format(task_info['project_name'] + '\n'))
        self.ui.InfoTextBox.appendPlainText('Description: {0}'.format(task_info['description']))
        self.ui.InfoTextBox.appendPlainText('Due Date: {0}'.format(task_info['due_date']))
        if task_info['last_comment']:
            self.ui.InfoTextBox.appendPlainText(
                'Comment: {}'.format(task_info['last_comment']['text'].encode('utf-8')))
        else:
            self.ui.InfoTextBox.appendPlainText('Comment: None')
        self.table2_model.load_data(self.read_data2())
        self.table2_model.layoutChanged.emit()
        self.no_data_no_click(self.table2_model)
        self.already_loaded_no_click('asset', self.table2_model)

        self.table3_model.load_data(self.read_data3())
        self.table3_model.layoutChanged.emit()
        self.no_data_no_click(self.table3_model)
        self.already_loaded_no_click('shot', self.table3_model)

    def table_clicked2(self, event):
        """
        어셋 목록이 띄워져있는 테이블뷰를 클릭하였을 때 동작하는 메서드
        선택한 어셋에 기반하여 정보를 받아오고 그 정보를 크게 띄운다.
        """
        clicked_cast = self.casting_info_list[event.row()]
        png = bytes(self.asset_thumbnail_list[event.row()])

        self.preview_pixmap = QPixmap()
        self.preview_pixmap.loadFromData(png)
        label = self.ui.Preview
        label.setPixmap(self.preview_pixmap.scaled(label.size(), Qt.KeepAspectRatio))

        self.ui.InfoTextBox.setPlainText('Asset Name: {}'.format(clicked_cast['asset_name'] + '\n'))
        self.ui.InfoTextBox.appendPlainText('Description: {0}'.format(clicked_cast['description']))
        self.ui.InfoTextBox.appendPlainText('Asset Type: {0}'.format(clicked_cast['asset_type_name']))
        self.ui.InfoTextBox.appendPlainText('Occurence: {0}'.format(str(clicked_cast['nb_occurences'])))
        self.ui.InfoTextBox.appendPlainText('Output File: {0}'.format(str(len(clicked_cast['output']))))
        self.ui.InfoTextBox.appendPlainText('Latest or Not: {0}'.format(self.old_or_not[clicked_cast['asset_name']]))

    def table_clicked3(self, event):
        """
        샷 목록이 띄워져있는 테이블뷰를 클릭하였을 때 동작하는 메서드
        선택한 샷에 기반하여 정보를 받아오고 그 정보를 크게 띄운다.
        """
        clicked_undi = self.undi_info_list[event.row()][0]
        clicked_cam = self.camera_info_list[event.row()][0]
        png = bytes(self.undi_thumbnail_list[event.row()])

        self.preview_pixmap = QPixmap()
        self.preview_pixmap.loadFromData(png)
        label = self.ui.Preview
        label.setPixmap(self.preview_pixmap.scaled(label.size(), Qt.KeepAspectRatio))

        selection_model = self.table3.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        sel_shot_indexes = set()
        for sel_idx in selected_indexes:
            sel_shot_indexes.add(sel_idx.row())
        self.my_shot_index_list = sel_shot_indexes

        self.ui.InfoTextBox.setPlainText('[Shot Info]')
        self.ui.InfoTextBox.appendPlainText('Shot Name: {}'.format(clicked_undi['shot_name'] + '\n'))
        self.ui.InfoTextBox.appendPlainText('[Undistortion Image Info]')
        self.ui.InfoTextBox.appendPlainText('Frame Range: {}'.format(clicked_undi['frame_range']))
        self.ui.InfoTextBox.appendPlainText('Description: {0}'.format(clicked_undi['description']))
        st = '\n'
        new_str = st.lstrip()
        self.ui.InfoTextBox.appendPlainText(new_str)
        self.ui.InfoTextBox.appendPlainText('[Camera Info]')
        self.ui.InfoTextBox.appendPlainText('Asset Type: {0}'.format(clicked_cam['output_type_name']))
        self.ui.InfoTextBox.appendPlainText('Description: {0}'.format(str(clicked_cam['description'])))

    # ----------------------------------------------------------------------------------------------
    # TableView 두개에 띄울 각각의 정보를 넣어둠

    def read_data(self):
        """
        task 선택하는 TableView의 데이터를 받아오는 메서드
        filter의 선택에 따라 정보가 바뀐다.
        """
        self.task, self.task_info, _, _, _ = self.ft.select_task()
        data = []
        for index in range(len(self.task_info)):
            data.append([self.task_info[index]['project_name'],
                         self.task_info[index]['sequence_name'] + '\n' + self.task_info[index]['asset_name'],
                         self.task_info[index]['due_date']])

        return data

    def read_data2(self):
        """
        asset 선택하는 TableView의 데이터를 받아오는 메서드
        task 선택 후 data가 생성된다.
        """
        # 썸네일을 얻기 위해 받아와야 하는 정보
        data = []
        if self.my_task is not None:
            # 캐스팅된 에셋목록 추가
            for index, cast in enumerate(self.casting_info_list):
                if len(cast['output']) != 0:
                    self.old_or_not[self.casting_info_list[index]['asset_name']] = 'Latest File Exists'
                    if len(self.asset_thumbnail_list):
                        data.append([self.asset_thumbnail_list[index], cast['asset_name'], cast['asset_type_name']])
                    else:
                        data.append([None, cast['asset_name'], cast['asset_type_name']])
                else:
                    self.old_or_not[self.casting_info_list[index]['asset_name']] = None
                    data.append([None, cast['asset_name'], 'No Output File to Load'])

            return data
        else:

            return data

    def read_data3(self):
        """
        샷 선택하는 TableView의 데이터를 받아오는 메서드
        task 선택 후 data가 생성된다.
        """
        data = []
        if self.my_task:
            # 샷 목록 추가
            for index, _ in enumerate(self.undi_info_list):
                if self.shot_list:
                    try:
                        self.undi_thumbnail_list[index]
                    except IndexError as exc:
                        data.append([None, self.shot_list[index]['shot_name']])
                        continue
                    data.append([self.undi_thumbnail_list[index], self.shot_list[index]['shot_name']])
                else:
                    data.append([None, 'No Output File to Load'])

            return data
        else:

            return data

    # ----------------------------------------------------------------------------------------------


def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    try:
        app = QtWidgets.QApplication().instance()
    except TypeError:
        app = QtWidgets.QApplication()
    myapp = MainWindow()
    myapp.ui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
