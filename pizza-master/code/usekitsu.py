#coding:utf8
import gazu
import pprint as pp


class KitsuThings:
    """
    Kitsu에 접근하여 필요한 정보들을 추출하는 매서드
    """
    def __init__(self):
        pass

    def _get_frame_padding(self, shot):
        """
        샷에 프레임 정보가 있을 경우 패딩을 생성해주는 매서드

        프레임 정보가 없거나 패딩의 자릿수가 4보다 작으면 4자리로 생성한다.

        Args:
            shot(dict): 선택한 테스크 에셋이 캐스팅된 시퀀스 아래에 잇는 샷들 중 로드하길 원하는 샷

        Returns:
            str: 파일명 끝에 붙일 첫번째 패딩의 문자열
        """
        if shot['nb_frames'] and len(str(shot['nb_frames'])) > 4:
            padding_info = len(str(shot['nb_frames'])) - 2
        else:
            padding_info = 2
        padding = '_1' + ('0' * padding_info) + '1'

        return padding

    def get_undistortion_img(self, shot):
        """
        선택한 shot에 소속된 task type이 Matchmove고,
        ouput type이 UndistortionJpg인 output file을 찾는 매서드

        샷에 대한 패딩을 얻어(get_frame_padding) 첫번째 언디스토션 시퀀스 이미지의 경로를 추출한다.

        Args:
            shot(dict): 선택한 테스크 에셋이 캐스팅된 시퀀스 아래에 잇는 샷들 중 로드하길 원하는 샷

        Returns:
            str: 첫번째 언디스토션 이미지의 path
        """
        padding = self._get_frame_padding(shot)
        output_type = gazu.files.get_output_type_by_name('UndistortionJpg')
        task_type = gazu.task.get_task_type_by_name('Matchmove')
        undi_path = gazu.files.build_entity_output_file_path(shot['id'], output_type, task_type)
        full_path = undi_path + padding + '.jpg'

        return full_path

    def get_camera(self, shot):
        """
        shot에 소속된 task type이 Camera고, ouput type이 FBX인 output file을 찾는 매서드

        output file의 저장된 정보로부터 확장자를 추출하고,
        path와 이어붙여 샷에 해당하는 가상 카메라의 전체 경로를 구한다.

        Args:
            shot(dict): 선택한 테스크 에셋이 캐스팅된 시퀀스 아래에 잇는 샷들 중 로드하길 원하는 샷

        Returns:
            str: 카메라(fbx 등) 아웃풋 파일이 저장된 path
        """
        output_type = gazu.files.get_output_type_by_name('Alembic')     #### Alembic으로 바꿔야 함
        task_type = gazu.task.get_task_type_by_name('Camera')
        camera_files = gazu.files.get_last_output_files_for_entity(shot, output_type, task_type)
        camera_path = gazu.files.build_entity_output_file_path(shot, output_type, task_type)
        # full_path = camera_path + '.' + camera_files[0]['representation']     ### output file에 안넣어줘서...
        full_path = camera_path + '.abc'    ### abc로 바꿔야 함

        return full_path

    def get_asset_path(self, casting):
        """
        작업 에셋에 캐스팅된 에셋들의 최신 output file들의 패스 리스트를 추출하는 매서드

        캐스팅된 에셋 하나에 아웃풋 파일이 여러개일 경우를 가정한다.

        file_list: 아래의 딕셔너리를 모은 리스트
        file_dict: 캐스팅된 에셋에서 필요한 정보들(path, nb_elements)만 정제한 딕셔너리

        Args:
            casting(dict): 캐스팅된 에셋의 간략한 정보가 담긴 dict
                           keys - path, nb_elements

        Returns:
            dict: 아웃풋 파일들의 패스(확장자 포함), 개수가 담긴 dict
        """
        file_dict = {
            'name': "",
            'path': "",
            'nb_elements': 0,
        }
        asset = gazu.asset.get_asset(casting['asset_id'])
        task_type = gazu.task.get_task_type_by_name('Modeling')
        output_file_list = gazu.files.get_last_output_files_for_entity(asset, task_type=task_type)
        # 각 output file의 패스를 생성하고, 리스트에 append
        if len(output_file_list) != 0:
            out_file = output_file_list[0]
            out_path = gazu.files.build_entity_output_file_path(asset,
                                                                out_file['output_type_id'],
                                                                out_file['task_type_id'],
                                                                revision=out_file['revision'])
            if out_file['nb_elements'] > 1:
                # path = out_path + '_' + '[1-' + str(out_file['nb_elements']) + ']' + '.' + out_file['representation']
                path = out_path + '_' + '[1-' + str(out_file['nb_elements']) + '].fbx' ### output file에 안넣어줘서..2
            else:
                path = out_path + '.fbx'
            file_dict['name'] = asset['name']
            file_dict['path'] = path
            file_dict['nb_elements'] = out_file['nb_elements']

        return file_dict
