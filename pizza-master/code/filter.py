# coding:utf8

import gazu
import pprint as pp


class Filter:
    """
    사용자의 선택에 따라 테스크, 에셋, 샷 등의 목록을 필터링하고, 필요한 정보를 정제해주는 클래스
    """
    def __init__(self):
        pass

    def _get_information_dict(self, task):
        """
        각 task에서 필터링에 필요한 정보들을 추출하여 딕셔너리에 추가하는 매서드

        collect_info_task 에서 사용된다.

        Args:
            task(dict): 유저에게 할당된 task

        Returns:
            dict: task에서 필요한 정보만 추출하여 모은 딕셔너리
            str: task asset이 속한 시퀀스의 이름
        """
        task_info = dict()
        task_info['project_name'] = task['project_name']
        if task['due_date']:
            task_info['due_date'] = task['due_date'].split('T')[0]
        else:
            task_info['due_date'] = task['due_date']
        task_info['description'] = task['description']
        task_info['last_comment'] = task['last_comment']
        # task asset이 사용되는 seq 구하기
        asset = gazu.asset.get_asset(task['entity_id'])
        shots = gazu.casting.get_asset_cast_in(asset)
        shot = gazu.shot.get_shot(shots[0]['shot_id'])
        seq = gazu.shot.get_sequence_from_shot(shot)
        task_info['sequence_name'] = seq['name']
        task_info['asset_name'] = asset['name']

        return task_info

    def collect_info_task(self):
        """
        필터링에 필요한 프로젝트 이름, 시퀀스 이름을 proj_set, seq_set에 중복 없이 모으고,
        각 task의 정보를 모아 반환하는 매서드

        Returns:
            list(task_info_list): task의 정보들 중 사용자에게 노출할 정보들만 모은 딕셔너리의 집합
                                  keys - project_name, due_date, description, last_comment, sequence_name
            list(task_list): 사용자에게 assign되었고, task status가 _Todo_ 또는 WIP인  모든 task 딕셔너리의 집합
            list(proj_set): 각 task가 속한 프로젝트의 이름들을 중복없이 모든 리스트
        """
        proj_list = []
        task_list = []
        task_info_list = []
        tmp_task_list = gazu.user.all_tasks_to_do()
        for index, task in enumerate(tmp_task_list):
            if task['task_type_name'] == 'LayoutAsset':
                proj_list.append(task['project_name'])
                task_info = self._get_information_dict(task)
                task_info_list.append(task_info)
                task_list.append(task)
        proj_set = list(set(proj_list))

        return task_info_list, task_list, proj_set

    def _get_img_cam_info_dict_list(self, shot, output_type, task_type, p=None):
        """
       리스트에 아웃풋 파일(언디스토션 이미지, camera)의 정보 중 필요한 정보를 선별하여 담는 매서드

        Args:
            shot(dict): 언디스토션 이미지, 카메라의 아웃풋 파일이 속한 shot
            output_type(dict): 아웃풋 파일이 속한 아웃풋 타입(jpg, abc, fbx)
            task_type(dict): 아웃풋 파일이 속한 테스크 타입(Camera, Matchmove...)

        Returns:
            list: output file의 모델 딕셔너리에서 필요한 정보들만 담은 리스트의 집합
                 keys - output_type_name, frame_range, output_name, comment, description, shot_name
        """
        info_list = []
        output_list_tmp = gazu.files.get_last_output_files_for_entity(shot['shot_id'], output_type, task_type)
        output_list_tmp2 = output_list_tmp
        output_list = []
        if len(output_list_tmp) > 1:
            for index in range(len(output_list_tmp)):
                del output_list_tmp2[index]
                if len(output_list_tmp2) == 0:
                    break
                for index2 in range(len(output_list_tmp2)):
                    if output_list_tmp[index]['source_file_id'] == output_list_tmp2[index2]['source_file_id']:
                        break
                    else:
                        output_list.append(output_list_tmp[index])
        else:
            output_list = output_list_tmp

        output_dict = {
            'output_type_name': None,
            'frame_range': None,
            'output_name': None,
            'comment': None,
            'description': None,
            'shot_name': None
        }
        output_dict['output_type_name'] = output_type['name']
        if len(output_list) is 0 and p:
            print("shot에 {0} output file이 존재하지 않습니다. Seq: {1}, Shot: {2}".format(output_type['name'],
                                                                                 shot['sequence_name'],
                                                                                 shot['shot_name']))
            info_list.append(output_dict)
        for output in output_list:
            shot = gazu.shot.get_shot(output['entity_id'])
            output_dict['frame_range'] = shot['nb_frames']
            output_dict['output_name'] = output['name']
            output_dict['comment'] = output['comment']
            output_dict['description'] = output['description']
            output_dict['shot_name'] = shot['name']
            info_list.append(output_dict)

        return info_list

    def _cast_dict_append(self, cast, output_type, asset, task_type):
        """
        캐스팅된 에셋의 정보 중 필요한 정보를 선별하여 딕셔너리에 담는 매서드

        Args:
            cast: 캐스팅된 에셋의 간략한 캐스팅 정보
            output_type(list): 에셋에서 쓰이는 모든 아웃풋 타입 딕셔너리의 집합
            asset(dict): 캐스팅된 에셋의 딕셔너리
            task_type(dict): 아웃풋 파일 생성에 필요한 Modeling task type

        Return:
            dict: 캐스팅된 에셋의 딕셔너리에서 필요한 정보들만 담은 리스트의 집합
                  keys - asset_name, asset_type_name, nb_occurences, output, description
                  output keys - output_type, revision
        """
        output_list = []
        output_dict = dict()
        for item in output_type:
            is_output = gazu.files.get_last_output_files_for_entity(asset, task_type=task_type)
            if len(is_output) != 0:
                revision = gazu.files.get_last_entity_output_revision(asset, item, task_type)
                output_dict['output_type'] = item['name']
                output_dict['revision'] = revision
                output_list.append(output_dict)
        casting_dict = {'asset_name': asset['name'],
                        'description': asset['description'],
                        'asset_type_name': asset['asset_type_name'],
                        'nb_occurences': cast['nb_occurences'],
                        'output': output_list,
                        }

        return casting_dict

    def _collect_info_casting(self, task):
        """
        선택한 layout task가 속한 작업 asset에 casting된 에셋들의 정보 중 필요한 내용을 추출하여 저장하는 매서드

        output file의 정보를 수집하기 위해 모델링, 매치무브, 카메라의 테스크 타입을 구한 뒤,
        작업 asset에 캐스팅된 다른 에셋들의 정보를 수집하여 저장한다.(_cast_dict_append)
        그리고 작업 asset이 cast in 된 샷들에서 언디스토션 이미지와 camera output의 정보 중 필요한 내용을 추출한다.(_get_img_cam_info_dict_list)

        Args:
            task(dict): 선택한 task의 딕셔너리

        Returns:
            list(casting_info_list): 캐스팅된 에셋들의 정보를 담은 리스트의 집합
                                     keys - asset_name, asset_type_name, nb_occurences, output, description
                                     output keys - output_type, revision
            list(undi_info_list): task asset이 캐스팅된 샷의 언디스토션 이미지 정보를 담은 리스트의 집합
                                  keys - output_type_name, frame_range, output_name, comment, description, shot_name
            list(camera_info_list): task asset이 캐스팅된 샷의 카메라 정보를 담은 리스트의 집합
                                    keys - output_type_name, frame_range, output_name, comment, description, shot_name
        """
        casting_info_list = []
        undi_info_list = []
        camera_info_list = []
        task_type = gazu.task.get_task_type_by_name('Modeling')
        task_match = gazu.task.get_task_type_by_name('Matchmove')
        task_cam = gazu.task.get_task_type_by_name('Camera')
        asset = gazu.entity.get_entity(task['entity_id'])
        shot_list = gazu.casting.get_asset_cast_in(asset)
        all_casting_list = gazu.casting.get_asset_casting(asset)
        for cast in all_casting_list:
            casted_asset = gazu.asset.get_asset(cast['asset_id'])
            output_types = gazu.files.all_output_types_for_entity(casted_asset)
            casting_dict = self._cast_dict_append(cast, output_types, casted_asset, task_type)
            casting_info_list.append(casting_dict)
        for shot in shot_list:
            jpgs = gazu.files.get_output_type_by_name('UndistortionJpg')
            abc = gazu.files.get_output_type_by_name('Alembic')     ##### Alembic으로 바꿔야 함
            if self._get_img_cam_info_dict_list(shot, jpgs, task_match):
                undi_info_list.append(self._get_img_cam_info_dict_list(shot, jpgs, task_match, 1))
            if self._get_img_cam_info_dict_list(shot, abc, task_cam):
                camera_info_list.append(self._get_img_cam_info_dict_list(shot, abc, task_cam, 1))

        return casting_info_list, undi_info_list, camera_info_list

    def _filter_info(self, proj_num=0):
        """
        유저가 필터링을 했는지 판별하여 해당하는 task들만 노출하는 매서드
        유저가 클릭한 테스크의 dict를 저장한다

        Args:
            proj_num: 선택한 프로젝트의 인덱스 번호. 0은 All을 뜻한다
            seq_num: 선택한 시퀀스의 인덱스 번호. 0은 All을 뜻한다

        Returns:
            list: 필터링된 task dict의 집합
            list: 필터링된 task 정보 중 필요한 내용만 담긴 dict의 집합
        """
        task_info_list, task_list, proj_set = self.collect_info_task()
        filtered_task_list = []
        filtered_task_info_list = []

        proj_set.sort()

        # 프로젝트 이름 필터링
        if proj_num == 0 or proj_num == None:
            return task_list, task_info_list
        else:
            proj = proj_set[proj_num-1]
            for index, task in enumerate(task_list):
                if task['project_name'] == proj:
                    filtered_task_list.append(task)
                    filtered_task_info_list.append(task_info_list[index])
            return filtered_task_list, filtered_task_info_list

    def select_task(self, proj_num=0, task_num=None, clicked_asset=None):
        """
        필터링을 마친 뒤 선택한 테스크에 대한 정보를 노출하는 매서드

        Args:
            proj_num: 선택한 프로젝트의 인덱스 번호. 0은 All을 뜻한다
            task_num: 선택한 테스크의 인덱스 번호. 테스크 선택 전에는 None
            clicked_asset: 선택한 테스크가 속한 에셋의 이름

        Returns:
            dict or list(task): 선택한 task의 딕셔너리 또는 모든 task 딕셔너리의 집합(선택 전)
            list(task_info): 선택한 task의 정제된 정보를 담은 딕셔너리의 집합
            list(casting_info_list): 캐스팅된 에셋의 정보가 담긴 딕셔너리의 집합
            list(undi_info_list): 언디스토션 이미지의 정보가 담긴 딕셔너리의 집합
            list(camera_info_list): 카메라 파일의 정보가 담긴 딕셔너리의 집합
        """
        casting_info_list = None
        undi_info_list = None
        camera_info_list = None
        final_task_list, final_task_info_list = self._filter_info(proj_num)
        if task_num is None:
            task = final_task_list
            task_info = final_task_info_list
        else:
            asset_name = clicked_asset.split('\n')[1]
            for index, task_item in enumerate(final_task_list):
                asset = gazu.asset.get_asset(task_item['entity_id'])
                if asset_name == asset['name']:
                    task = task_item
                    task_info = final_task_info_list[index]
                    casting_info_list, undi_info_list, camera_info_list = self._collect_info_casting(task)
        return task, task_info, casting_info_list, undi_info_list, camera_info_list
