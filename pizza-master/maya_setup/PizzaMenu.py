import maya.cmds as mc
import sys

sys.path.append('/home/rapa/TEST/git/pizza/python')

if mc.menu('pizzaMenu',exists=True):
    mc.menu('pizzaMenu', e=True, dai=True)
else:
    mc.setParent('MayaWindow')
    mc.menu('pizzaMenu', l="Pizza", p='MayaWindow', to=True)
    
mc.setParent(menu=True)
    
mc.menuItem(l="Pizza", sm=True, to=True)
mc.menuItem(l="Pizza_API", c="import PizzaMaya.ui.UI_controller; app = UI_controller.MainWindow();", ann="Open the Pizza.", image="pizza_API.jpg")
mc.setParent(menu=True)

shelf_name = "pizza"
mc.shelfLayout(shelf_name, p="ShelfLayout")
mc.shelfButton(
    label="Pizza_API",
    image="pizza_API.png",
    command="import PizzaMaya.ui.UI_controller; myapp = PizzaMaya.ui.UI_controller.MainWindow();", 
    parent=shelf_name
)
