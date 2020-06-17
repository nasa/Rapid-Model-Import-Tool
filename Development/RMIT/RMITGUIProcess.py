# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui, QtTest
from PyQt5.QtCore import Qt
import os
import subprocess
import pathlib
import sys
import time
import configparser
from win32 import win32gui
try:
    import lib.Utils.errorLog as err
except Exception:
    import Utils.errorLog as err

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(
            context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

if sys.platform == "win32":
    import ctypes
    ctypes.windll.kernel32.SetDllDirectoryA(None)

class Ui_MainWindow(QtWidgets.QWidget):
    """
    | **Main App Class:**
    | Sets all the defaults for the GUI.
    | The application consists of several core components.

    - Decimation Options.
    - File Picking Dialog
    - File Destination Dialog [Default to input directory]
    - Processing button.

    | **Usage guide**:
    - Pick a file for processing
    - Pick a folder for output
    - Optional Headless and Dense removal
    - Choose a decimation level.
    - Click on Process.
    """

    def setupUi(self, MainWindow):
        # Main window declaration
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(400, 186)

        # Defaults for widget. Such as decimations and filepath
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        #Need to disable some windows if unit testing
        self.unittesting = False

        #Text options
        self.filePathIn = ''
        self.filePathOut = ''
        self.filename = []
        #Headless
        self.headless = False

        #Decimation
        self.decimate = False
        self.decimateAmount = 0.0
        #Cleanup
        self.cleanUp = False
        self.cleanUpPercent = 0.5
        #Split meshes
        self.loose = False
        #Remove hidden
        self.hidden = False
        #Extract function/Flatten
        self.delete = False
        #Center
        self.center = False
        #Merge Meshes
        self.merge = False

        # Grid layout declerations
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        
        '''
        Menu text and file bar
        '''

        #Main text in GUI
        self.processModel = QtWidgets.QLabel(self.centralwidget)
        self.processModel.setObjectName(_fromUtf8("processModel"))
        self.gridLayout.addWidget(
            self.processModel, 0, 0, 3, 4)

        # Main menu menu bar and file
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 462, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))

        # Main menu status bar
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))

        # Main menu close
        MainWindow.setStatusBar(self.statusbar)
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionClose.triggered.connect(self.closeApp)
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        '''
        Input sections and buttons
        '''
        #Starting the buttons
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser2 = QtWidgets.QTextBrowser(self.centralwidget)
       
        # Sizing policies for the widget. How the widget handled stretching
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.textBrowser.sizePolicy().hasHeightForWidth())

        # Sets the sizing policy from values above. Input.self.textBrowser.setSizePolicy(sizePolicy)self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 20))
        self.textBrowser.setInputMethodHints(QtCore.Qt.ImhNone)
        self.textBrowser.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))

        # Sets the sizing policy from values above. Output.self.textBrowser2.setSizePolicy(sizePolicy)self.textBrowser2.setSizePolicy(sizePolicy)
        self.textBrowser2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.textBrowser2.setInputMethodHints(QtCore.Qt.ImhNone)
        self.textBrowser2.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser2.setObjectName(_fromUtf8("textBrowser2"))

        # Grid Layout for textBrowser.
        self.gridLayout.addWidget(self.textBrowser, 3, 0, 1, 2)
        self.gridLayout.addWidget(self.textBrowser2, 4, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 10, 2, 3)

        # Pick A Input button
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.btnBrowse.clicked.connect(self.getFile)
        self.gridLayout.addWidget(self.btnBrowse, 3, 4, 1, 2)

        # Pick A Output button
        self.btnOutput = QtWidgets.QPushButton(self.centralwidget)
        self.btnOutput.setObjectName(_fromUtf8("btnOutput"))
        self.btnOutput.clicked.connect(self.setOutput)
        self.gridLayout.addWidget(self.btnOutput, 4, 4, 1, 2)
       
        '''
        Buttons for various functions in headless
        Is layed out in order below
        '''

        # Headless boolean
        self.Headless_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Headless_chkBox.setObjectName(_fromUtf8("headless"))
        self.Headless_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Headless_chkBox))
        self.gridLayout.addWidget(self.Headless_chkBox, 5, 0, 1, 4)

        # Delete hierarchy sub-boolean
        self.Delete_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Delete_chkBox.setObjectName(_fromUtf8("delete"))
        self.Delete_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Delete_chkBox))
        self.gridLayout.addWidget(self.Delete_chkBox, 6, 0, 1, 4)
        self.Delete_chkBox.setDisabled(True)
        
        # Remove hidden objects sub-boolean
        self.Hidden_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Hidden_chkBox.setObjectName(_fromUtf8("hidden"))
        self.Hidden_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Hidden_chkBox))
        self.gridLayout.addWidget(self.Hidden_chkBox, 7, 0, 1, 4)
        self.Hidden_chkBox.setDisabled(True)

        # Split sub-boolean
        self.Loose_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Loose_chkBox.setObjectName(_fromUtf8("loose"))
        self.Loose_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Loose_chkBox))
        self.gridLayout.addWidget(self.Loose_chkBox, 8, 0, 1, 4)
        self.Loose_chkBox.setDisabled(True)

        # Cleanup boolean
        self.CleanUp_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.CleanUp_chkBox.setObjectName(_fromUtf8("cleanUp"))
        self.CleanUp_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.CleanUp_chkBox))
        self.gridLayout.addWidget(self.CleanUp_chkBox, 9, 0, 1, 4)
        self.CleanUp_chkBox.setDisabled(True)

        # Clean up percentage
        self.CleanUp_percentage = QtWidgets.QLineEdit(self.centralwidget)
        self.CleanUp_percentage.setObjectName(_fromUtf8("percent"))
        self.CleanUp_percentage.setPlaceholderText("0.5")
        self.CleanUp_percentage.setText("0.5")
        #self.CleanUp_percentage.resize(20,10)
        self.gridLayout.addWidget(self.CleanUp_percentage, 10, 1, 1, 1)
        self.CleanUp_percentage.setDisabled(True)

        # Clean up percentage label
        self.CleanUp_percentage_label = QtWidgets.QLabel(self.centralwidget)
        self.CleanUp_percentage_label.setObjectName(_fromUtf8("percentLabel"))
        self.gridLayout.addWidget(self.CleanUp_percentage_label, 10, 0, 1, 1)
        self.CleanUp_percentage_label.setDisabled(True)

        # Merge sub-boolean
        self.Merge_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Merge_chkBox.setObjectName(_fromUtf8("merge"))
        self.Merge_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Merge_chkBox))
        self.gridLayout.addWidget(self.Merge_chkBox, 11, 0, 1, 4)
        self.Merge_chkBox.setDisabled(True)


        # Center sub-boolean
        self.Center_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Center_chkBox.setObjectName(_fromUtf8("center"))
        self.Center_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Center_chkBox))
        self.gridLayout.addWidget(self.Center_chkBox, 12, 0, 1, 4)
        self.Center_chkBox.setDisabled(True)



        # Slider creation for Decimation
        # Slider only does ints. Changed to floats later on
        self.dec_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.dec_slider.setMinimum(0)
        self.dec_slider.setMaximum(50)
        self.dec_slider.setValue(0)
        self.dec_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.dec_slider.setTickInterval(5)
        self.dec_slider.setDisabled(True)
        # Sets the placement of the slider
        self.gridLayout.addWidget(self.dec_slider, 6, 5, 8, 2)
        # Connection for changes
        self.dec_slider.valueChanged.connect(self.sliderChange)
        # Percentage label
        self.slider_label = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.slider_label, 12, 3, 2, 2)
        self.slider_label.setText("\n\n\t {}".format(self.decimateAmount))
        self.slider_label.setDisabled(True)

        # Text label Decimation
        self.decimation = QtWidgets.QLabel(self.centralwidget)
        self.decimation.setObjectName(_fromUtf8("decimation"))
        self.gridLayout.addWidget(
            self.decimation, 5, 4, 1, 2, Qt.AlignCenter)   
        self.decimation.setDisabled(True)

        '''
        Hiding Launcher console window, saving window id
        '''
        self.cmd_window = None
        def windowEnumerationHandler(hwnd, top_windows):
            top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for i in top_windows:
            if "rmit" in i[1].lower():
                self.cmd_window = i[0] # saving window id
                break

        win32gui.ShowWindow(self.cmd_window, 0) # hide window


        '''
        Process button
        '''
        # Process set up and placement in the widget
        self.Process = QtWidgets.QPushButton(self.centralwidget)
        self.Process.setObjectName(_fromUtf8("Process"))
        self.Process.clicked.connect(self.processFile)
        self.gridLayout.addWidget(self.Process, 14, 0, 1, 2)

        '''
        Final code to place widgets
        '''
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        return True

    def retranslateUi(self, MainWindow):
        """
        Handles the sizing when the user re-sizes the window. Keeps constraints

        :param MainWindow: Passes Main Window object to re-translate
        :return: self.
        """
        MainWindow.setWindowTitle(_translate("MainWindow", "RMIT Launcher Window", None))
        itLogo = ''
        try:
            if getattr(sys, 'frozen', False): #Frozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
            else:                         #unFrozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
        except:
            pass
        MainWindow.setWindowIcon(QtGui.QIcon(itLogo))
        #Setting texts for all the widgets
        self.Process.setText(_translate("MainWindow", "Process", None))
        self.CleanUp_chkBox.setText(_translate(
            "MainWindow", "Remove small, high density objects", None))
        self.Loose_chkBox.setText(_translate(
            "MainWindow", "Separate objects by loose meshes", None))
        self.Merge_chkBox.setText(_translate(
            "MainWindow", "Merge all objects together", None))
        self.Delete_chkBox.setText(_translate(
            "MainWindow", "Delete any relation/hierarchy of object(s)", None))
        self.Hidden_chkBox.setText(_translate(
            "MainWindow", "Remove hidden object(s)", None))
        self.Center_chkBox.setText(_translate(
            "MainWindow", "Center object(s) to world origin", None))
        self.Headless_chkBox.setText(_translate(
            "MainWindow", "Headless: Runs Blender in the background", None))
        self.CleanUp_percentage_label.setText(_translate(
        "MainWindow", "          Max relative size to remove (Max 99.99):", None))
        self.decimation.setText(_translate(
            "MainWindow", "<html><head/><body><p>"
            "<span style=\" font-size:10pt;\">"
            "<u>Decimation</u></span></p></body></html>", None))
        self.processModel.setText(_translate(
            "MainWindow", "<html><head/><body><p>"
            "<span style=\" font-size:10pt; font-weight:600;\">"
            "Choose Model to Process and Output Location</span></p></body></html>", None))
        self.btnBrowse.setText(_translate("MainWindow", "Choose Input", None))
        self.btnOutput.setText(_translate("MainWindow", "Choose Output", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionClose.setText(_translate("MainWindow", "Exit", None))                

    def sliderChange(self, value):
        """
        GUI slider for the decimation option. Works in 10% increments.
        :param value: Decimation value divided by 10 to record a percent.
        :return:
        """
        self.decimateAmount = round((2*value)/100,2)
        self.slider_label.setText("\n\n\t {} %".format(round(self.decimateAmount*100,2)))

    def getFile(self):
        """
        The button used to pick a valid file for processing.
        Invokes the PyQT FileDialog, displays name in text box.

        :param MainWindow: Main window object
        :return: (str) path to file.
        """
        
        # Use the QT File Dialog system for selecting a file
        specialChars = ['!', '@', '#', '$', '%', '^', '&', '*']
        if not self.unittesting:
            self.filename = QtWidgets.QFileDialog.getOpenFileName(
                self, 'Open File', '.', "Model files (*.dae *.obj *.stl *.fbx *.ply *.gltf *.glb)")

       #Set Icon
        itLogo = ''
        try:
            if getattr(sys, 'frozen', False): #Frozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
            else:                         #unFrozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
        except:
            pass

       # If the user has special characters in the file name. Kick it back. Messes up Blender.
        if any(sChar in self.filename[0] for sChar in specialChars):
            if not self.unittesting:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Please remove special characters from file name')
                msg.setWindowTitle("RMIT Launcher")
                msg.setWindowIcon(QtGui.QIcon(itLogo))
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()
            return False 
        
        try:
            fname = open(self.filename[0], "r", encoding='utf-8', errors='ignore')
            self.textBrowser.setText(os.path.basename(fname.name))
            self.filePathIn = fname.name

            # Set the default ouput to be the same folder as the input
            # Make sure file name does not contain . as it causes a bug
            sName = os.path.splitext(os.path.basename(fname.name))[0]          
            if('.' in sName):
                sName = sName.replace('.','')
            self.filePathOut = os.path.dirname(self.filePathIn) + "/" + sName + ".gltf"
            self.textBrowser2.setText(self.filePathOut)
            fname.close()
            return True
        except:
            pass
        
    def setOutput(self):
        """
        The button used to set the output for the file.
        Invokes the PyQT FileDialog, displays name in text box.

        :param MainWindow: Main window object
        :return: (str) path to directory.
        """
        specialChars = ['!', '@', '#', '$', '%', '^', '&', '*']
        fileTypes = ['gltf', 'glb', 'fbx', 'dae', 'obj', 'stl']
        if not self.unittesting:
            self.filename = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Choose an export directory and file type',
                self.filePathOut,
                "Gltf (*.gltf);;FBX (*.fbx);;Collada (*.dae);;Wavefront (*.obj);;STL (*.stl)")
        #Set icon
        itLogo = ''
        try:
            if getattr(sys, 'frozen', False): #Frozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
            else:                         #unFrozen
                itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
        except:
            pass
        # If the user has special characters in the file name. Kick it back. Messes up Blender.
        if any(sChar in self.filename[0] for sChar in specialChars):
            if not self.unittesting:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Please remove special characters from file name')
                msg.setWindowTitle("RMIT Launcher")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setWindowIcon(QtGui.QIcon(itLogo))
                msg.exec_()
            return False
        
        # This ensures that the file extension is one that is supported.
        if  any(filetype in self.filename[0][-4:] for filetype in fileTypes) or self.filename[0] == '':
            pass
        else:
            if not self.unittesting:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText('Export path contains unsupported file type. Please correct')
                msg.setWindowTitle("RMIT Launcher")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setWindowIcon(QtGui.QIcon(itLogo))
                msg.exec_()
            return False
        
        # If the user doesn't make any change or hits cancel then just pass.
        if self.filename[0] == '':
            pass
        else:
            self.textBrowser2.setText(self.filename[0])
            self.filePathOut = self.filename[0]
        return True
    #TODO: is there a way to not always check object name
    def btnstate(self, b):
        """
        Records the user choice of decimation and if headless

        :param b: the check box option chosen by user
        :return: bool type options
        """
        if (b.objectName() == "headless"):
            if b.isChecked():
                self.CleanUp_chkBox.setDisabled(False)
                self.Delete_chkBox.setDisabled(False)
                self.Hidden_chkBox.setDisabled(False)
                self.Loose_chkBox.setDisabled(False)
                self.Center_chkBox.setDisabled(False)
                self.Merge_chkBox.setDisabled(False)
                self.decimation.setDisabled(False)
                self.dec_slider.setDisabled(False)
                self.slider_label.setDisabled(False)
                self.headless = True
            else:
                self.CleanUp_chkBox.setDisabled(True)
                self.Delete_chkBox.setDisabled(True)
                self.Hidden_chkBox.setDisabled(True)
                self.Loose_chkBox.setDisabled(True)
                self.decimation.setDisabled(True)
                self.Center_chkBox.setDisabled(True)
                self.Merge_chkBox.setDisabled(True)
                self.CleanUp_chkBox.setChecked(False)
                self.Loose_chkBox.setChecked(False)
                self.Delete_chkBox.setChecked(False)
                self.Hidden_chkBox.setChecked(False)
                self.Center_chkBox.setChecked(False)
                self.Merge_chkBox.setChecked(False)
                self.dec_slider.setDisabled(True)
                self.slider_label.setDisabled(True)
                self.headless = False

        elif (b.objectName() == "cleanUp"):
            if b.isChecked():
                self.CleanUp_percentage.setDisabled(False)
                self.CleanUp_percentage_label.setDisabled(False)
                self.cleanUpPercent = float(self.CleanUp_percentage.text())/100
                self.cleanUp = True
            else:
                self.CleanUp_percentage.setDisabled(True)
                self.CleanUp_percentage_label.setDisabled(True)
                self.cleanUpPercent = 0.0
                self.cleanUp = False
        elif (b.objectName() == "hidden"):
            if b.isChecked():
                self.hidden = True
            else:
                self.hidden = False     
        elif (b.objectName() == "delete"):
            if b.isChecked():
                self.delete = True
            else:
                self.delete = False       
        elif (b.objectName() == "loose"):
            if b.isChecked():
                self.loose = True
            else:
                self.loose = False
        elif (b.objectName() == "center"):
            if b.isChecked():
                self.center = True
            else:
                self.center = False
        elif (b.objectName() == "merge"):
            if b.isChecked():
                self.merge = True
            else:
                self.merge = False            


    def processFile(self):
        """
        When given a path, this function will process the file with Blender.

        :return:
        """
        with open('dataProcessingLogs.txt', 'w') as f:
            try:
                if self.filePathIn == '' or self.filePathOut == '':
                    raise Exception("Input or Output file was not set")
                
                # Get current working directory        
                if getattr(sys, 'frozen', False): #Frozen
                    cwdir = pathlib.Path(sys.executable).parent.resolve()
                else:                             #unFrozen
                    cwdir = pathlib.Path(__file__).parent.resolve()
                #Changes the current working directory to parent one. RMIT folder
                os.chdir(cwdir)

                #Try to find blender.exe. Fail if it can't be found. 
                try:
                    # curDir is current directory path, dirs is all folders, files are names
                    # This list comprehension will walk the directories and assign if found.
                    blenderPath = [os.path.join(curDir, x)
                                   for curDir, dirs, files in os.walk(cwdir)
                                   for x in files if str(curDir+x).endswith("blender_for_RMITblender.exe")]
                    blenderPath = blenderPath[0]
                except:    
                    err.errorReport()
                    raise Exception("Failed to find Blender")                    

                #Checking to see if its not a default supported filetype, if not it will run the datasmith process to export to fbx and then into the normal process
                fileTypes = ['.fbx','.dae','.obj','.stl','.ply', 'gltf', 'glb']
                if not any(x in self.filePathIn.casefold() for x in fileTypes):
                    try:
                        inputD = self.filePathIn
                        outputD = os.path.dirname(os.path.realpath(__file__)) + "\\Datasmith\Exports\main_exportData.fbx"
                        scriptD = os.path.dirname(os.path.realpath(__file__)) + "\\unrealim.py"
                        projectD = os.path.dirname(os.path.realpath(__file__)) + "\\Datasmith\Project\datasmith.uproject"
                        #Read from config
                        config = configparser.ConfigParser()
                        #config.read('RMIT.config')
                        #if 'datasmith' in config and 'exe' in config['datasmith']:
                        #    pathD = config['datasmith']['exe']
                            #else:
                            #    err.errorReport()
                            #    return
                        #else:
                        #    return
                        pathD = "C:\\Program Files\\Epic Games\\UE_4.24\\Engine\\Binaries\\Win64\\UE4Editor-Cmd.exe"
                        argsD = '"{}" "{}" -run=pythonscript -script="{} {} {}"'.format(pathD,projectD,scriptD,inputD,outputD)
                        print(argsD)
                        self.colorfix = True
                        subprocess.run(argsD, shell=True)
                        self.filePathIn = outputD
                    except:
                        err.errorReport()
                
                #TODO: This seems unncessary now. Test and verify so that this can be deleted. 
                #      I don't think we need to divide by 100 when the value input is already in decimal form. i.e : 0.01
                if float(self.CleanUp_percentage.text()) > 99.99 or float(self.CleanUp_percentage.text()) < 0:
                    raise Exception("Cleanup percent is not a proper value")
                self.cleanUpPercent = float(self.CleanUp_percentage.text())/100
                # This is a silly fix because it will be sent as a none object without any value...
                self.decimate = not (self.decimateAmount == 0.0)

                """
                Argument Flags:
                -b(Background), -P(PythonScript), -i(filePathIn,<str>), -e(filePathOut<str>), -d(decimate<bool>), -p(decimate<float>)
                -c(cleanUp<bool>), -l(cleanUpPercent<float>), -x(hidden<bool>), -r(delete<bool>), -m(merge<bool>), -o(center<bool>), -s(loose<bool>)
                """
                if self.headless == True:
                    if self.cmd_window != None:
                        win32gui.ShowWindow(self.cmd_window, 1)
                    args = "{} -b -P RMIT_BlenderDriver.py -- -i {} -e {} -d {} -p {} -c {} -l {} -x {} -r {} -m {} -o {} -s {}".format(
                        blenderPath,self.filePathIn,self.filePathOut,self.decimate,self.decimateAmount,self.cleanUp,self.cleanUpPercent,self.hidden,self.delete,self.merge,self.center,self.loose)
                else:
                    #TODO: The default float of the clean up divides it again by 100. The resulting arg is 0.0001. Check this for accuracy.
                    # Blender recognizes all arguments after -- as args for scripts.
                    args = "start cmd.exe /k {} -P RMIT_BlenderDriver.py -- -i {} -e {} -d {} -p {} -c {} -l {} -x {} -r {} -m {} -o {} -s {}".format(
                        blenderPath,self.filePathIn,self.filePathOut,self.decimate,self.decimateAmount,self.cleanUp,self.cleanUpPercent,self.hidden,self.delete,self.merge,self.center,self.loose)
               
                # Process instantiation for blender with options and script args
                try:
                    if not self.unittesting:   
                        subprocess.run(args,shell=True)
                    else:
                        return True
                except:
                    err.errorReport()
                    raise Exception("Could not run subprocess")
                #os.system(args)
                
                f.write('Success: \n' + args + '\n')
            except Exception as inst:
                f.write('Failed: ' + str(inst))
                try:
                    if getattr(sys, 'frozen', False): #Frozen
                        itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
                    else:                         #unFrozen
                        itLogo = str(list(pathlib.Path().rglob('ITACL-Patch-Final.png'))[0])
                except:
                    pass
                if not self.unittesting:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText(str(inst))
                    msg.setWindowTitle("RMIT Launcher")
                    msg.setWindowIcon(QtGui.QIcon(itLogo))
                    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                    msg.exec_()
                return False


    def closeApp(self):
        """
        Close the application.

        :return:
        """
        sys.exit()



if __name__ == "__main__":
    """
    Create a new instance of the GUI main window.
    Apply defaults, show and then exit when closed.
    """
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())