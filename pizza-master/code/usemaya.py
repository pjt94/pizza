#coding:utf8
import os
import re
import gazu
import pprint as pp
import maya.cmds as mc
from usekitsu import KitsuThings
from logger import Logger


class MayaThings:
    """
    마야에서 working, output, preview 파일을 import, export하는 클래스
    """
    def __init__(self):
        """
        모듈의 인스턴스를 생성한다.
        """
        self.kit = KitsuThings()
        self.log = Logger()

    def load_working(self, task, num=0):
        """
        마야에서 선택한 테스크에 working file이 있을 경우, 해당 파일을 import 하는 매서드

        * UI에서 적절히 구현할 방법을 찾지 못했다...

        Args:
            task(dict): 사용자가 선택한 task의 딕셔너리
            num(int): 사용자가 선택한 working file의 revision
        """
        working = gazu.files.get_last_working_file_revision(task)

        if working is None:
            raise ValueError("working file이 존재하지 않습니다")
        elif num != 0:
            path = gazu.files.build_working_file_path(task, revision=num)
        else:
            path = gazu.files.build_working_file_path(task, revision=working['revision'])
        path = path + '.' + working['representation']
        mc.file(path, i=True)

    def _load_output(self, path, undi_seq_path=None, asset=None):
        """
        마야에서 task asset에 캐스팅된 에셋들의 output file들을 레퍼런스 형태로 import하는 매서드

        입력된 패스가 언디스토션 이미지라면 시퀀스 길이를 패딩에 맞게 재설정하되, 최대값에 맞춘다.
        입력된 패스가 에셋(fbx, obj 등)이라면 nb_elements의 값에 맞게 인스턴스를 생성한다.

        Args:
            path(str): 확장자를 포함한 아웃풋 파일의 패스
            asset(dict): 로드하고자 하는 에셋 아웃풋 파일의 nb_elements, path 정보가 담긴 딕셔너리
        """
        if undi_seq_path:
            # 시퀀스 길이(씬의 프레임레인지) 를 가장 길게 설정
            file_list = os.listdir(os.path.dirname(undi_seq_path))
            frame_range = len(file_list)
            end_frame = mc.playbackOptions(query=True, max=True)
            # if end_frame < frame_range:
            mc.playbackOptions(min=1001, max=frame_range+1000)

        objects_shape = mc.ls(type='mesh')
        objects = mc.listRelatives(objects_shape, p=1)
        object_found = None
        new_z = 0
        if objects:
            for obj in objects:
                pos = mc.xform(obj, q=True, ws=True, t=True)
                if pos == [0.0, 0.0, 0.0]:
                    object_found = True
                else:
                    object_found = False
                    break
                while object_found:
                    for obj in objects:
                        pos = mc.xform(obj, q=True, ws=True, t=True)
                        if pos == [0.0, new_z, 0.0]:
                            new_z += 1
                        else:
                            object_found = False

        my_object_nodes = mc.file(
            path, r=True, ignoreVersion=True,
            # path의 아웃풋 파일을 import 하는데, 이 때 파일의 버전 번호를 무시한다.
            mergeNamespacesOnClash=False,
            # 네임스페이스 충돌이 발생하면 병합하지 않도록 지정
            # fbx 애니메이션 데이터를 씬의 기존 애니메이션과 결합하도록 지정
            loadReferenceDepth="all",
            returnNewNodes=True
            # 변수에 노드의 정보값을 넣으려고 쓰는 거라 없어도 될 듯
        )
        my_object = mc.ls(my_object_nodes, type='transform')
        if object_found != None:
            mc.setAttr("%s.translateZ" % my_object[0], new_z)

        i = 0
        v = 0
        if asset and asset['nb_elements'] > 1:
            # 에셋이라면 nb_elements에 맞게 인스턴싱 진행
            for index in range(asset['nb_elements']-1):
                full_filename = os.path.basename(asset['path'])
                file_name_parts = full_filename.split('_')
                import_name = '_'.join(file_name_parts[:-1]) \
                              + '__1_' + str(asset['nb_elements']) + '__' + file_name_parts[2] + '_GRP'
                try:
                    mesh = mc.listRelatives(import_name, c=1)
                except ValueError as exc:
                    import_name = '_'.join(file_name_parts[:-1]) \
                                  + '__1_' + str(asset['nb_elements']) + '__' + file_name_parts[2]
                    mesh = mc.listRelatives(import_name, c=1)

                instance_geo = mc.instance(mesh)
                bounding_box = mc.exactWorldBoundingBox(instance_geo, ce=1)
                if index <= 10:
                    mc.setAttr("%s.translateX" % instance_geo[0], i + bounding_box[3]*2)
                    i += bounding_box[3]*2
                    mc.setAttr("%s.translateZ" % instance_geo[0], new_z-1)
                else:
                    mc.setAttr("%s.translateZ" % instance_geo[0], bounding_box[5] * 2)
                    mc.setAttr("%s.translateX" % instance_geo[0], v + bounding_box[3]*2)
                    v += bounding_box[3] * 2

    def _connect_image(self, undi_path, camera_path):
        """
        import한 언디스토션 이미지(아웃풋 파일) 시퀀스와 camera를 연결시켜주는 매서드

        카메라가 바라보는 방향에 언디스토션 이미지가 뜨고, 카메라와 이미지 플레인을 연결하여
        이미지가 카메라의 움직임에 따라 움직이며, 시퀀스 옵션을 True로 하여 이미지가 영상처럼 넘어가게 한다.
        그리고 노드로 둘을 연결해 visibility를 한번에 컨트롤할 수 있게 한다.

        Args:
            undi_path(str): 확장자까지 포함된 첫번째 언디스토션 이미지의 파일경로
            camera_path(str): 카메라 파일의 전체 경로
        """
        camera_name_tmp = (os.path.basename(camera_path)).split('.')[0]

        startup_cameras = []
        all_cameras = mc.ls(type='camera', l=True)
        for camera in all_cameras:
            if mc.camera(mc.listRelatives(camera, parent=True)[0], startupCamera=True, q=True):
                startup_cameras.append(camera)
        custom_camera = list(set(all_cameras) - set(startup_cameras))

        for cam_name in custom_camera:
            if camera_name_tmp in cam_name:
                cam_name_parts1 = cam_name.split("|")
        camera_name = camera_name_tmp + '_object'
        try:
            image_plane = mc.imagePlane(camera=camera_name)
        except RuntimeError as exc:
            camera_name = camera_name_tmp + '_cam_fire_FS'
            image_plane = mc.imagePlane(camera=camera_name)

        mc.setAttr(image_plane[0]+'.imageName', undi_path, type='string')
        mc.setAttr(image_plane[0]+'.useFrameExtension', True)
        mc.connectAttr('%s.visibility' % camera_name, '%s.visibility' % image_plane[0])

    def import_cam_seq(self, shot_simple):
        """
        선택한 샷에 소속된 언디스토션 시퀀스를 찾고(kit.get_undistort_img)
        샷에 소속된 카메라 output file도 찾아서(kit.get_camera)
        모두 import한 뒤(load_output), 언디스토션 시퀀스를 카메라와 연결시키는(connect_image) 매서드

        Args:
            shot_simple(dict): 선택한 테스크의 작업 asset이 cast in된 샷들 중 import하길 원하는 샷의 간소화된 캐스팅ver 딕셔너리
        """
        shot = gazu.shot.get_shot(shot_simple['shot_id'])
        undi_seq_path = self.kit.get_undistortion_img(shot)
        camera_path = self.kit.get_camera(shot)
        # self._load_output(undi_seq_path)
        self._load_output(camera_path, undi_seq_path)
        self._connect_image(undi_seq_path, camera_path)

    def import_casting_asset(self, asset, num_list=None):
        """
        작업 asset에 캐스팅된 에셋들 중 선택한 것들의 output file 저장위치를 추출하여 마야에 import 하는 매서드

        task asset에 캐스팅된 에셋들 중 import 할 파일을 고른 뒤,
        각각의 확장자 포함된 패스를 추출하고(kit.get_kitsu_path),
        추출한 패스를 기반으로 마야에 import 한다.(_load_output)

        file_dict_list: 캐스팅된 모든 에셋에 있는 각 output file들(최신버전)의
                        path, nb_elements가 기록된 dict를 모은 리스트
        asset_output_list: 에셋 하나에 대한 output file들(최신버전)의 path, nb_elements가 기록된 dict를 모은 리스트

        Args:
            asset(dict): 선택한 task가 속한 작업 에셋
            num_list(list): import 하기를 선택한 에셋의 인덱스 번호의 집합
        """
        file_dict_list = []
        all_cast_list = gazu.casting.get_asset_casting(asset)

        for casting in all_cast_list:
            output_path_nb_dict = self.kit.get_asset_path(casting)
            if output_path_nb_dict:
                file_dict_list.append(output_path_nb_dict)
        for index in num_list:
            asset_output = file_dict_list[index]
            if asset_output['path'] == '':
                print('asset에 아웃풋 파일이 존재하지 않습니다. Asset Name: {0}'.format(asset['name']))
            else:
                self._load_output(asset_output['path'], asset=asset_output)
                self.log.load_file_log(asset_output['name'])

    def save_scene_file(self, path, representation):
        """
        마야 내에서 저장 경로와 저장 형식을 선택해 작업한 씬 파일을 저장하는 매서드

        working file은 .ma, output file은 .mb 형태로 저장된다.

        Args:
            path(str): 씬파일을 저장할 확장자를 제외한 이름까지의 경로
            representation(str): "ma"또는 "mb" 확장자
        """
        full_path = path+'.'+representation
        maya_path = os.path.dirname(full_path)
        if os.path.exists(maya_path) == False:
            os.makedirs(maya_path)
        mc.file(rename=full_path)
        if representation == 'mb':
            mc.file(save=True, type='mayaBinary', force=True)
        else:
            mc.file(save=True, type='mayaAscii', force=True)

    def _make_main_preview_mov(self, path):
        """
        레이아웃의 main preview용 파일을 만드는 매서드

        먼저 카메라 그룹을 생성하고, 동일한 파일명이 있는지 확인하여 존재한다면 suffix의 숫자를 하나 올린다.
        그리고 다른 카메라와 언디스토션 이미지를 모두 보이지 않게 설정한 뒤,
        main preview용 영상(플레이블라스트)을 지정된 path에 저장하고,
        프리뷰를 만들기 위해 생성한 카메라 그룹을 삭제한다.

        Args:
            path: mov파일을 저장할 확장자를 제외한 이름까지의 경로
        """
        cam = mc.camera(
            centerOfInterest=5, focalLength=35,
            lensSqueezeRatio=1, cameraScale=1,
            horizontalFilmAperture=1.41732,
            horizontalFilmOffset=0,
            verticalFilmAperture=0.94488,
            verticalFilmOffset=0, filmFit='Fill',
            overscan=1, motionBlur=0, shutterAngle=144,
            nearClipPlane=0.1, farClipPlane=100000,
            orthographic=0, orthographicWidth=30,
            panZoomEnabled=0, horizontalPan=0,
            verticalPan=0, zoom=1
        )
        # 시퀀스 프리뷰 카메라 생성
        mc.setAttr("%s.rotateX" % cam[0], -35)
        mc.lookThru(cam[0])
        mc.viewFit(cam[1], all=True)
        # 35도 all frame view 만들기
        group_name = '%s_GRP' % cam[0]
        cam_group = mc.group(em=1, n=group_name)
        # 카메라 그룹 만들기
        mc.parent(cam, cam_group)
        # 위치가 (0,0,0)인 그룹에 카메라 페런트
        mc.currentTime(1)
        mc.setKeyframe("%s.ry" % cam_group)
        mc.currentTime(120)
        mc.setAttr("%s.rotateY" % cam_group, 360)
        mc.setKeyframe("%s.ry" % cam_group)
        # 1~120프레임 카메라그룹 rotateY값에 360도 키설정

        # 동일한 파일명 있는지 확인 후 존재하면 file name의 suffix 올림
        filename = '_main'
        extension = 'mov'
        if os.path.exists(path + filename + '.' + extension):
            i = 1
            while os.path.exists(path + filename + '_%02d.' % i + extension):
                i += 1
            filename = filename + '_%02d' % i

        # 모든 카메라와 언디img를 안 보이게 꺼줌
        all_cameras = mc.ls(type='camera', l=True)
        for camera in all_cameras:
            cam_name_parts = camera.split('|')
            if len(cam_name_parts) < 3:
                mc.setAttr("%s.visibility" % cam_name_parts[1], False)
            else:
                mc.setAttr("%s.visibility" % cam_name_parts[2], False)

        # 플레이블라스트 mov출력
        mc.playblast(
            format='qt',
            filename=path+filename,
            sequenceTime=False,
            clearCache=True, viewer=True,
            showOrnaments=True,
            fp=4, percent=50,
            compression='jpeg',
            quality=50,
            startTime=0,
            endTime=300,
            wh=(1920, 1080)
        )
        mc.delete(cam_group)
        # 메인 프리뷰용 카메라 그룹지우기

    def export_output_n_main_preview_file(self, path, preview_path):
        """
        작업한 파일을 mb 형태의 output file로 저장하고(save_scene_file),
        레이아웃 작업의 main preview 파일도 mov로 저장하는(_make_main_preview_mov) 매서드

        Args:
            path(str): output file을 저장할 확장자를 제외한 경로
            preview_path(str): preview file을 저장할 확장자를 제외한 경로
        """
        # output file 저장
        self.save_scene_file(path, 'mb')

        # main preview file 저장
        self._make_main_preview_mov(preview_path)
        
    def export_shot_previews(self, path, shot, custom_camera):
        """
        각 샷에 해당하는 preview 영상을 저장하는 매서드

        현재 작업중인 씬에 존재하는 모든 카메라(샷)에 대한 프리뷰 영상을 프레임레인지에 맞게 저장한다.
        그리고 저장을 하기 전에 방해가 되는 다른 카메라, 언디스토션 이미지를 모두 보이지 않게 한다.

        Args:
            path(str): preview 파일의 확장자를 뺀 전체 경로
            shot(dict): preview 파일을 저장할 shot의 딕셔너리
            camera(str): 현재 작업중인 마야 씬에 존재하는 카메라의 하이어라키 구조
        """
        # shot의 언디스토션 이미지들을 저장한 폴더로부터 프레임 레인지를 추출
        undi_seq_path = self.kit.get_undistortion_img(shot)
        file_list = os.listdir(os.path.dirname(undi_seq_path))
        frame_range = len(file_list)

        # 다른 카메라랑 이미지플레인 다 끄고, 샷에 해당하는 카메라만 켜서 플레이블라스트 프리뷰 저장
        startup_cameras = []
        all_cameras = mc.ls(type='camera', l=True)
        for cam in all_cameras:
            if mc.camera(mc.listRelatives(cam, parent=True)[0], startupCamera=True, q=True):
                startup_cameras.append(cam)
        # for cam in startup_cameras:
        #     cam_name_parts = cam.split('|')
        #     mc.setAttr("%s.visibility" % cam_name_parts[1], False)

        # startup_cameras = []
        # all_cameras = mc.ls(type='camera', l=True)
        # for cam in all_cameras:
        #     if mc.camera(mc.listRelatives(cam, parent=True)[0], startupCamera=True, q=True):
        #         startup_cameras.append(cam)
        # print(startup_cameras)
        # custom_camera = list(set(all_cameras) - set(startup_cameras))
        # for cam in custom_camera:
        #     print(cam)
        #     transform_cam = mc.listRelatives(cam, p=1)
        #     print(transform_cam)
        #     mc.setAttr("%s.visibility" % transform_cam[0], False)

        cam_name_parts = custom_camera.split('|')
        mc.setAttr("%s.visibility" % cam_name_parts[1], True)
        mc.lookThru(custom_camera)
        mc.playblast(
            format='qt',
            filename=path,
            sequenceTime=False,
            clearCache=True, viewer=True,
            showOrnaments=True,
            percent=50,
            compression="jpeg",
            quality=50,
            startTime=1001,
            endTime=frame_range+1000,
            wh=(1920, 1080)
        )

        # for cam in startup_cameras:
        #     cam_name_parts = cam.split('|')
        #     mc.setAttr("%s.visibility" % cam_name_parts[1], True)

    def export_shot_scene(self, path, shot, camera):
        """
        각 샷에 해당하는 .mb파일을 샷의 layout(task type) 폴더에 저장하는 매서드

        그리고 저장을 하기 전에 방해가 되는 다른 카메라, 언디스토션 이미지를 모두 보이지 않게 한다.

        Args:
            path(str): 샷 씬파일의 확장자를 뺀 전체 경로
            shot(dict): mb 파일을 저장할 shot의 딕셔너리
            camera(str): 현재 작업중인 마야 씬에 존재하는 카메라의 하이어라키 구조
        """
        # shot의 언디스토션 이미지들을 저장한 폴더로부터 프레임 레인지를 추출
        undi_seq_path = self.kit.get_undistortion_img(shot)
        file_list = os.listdir(os.path.dirname(undi_seq_path))
        frame_range = len(file_list)

        # 다른 카메라랑 이미지플레인 다 끄고, 샷에 해당하는 카메라만 켜서 mb 파일 저장
        shot_name = shot['name']
        if shot_name not in camera:
            cam_name_parts = camera.split('|')
            mc.setAttr("%s.visibility" % cam_name_parts[1], False)
        else:
            cam_name_parts = camera.split('|')
            mc.setAttr("%s.visibility" % cam_name_parts[1], True)
            mc.lookThru(camera)
            self.save_scene_file(path, 'mb')
            mc.setAttr("%s.visibility" % cam_name_parts[1], False)
            # 켰던 카메라 다시 꺼줌

    def get_working_task(self):
        shot_dict_list = []
        startup_cameras = []
        all_assets = []
        all_references = mc.ls(references=True)
        for ref in all_references:
            ref_nodes = mc.referenceQuery(ref, nodes=True)
            if ref_nodes:
                for node in ref_nodes:
                    if mc.objectType(node) == 'mesh':
                        while True:
                            parent = mc.listRelatives(node, parent=True)
                            if parent is None:
                                root_node = node
                                break
                            else:
                                node = parent[0]
                        if root_node not in all_assets:
                            all_assets.append(root_node)

        all_cameras = mc.ls(type='camera', l=True)
        for camera in all_cameras:
            if mc.camera(mc.listRelatives(camera, parent=True)[0], startupCamera=True, q=True):
                startup_cameras.append(camera)
        custom_camera = list(set(all_cameras) - set(startup_cameras))

        if custom_camera:
            for cam_name in custom_camera:
                cam_name_parts1 = cam_name.split("|")
                cam_name_parts_list = re.split(r'_v\d+_', cam_name_parts1[1])
                cam_name_parts2 = cam_name_parts_list[0].split('_')
                proj_name = (cam_name_parts2[0]).title()
                proj = gazu.project.get_project_by_name(proj_name)
                seq_name = cam_name_parts2[1]
                seq = gazu.shot.get_sequence_by_name(proj, seq_name)
                shot = gazu.shot.get_shot_by_name(seq, cam_name_parts2[2])
                shot_dict_list.append(shot)

        return shot_dict_list, custom_camera, all_assets

    def update_reference(self, asset, asset_name_rn, revision, output_type, task_type):
        new_revision_path = gazu.files.build_entity_output_file_path(asset, output_type, task_type,
                                                                      representation='fbx',
                                                                      revision=revision)
        new_file_path = new_revision_path + '.fbx'
        mc.file(new_file_path, loadReference=asset_name_rn)
