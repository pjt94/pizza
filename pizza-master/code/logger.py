#coding:utf-8

import os
import logging


class Logger:
    """
    class Logger는 로깅을 설정하고 관리하는 방법을 제공합니다.
    호스트에 대한 성공적인 연결, 로그인 시도, 파일 생성 및 로드와 같은 응용 프로그램에서 사용할 수 있습니다.

    Attributes:
    - logger (Logger): 인증 이벤트를 기록하는 Logger 클래스의 인스턴스.
    - log (logging.Logger): 메시지를 로깅하는 데 사용되는 로거 객체입니다.

    Methods:
    - __init__(): Logger 객체를 초기화합니다.
    - set_logger(): Logger 객체를 설정하고 여기에 핸들러를 추가합니다.
    - connect_log(host_url): 지정한 호스트에 대한 연결이 성공했음을 나타내는 메시지를 기록합니다.
    - enter_log(user_name): 지정한 이름의 사용자가 성공적으로 로그인했음을 나타내는 메시지를 기록합니다.
    - create_working_file_log(user_name, working_file): 지정한 이름을 가진 사용자가 지정한 위치에
                                                        Maya 파일을 생성했음을 나타내는 메시지를 기록합니다.
    - load_output_file_log(user_name, output_file_path): 지정한 이름을 가진 사용자가 지정한 위치에서
                                                        출력 파일을 로드했음을 나타내는 메시지를 기록합니다.
    """

    def __init__(self):
        """
        Logger 객체를 초기화합니다.

        Raises:
            ValueError: 디렉터리 생성이 실패할 경우
        """
        self.log = None
        self.dir_path = os.path.dirname(os.path.abspath(__file__))+'/.config'
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError("에러 메시지 : 디렉터리를 만들지 못했습니다.")
        self.set_logger()

    def set_logger(self):
        """
        logger instance에 stream handler 및 file handler를 추가하여 피자 응용 프로그램에 대한 로깅 구성을 설정합니다.
        INFO level에서 10개의 테스트 메시지를 기록합니다.
        """
        self.log = logging.getLogger('pizza')

        if len(self.log.handlers) == 0:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
            self.log.setLevel(logging.DEBUG)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(logging.INFO)
            self.log.addHandler(stream_handler)

            file_handler = logging.FileHandler(os.path.join(self.dir_path, 'pizza_test.log'))
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.log.addHandler(file_handler)

    def connect_log(self, host_url):
        """
        DEBUG level에서 지정된 'host_url'에 대한 성공적인 연결 및 실패를 기록합니다.

        Args:
            host_url(str): Kitsu 호스트의 주소
        """
        if host_url:
            self.log.debug("연결에 성공하였습니다. {}".format(host_url))

    def enter_log(self, user_name):
        """
        DEBUG level에서 지정된 'user_name'을 사용하여 사용자의 성공적인 로그인을 기록합니다.

        Args:
            user_name(str): 기록된 사용자의 이름
        """
        if user_name:
            self.log.debug("{}: Log-in Succeed".format(user_name))

    def failed_log(self):
        self.log.debug("Failed Connection")

    def logout_log(self):
        self.log.debug("Logout Succeed")

    def load_file_log(self, file_name):
        """
        파일을 만든 사용자의 이름 및 파일 경로와 함께 DEBUG level에서 Maya 파일을 생성한 것을 기록합니다.
        파일이 없으면 경고 메시지를 기록합니다.

        Args:
            user_name(str): 로그인한 사용자의 이름
            working_file(str): working file이 저장될 path str
        """
        if type(file_name) == set:
            return self.log.debug("{0}번째 에셋이 로드되었습니다.".format(str(file_name)))
        else:
            return self.log.debug("로드된 에셋 이름: {0}".format(file_name))

    def save_output_file_log(self, file_name):
        """
        파일을 로드한 사용자의 이름과 파일 경로와 함께 DEBUG 수준의 출력 파일 로드를 기록합니다.

        Args:
            user_name(str): 로그인한 사용자의 이름
            output_file_path(str): output file이 저장될 path str

        Returns:
            log: Debug 레벨의 로그 메세지
        """
        return self.log.debug("{} load working / output file".format(file_name))
