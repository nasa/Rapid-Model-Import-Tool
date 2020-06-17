import win32gui, win32con, win32process
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE
import os

# ['D:\\Jose\\RMIT_REPO...ender.exe', '-P', 'D:\\Jose\\RMIT_REPO...Driver.py', '--', '-i', '//avr-e/Users/AVR/R...nlift.dae', '-e', 
# '//avr-e/Users/AVR/R...lift.gltf', '-d', '0.09', '-c', '0', '-l', 'False', ...]

args4Sub = ['D:\\Jose\\RMIT_REPO\\Experimentation\\Blender_Clients\\blender-2.81.0-8-28-19\\blender.exe', '-P', 
        'D:\\Jose\\RMIT_REPO\\Experimentation\\Blender_Plugin\\RMIT_BlenderDriver.py', '--', '-i', 
        '//avr-e/Users/AVR/RMIT_Models/Test_Models/inputs/Manlift.dae', '-e', 
        '//avr-e/Users/AVR/RMIT_Models/Test_Models/inputs/Manlift.gltf', '-d', '0.09', '-c', '0', '-l', 'False', 
        '-x', '.01']

args4OS = "D:/Jose/RMIT_REPO/Experimentation/Blender_Clients/blender-2.81.0-8-28-19/blender.exe -P 'D:/Jose/RMIT_REPO/Experimentation/Blender_Plugin/RMIT_BlenderDriver.py' -- -i '//avr-e/Users/AVR/RMIT_Models/Test_Models/inputs/Manlift.dae' -e '//avr-e/Users/AVR/RMIT_Models/Test_Models/inputs/Manlift.gltf' -d '0.09' -c '0' -l 'False' -x .01"

args4Window = ['D:\\Jose\\RMIT_REPO\\Experimentation\\Blender_Clients\\blender-2.81.0-8-28-19\\blender.exe', '-P', 
        'D:\\Jose\\RMIT_REPO\\Experimentation\\Blender_Plugin\\externalwindow.py']

#subTest = subprocess.call(['C:\\Windows\\System32\\cmd.exe'])
#osTest = os.system(args4Sub)
osTest = os.system(args4OS)
#extWindow = subprocess.run(args = args4Window)

'''
from PyQt5.QtWidgets import *
app = QApplication([])
button = QPushButton('Click')
def on_button_clicked():
    osTest = os.system(args4OS)
    windowList = []
    win32gui.EnumWindows(lambda hwnd, windowList: windowList.append((win32gui.GetWindowText(hwnd),hwnd)), windowList)
    cmdWindow = [i for i in windowList if "subprocess.exe" in i[0].lower()]
    win32gui.SetWindowPos(cmdWindow[0][1],win32con.HWND_TOPMOST,10,10,500,500,0) #100,100 is the size of the window

button.clicked.connect(on_button_clicked)
button.show()
app.exec_()
'''