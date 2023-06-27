#coding:utf-8

"""

** API 소개 **

마야를 사용하는 레이아웃 팀을 위한 api이고, Gazu를 활용하여 Asset 및 shot의 정보를 가져와 사용하는 것을 목표로 합니다.
샷의 카메라와 캐스팅 정보를 수집하고, 다음 정보를 활용하여 작업 파일과 출력 파일을 퍼블리싱하는 역할을 합니다.
마야에 내장된 스크립트를 클릭하면 모든 에셋, 카메라, 언디스토션 이미지를 불러오거나 작업물을 저장할 수 있습니다.
Kitsu에서 기록된 정보를 가져와 마야에서 Load/Save 및 작업을 진행합니다.
파일 경로를 추적하여 작업 파일과 아웃풋 파일, 프리뷰 영상을 실제 폴더 트리에 저장합니다.
Kitsu에 퍼블리시한 후 파일들을 업로드합니다.
구버전 작업 시 최신파일이 존재하는 것을 표시해 줍니다.



--------------------------------------------------------------------------------------------


Team Pizza License


Original work Copyright (c) 2023 Team Pizza


--------------------------------------------------------------------------------------------


이에 따라 사본을 입수하는 모든 사람에게 무료로 허가가 부여됩니다.
이 소프트웨어 및 관련 문서 파일("소프트웨어")을 처리합니다.
사용, 복사, 수정, 병합, 게시, 배포, 하위 라이센스 및/또는 판매
본 소프트웨어의 사본 및 본 소프트웨어를 사용하는 사람을 허용합니다.

다음 조건에 따라 제공됩니다:
위의 저작권 고지 및 이 허가 고지는 다음에 포함되어야 합니다.

본 소프트웨어 또는 사용 또는 기타 거래와 관련되거나 이와 관련하여 어떠한 경우에도
저작자 또는 저작권 소유자는 계약상의 행위, 불법행위, 그 밖의 행위에 관계없이 발생하는
모든 청구, 손해 또는 기타에 대해 책임을 지지 않습니다.


--------------------------------------------------------------------------------------------


**class : SetThings**

위 클래스는 샷에 있는 레이아웃 팀에 주어진 테스크에 캐스팅된 에셋의 경로를 추출하고, 마야에 import 하며(미구현)
폴더 트리에 저장된 working, output, preview 파일을 Kitsu에 퍼블리싱하는 class이다.

    ** def __init__: **
        프로덕션 데이터베이스에 대한 연결을 설정하고, 사용자 로그인 후 사용자 정의 클래스인 PublishThings의 인스턴스를 생성한다.

        .. doctest::
            None

        Output >>
            self._project = project의 dict
            self._shot = shot의 dict
            self._task = task의 dict
            Dict Available Data : https://gazu.cg-wire.com/data.html

    ** def project(self, value): **
        테스크가 있는 프로젝트를 선택하는 세터

        .. doctest::
            a = SetThings()
            a.project = 'NetfilxAcademy'

        Output >>
            project_dict

    ** def update_filetree(mountpoint, root): **
        지정된 mountpoint 및 root로 프로젝트의 파일 트리를 업데이트한다.

        .. doctest::
            a = SetThings()
            a.update_filetree('/home/rapa/mnt', 'test')

        Output >>
            shot_path = "/home/pizza/kitsu/<Project>/shots/<Sequence>/<Shot>/<TaskType>... 생성

    ** def select_task(self, num=0): **
        user에 assign되어 있으며 상태가 Todo인 task를 선택하고
        선택한 task에 기반하여 shot을 추출해 저장한다.
        num에 원하는 테스크의 인덱스 번호를 입력한다.

        .. doctest::
            a = SetThings()
            a.select_task(1)

        Output >>
            self._task = task_dict
            self._shot = shot_dict

    ** def _get_kitsu_path(self, casting): **
        샷에 캐스팅된 에셋의 최신 output file들의 패스 리스트를 추출하는 매서드

        .. doctest::
            이 매서드는 외부에서 호출할 수 없다.

        Output >>
            /home/pizza/<Project>/shots/<Sequence>/<Shot>/<TaskType>/output/<OutputType>/v<Revision>/pizza.fbx

    ** def run_program(comment): **
        api의 주요 기능을 실행한다.

        .. doctest::
            a = SetThings()
            a.run_program("This is like commit")

        Output >>
            Kitsu에 데이터 퍼블리싱
            폴더 트리에 working, output, preview 파일 저장하고 Kitsu에 업로드



**class : PublishThings**

위 클래스는 working file과 output file을 저장하고 가져오기 위한 실제 폴더를 생성하며, Kitsu에 파일정보를 기록한 뒤 업로드하는 class 이다.

    ** def __init__: **
        software 및 output type은 class에 대한 생성자 메서드를 정의하며, 이를 초기화 합니다.

        .. doctest::
            None

            Output >>
            self._software는 software의 이름값을 가진다.
            self._output_type은 output_type의 이름값을 가진다.

    ** def _select_software(self, num=0): **
        working file을 생성하기 위해 소프트웨어를 저장합니다.
        software_list를 출력하여 원하는 값을 반환한다.

        .. doctest::
            이 매서드는 외부에서 호출할 수 없다.

            Output >>
            software_list[num] = {"name" : "None",
                                    "key": "value" }

    ** def _select_output_type(self, shot, num=0): **
        output 파일을 생성하기 위하여 output types의 entity의 정보를 사용하여 초기 output type을 설정한다.
        output_type_list를 출력하여 원하는 값을 반환한다.

        .. doctest::
            이 매서드는 외부에서 호출할 수 없다.

            Output >>
            output_type_list[num] = {"name" : "main",
                                    "output_type": "value" }

    ** def publish_file_data(self, shot, task, comment): **
        작업 파일과 출력 파일을 만들고 각 파일의 경로를 구축한다.
        shot, task, comment의 세 가지 인수를 사용하고, output_file, output_path, working_file, working_path 네 가지 값을 반환한다.

        주어진 task 및 shot 을 기반으로 작업 파일과 출력 파일을 만들어 먼저 task에 대한 기존 작업 파일이 있는지 확인하고, 없으면 새 작업 파일을 생성한다.
        그 다음 지정된 shot 및 작업에 대한 기존 출력 파일이 있는지 확인하고, 없으면 새 출력 파일을 생성한다.

        .. doctest::
            이 매서드는 모듈의 SetThings 클래스 내에서 사용된다.
            a = PublishThings()
            a.publish_file_data(self.shot, self.task, self.comment)

           Output >>
            working_file = {"working_file_id": "1234"}
            working_path는 다음과 같이 출력됩니다 : "/path/to/working/file.v001.ma"
            output_file = {"output_file_id": "5678"}
            output_path는 다음과 같이 출력됩니다 : "/path/to/output/file.v001.exr"

    ** def _make_folder_tree(self, path): **
        working file, output file을 저장 및 내보내기 위한 실제 폴더를 생성한다.

        .. doctest::
            이 매서드는 외부에서 호출할 수 없다.

            Output >>
            /mnt/project/pizza/<project_name>/<asset>/<asset_Type>/<Task>/<Task_Type>/<output>
            파일트리 구조에 맞게 폴더가 생성됩니다.

    **def _upload_files(self, task, path, comment, file_type):**
        작업한 working file과 task에 대한 prewiew file을 Kitsu에 업로드한다.
        working file의 경로와 software를 전체 경로로 지정하고,
        output file의 경로와 확장자명을 전체 경로로 지정한다.
        지정된 output file의 경로를 통해 preview file을 업로드한다.

        .. doctest::
            이 매서드는 외부에서 호출할 수 없다.

            Output >>
                작업한 working파일과 Task에 대한 preview file을 Kitsu에 업로드

    **def save_publish_real_data(self, shot, task, comment):**
        경로에 맞추어 폴더 트리를 생성하고, 파일을 저장한 후 working file과 preview file을 Kitsu에 업로드한다.
        working file, path 및 output file, path의 정보를 불러온 후,
        각 build된 경로에 파일명을 잘라내는 경로를 지정하고 이에 대한 폴더를 생성
        생성된 폴더에 따른 working file, output file 업로드

        .. doctest::
            이 매서드는 모듈의 SetThings 클래스 내에서 사용된다.
            a = PublishThings()
            a.save_publish_real_data(self.shot, self.task, self.comment)

            Output >>
                폴더 트리를 생성하고 working, output, preview 다음 파일을 저장 후 Kitsu에 업로드





# from .kitsumaya import SetThings as sett
# from .publish import PublishThings as pub
# from .usemaya import MayaThings as mayat

# import sys
# sys.path.append('/home/rapa/TEST/git/pizza/ahyeon/MayaGazuAPI')
# import MayaGazuAPI
# reload(MayaGazuAPI)


# # Maya Script Editor


"""
