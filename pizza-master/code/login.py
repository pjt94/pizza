# coding=utf-8

import os
import json
import gazu
from logger import Logger


class LogIn(object):
    """
    class LogIn은 사용자가 Kitsu에 로그인 또는 로그아웃 하는 전반적인 과정을 저장하고, 자동화를 돕습니다.
    """
    def __init__(self):
        """
        Attributes:
            - _host (str): 사용자가 연결된 호스트의 URL입니다.
            - _user (dict): 로그인한 사용자에 대한 정보가 들어 있는 사전입니다.
            - _user_id (str): 로그인한 사용자의 ID입니다.
            - _user_pw (str): 로그인한 사용자의 암호입니다.
            - _valid_host (bool): 호스트에 대한 연결이 유효한지 여부를 나타내는 플래그입니다.
            - _valid_user (bool): 로그인 자격 증명이 유효한지 여부를 나타내는 플래그입니다.
            - _auto_login (bool): 자동 로그인이 선택되었는지 확인하는 플래그입니다.
            - dir_path (str): 로그 파일이 저장될 디렉터리의 경로입니다.
            - user_path (str): 사용자의 인증 정보가 저장된 JSON 파일의 경로입니다.

        Methods:
            - __init__(): Login 개체를 초기화합니다.
            - connect_host(try_host): 지정한 호스트에 연결하고 그에 따라 _host 및 _valid_host 특성을 설정합니다.
            - log_in(try_id, try_pw): 지정된 사용자 ID와 암호를 사용하여 현재 연결된 호스트에 로그인하고,
                                     그에 따라 _user, _user_id, _user_pw 및 _valid_user 특성을 설정합니다.
            - log_out(): 현재 로그인한 사용자를 로그아웃합니다.
            - access_setting(): 사용자 구성 디렉터리 및 user.json 파일이 있는지 확인하고 없으면 생성합니다.
            - load_setting(): user.json 파일에서 사용자 설정을 로드하고 그에 따라
                            _host, _user, _user_id 및 _user_pw 특성을 설정합니다.
            - save_setting(): 현재 사용자 설정을 user.json 파일에 저장합니다.
            - reset_setting(): 현재 사용자 설정을 기본값으로 재설정합니다.
        """
        self._host = None
        self._user = None
        self._user_id = None
        self._user_pw = None
        self._valid_host = False
        self._valid_user = False
        self._auto_login = False

        self.logging = Logger()
        self.dir_path = os.path.dirname(os.path.abspath(__file__))+'/.config'
        self.user_path = os.path.join(self.dir_path, 'user.json')
        self.logging.set_logger()

    @property
    def valid_host(self):
        """
        현재 호스트 연결의 유효성을 반환하는 속성입니다.
        """
        return self._valid_host

    @valid_host.setter
    def valid_host(self, value):
        self._valid_host = value

    @property
    def valid_user(self):
        """
        현재 사용자 로그인의 유효성을 반환하는 속성입니다.
        """
        return self._valid_user

    @valid_user.setter
    def valid_user(self, value):
        self._valid_user = value

    @property
    def host(self):
        """
        현재 호스트의 URL을 반환하는 속성입니다.
        """
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def user(self):
        """
        현재 로그인한 사용자의 사용자 사전을 반환합니다.
        """
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def user_id(self):
        """
        현재 로그인한 사용자의 id를 반환합니다.
        """
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def user_pw(self):
        """
        현재 로그인한 사용자의 password를 반환합니다.
        """
        return self._user_pw

    @user_pw.setter
    def user_pw(self, value):
        self._user_pw = value

    @property
    def auto_login(self):
        """
        현재 로그인한 사용자가 자동 로그인을 선택하였는지의 여부를 반환합니다.
        """
        return self._auto_login

    @auto_login.setter
    def auto_login(self, value):
        self._auto_login = value

    def connect_host(self):
        """
        지정된 호스트 URL에 연결을 시도하고 인증 설정에 저장합니다.

        Returns:
            bool : 연결이 성공하면 True이고, 그렇지 않으면 False입니다.

        Raises:
            ValueError: 호스트 URL이 잘못된 경우.
        """
        gazu.set_host(self.host)

        if not gazu.client.host_is_valid():
            self.logging.failed_log()
            raise ValueError('에러 메시지 : 호스트 URL이 잘못되었습니다.')

        self.valid_host = True
        self.logging.connect_log(self.host)

        return True

    def log_in(self):
        """
        제공된 사용자 ID와 암호로 사용자를 로그인합니다.

        Returns:
            bool : 로그인이 성공하면 True이고, 그렇지 않으면 False입니다.

        Raises:
            SystemError: 자격 증명이 올바르지 않은 경우
            ValueError: 호스트가 연결되어 있지 않은 경우
        """
        try:
            log_in = gazu.log_in(self.user_id, self.user_pw)
        except gazu.AuthFailedException:
            self.logging.failed_log()
            raise ValueError('에러 메시지 : 사용자 ID 또는 암호가 잘못 입력되었습니다.')

        self.user = log_in['user']
        self.valid_user = True
        self.save_setting()
        self.logging.enter_log(self.user["full_name"])

        return True, self.user["full_name"]

    def log_out(self):
        """
        현재 사용자를 로그아웃합니다.

        Returns:
            bool: 로그아웃이 성공하면 True이고, 그렇지 않으면 False입니다.
        """
        # gazu.log_out()
        self.user = None
        self.reset_setting()
        self.logging.logout_log()

        return True

    def access_setting(self):
        """
        인증 디렉터리에 대한 액세스 설정을 확인하고 존재하지 않는 경우 user.json을 생성합니다.

        Returns:
            bool: 액세스 검사가 성공하면 True이고, 그렇지 않으면 False입니다.

        Raises:
            ValueError: OS 오류로 인해 dir_path에서 지정한 디렉토리를 생성할 수 없거나 user.json 파일을 생성할 수 없는 경우.
        """
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise ValueError("에러 메시지 : 디렉터리를 만들지 못했습니다.")

        if not os.path.exists(self.user_path):
            try:
                self.reset_setting()
            except OSError:
                raise ValueError("에러 메시지 : user.json 파일을 생성하지 못했습니다.")

        return True

    def load_setting(self):
        """
        user.json 파일에서 인증 설정을 load하고 필요한 경우 호스트에 연결합니다.

        Returns:

        """
        user_dict = {}
        if os.path.exists(self.user_path):
            with open(self.user_path, 'r') as json_file:
                user_dict = json.load(json_file)
        else:
            self.access_setting()
            with open(self.user_path, 'r') as json_file:
                user_dict = json.load(json_file)

        return user_dict

    def save_setting(self):
        """
        현재 인증 설정을 user.json 파일에 저장합니다.

        Returns:

        """
        user_dict = {
            'host': self.host,
            'user_id': self.user_id,
            'user_pw': self.user_pw,
            'valid_host': self.valid_host,
            'valid_user': self.valid_user,
            'auto_login': self.auto_login
        }
        with open(self.user_path, 'w') as json_file:
            json.dump(user_dict, json_file)

        return user_dict

    def reset_setting(self):
        """
        인증 설정을 기본값으로 재설정합니다.
        """
        self.host = ''
        self.user_id = ''
        self.user_pw = ''
        self.valid_host = False
        self.valid_user = False
        self.auto_login = False
        self.save_setting()
