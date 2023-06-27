#coding:utf8
import maya.cmds as mc

mc.evalDeferred('execfile("/home/rapa/maya/2020/scripts/PizzaMenu.py")')
#이 코드 라인은 Maya.cmds 모듈을 가져온 다음 evalDeferred 함수를 사용하여 "PizaMenu.py" 스크립트를 실행하는 "execfile" 명령을 실행합니다. evalDeferred 기능은 Maya가 로드를 마친 후 스크립트가 실행되도록 하여 시작 시 로드될 수 있는 다른 스크립트 또는 플러그인과의 충돌을 방지할 수 있습니다.
