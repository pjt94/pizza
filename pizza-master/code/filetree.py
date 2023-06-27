# coding=utf-8

import os
import gazu


def update_filetree(mountpoint, root):
    """
    파일 트리를 업데이트하는 매서드

    Args:
        mountpoint(str/path): 폴더 트리를 생성할 위치의 전체 경로
        root(str/folder name): 폴더 트리를 생성할 mountpoint의 자식 폴더 이름
    """
    gazu.client.set_host("http://192.168.3.116/api")
    gazu.log_in("pipeline@rapa.org", "netflixacademy")

    tree = {
        "working": {
            "mountpoint": mountpoint,
            "root": root,
            "folder_path": {
                "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/working/v<Revision>",
                "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/working/v<Revision>",
                "style": "lowercase"
            },
            "file_name": {
                "shot": "<Project>_<Sequence>_<Shot>_<TaskType>_<Revision>",
                "asset": "<Project>_<AssetType>_<Asset>_<TaskType>_<Revision>",
                "style": "lowercase"
            }
        },
        "output": {
            "mountpoint": mountpoint,
            "root": root,
            "folder_path": {
                "shot": "<Project>/shots/<Sequence>/<Shot>/<TaskType>/output/<OutputType>/v<Revision>",
                "asset": "<Project>/assets/<AssetType>/<Asset>/<TaskType>/output/<OutputType>/v<Revision>",
                "style": "lowercase"
            },
            "file_name": {
                "shot": "<Project>_<Sequence>_<Shot>_<OutputType>_v<Revision>",
                "asset": "<Project>_<AssetType>_<Asset>_<OutputType>_v<Revision>",
                "style": "lowercase"
            }
        }
    }
    project = gazu.project.get_project_by_name('Project2')
    gazu.files.update_project_file_tree(project, tree)


def _make_folder_tree(path):
    """
    working file, output file을 save/export 하기 위한 실제 폴더를 생성하는 매서드

    폴더가 이미 있으면 생성하지 않는다.

    Args:
        path(str): 파일명을 제외한 폴더 경로
    """

    if os.path.exists(path) is False:
        os.makedirs(path)
    else:
        raise SystemError("폴더가 이미 존재합니다.")


update_filetree('/mnt/project/pizza', 'kitsu')
