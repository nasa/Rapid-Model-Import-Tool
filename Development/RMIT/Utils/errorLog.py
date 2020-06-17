# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys
import os
import platform
import webbrowser
import time
import pathlib

def errorReport():
    try:
        app = QApplication([])
        ex = App()
        sys.exit(app.exec_())
        return True
    except:
        return False
#Function the locates blender error file if it exists. will be under the name untitled.crash
def b_crash():
    rTime = 0
    bCrash = ""
    for filename in os.listdir(os.environ['TMP']):
        if "crash" in str(filename) and "untitled" in str(filename) and os.path.getmtime(str(os.environ['TMP']) + "\\" + str(filename)) < (time.mktime(time.gmtime()) - 300):
            if os.path.getmtime(str(os.environ['TMP']) + "\\" + str(filename)) > rTime:
                rTime = os.path.getmtime(str(os.environ['TMP']) + "\\" + str(filename))
                bCrash =  str(os.environ['TMP']) + "\\" + str(filename)
    return bCrash

class App(QMainWindow):
#Setting up GUI features
    def __init__(self):
        super().__init__()
        self.title = 'RMIT Crash Report'
        self.left = 400
        self.top = 400
        self.width = 320
        self.height = 270
        self.initUI()
        if getattr(sys, 'frozen', False): #Frozen
            itLogo = str(pathlib.Path(__file__).parent.parent.parent / 'ITACL-Patch-Final.ico')
        else:                             #unFrozen
            itLogo = str(pathlib.Path(__file__).parent.parent.parent / 'ITACL-Patch-Final.ico')
        self.setWindowIcon(QtGui.QIcon(itLogo))
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        self.b = QPlainTextEdit(self)
#This never aligns well, as such writing to text box
        #self.b.label("Looks like there was a crash! Send feedback below:")
        self.b.insertPlainText("Looks like there was a crash! If serious please send feedback")
        self.b.move(10,30)
        self.b.resize(300,200)
        
        # Create a button in the window
        self.button = QPushButton('Send', self)
        self.button.move(20,235)
        self.button2 = QPushButton('Exit', self)
        self.button2.move(200,235)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.button2.clicked.connect(self.on_click2)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
        #Writing to log with system info and setting up parameters for emailing report
        f = open(os.path.dirname(__file__) + "/../RMIT.log","a+")
        f.write("---------ERROR REPORT---------"+"\r\n")
        uname = platform.uname()
        f.write("User input: " + self.b.toPlainText())
        f.write("System: " + uname.system + "\r\n")
        f.write("Node Name: " + uname.node + "\r\n")
        f.write("Version: " + uname.version  + "\r\n")
        f.write("Machine: " + uname.machine  + "\r\n")
        f.write("Processor: " + uname.processor + "\r\n")
        pythonVer = platform.python_version()
        f.write("Python version: "+ pythonVer + "\r\n")
        f.close()
        #Checking if there is a blender error report and if so notifying as such in log
        boutput = b_crash()
        if (boutput != ""):
            f.write("-----THERE WAS A BLENDER ERROR REPORT-----" + "\r\n" )
            f.write("Location of file: "+ boutput + "\r\n")
            f.write("If asked please send this file")


        recipient = 'ksc-dl-it-rmit@mail.nasa.gov'
        subject = 'RMIT bug report'
        #Ensuring that it does not exceed email character limit
        with open(os.path.dirname(__file__) + '/../RMIT.log', 'r') as b:
            body = b.read() 
        length = len(body)
        f.close()
        if (length > 23000):
            body = body[length-23000:length]
        #Replacing values with proper values for html
        body = body.replace(' ', '%20')
        body = body.replace('\n','%0D%0A')
        #Essentially having a browser open up an email, that automatically opens based on system
        webbrowser.open('mailto:?to=' + recipient + '&subject=' + subject + '&body=' + body + "&ni_email_cfg_file=.email.config", new=1)
        self.close()
    def on_click2(self):
        self.close()