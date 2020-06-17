# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
import os
import pathlib
import sys
import shlex
import subprocess

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
        MainWindow.resize(500, 182)

        # Defaults for widget. Such as decimations and filepath
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.decimateAmount = 0.0
        self.cleanUp = 0
        self.loose = False
        self.headless = ''
        self.filePathIn = ''
        self.filePathOut = ''
        self.percent = .01

        # Grid layout declerations
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        # Process set up and placement in the widget
        self.Process = QtWidgets.QPushButton(self.centralwidget)
        self.Process.setObjectName(_fromUtf8("Process"))
        self.Process.clicked.connect(self.processCollada)
        self.gridLayout.addWidget(self.Process, 8, 9, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser2 = QtWidgets.QTextBrowser(self.centralwidget)

        # Sizing policies for the widget. How the widget handled stretching
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.textBrowser.sizePolicy().hasHeightForWidth())

        # Sets the sizing policy from values above. Input.
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMaximumSize(QtCore.QSize(16777215, 20))
        self.textBrowser.setInputMethodHints(QtCore.Qt.ImhNone)
        self.textBrowser.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))

        # Sets the sizing policy from values above. Output.
        self.textBrowser2.setSizePolicy(sizePolicy)
        self.textBrowser2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.textBrowser2.setInputMethodHints(QtCore.Qt.ImhNone)
        self.textBrowser2.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser2.setObjectName(_fromUtf8("textBrowser2"))

        # Grid Layout for textBrowser.
        self.gridLayout.addWidget(self.textBrowser, 3, 0, 1, 8)
        self.gridLayout.addWidget(self.textBrowser2, 4, 0, 1, 8)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 10, 2, 2)

        # Pick A Input button
        self.btnBrowse = QtWidgets.QPushButton(self.centralwidget)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.btnBrowse.clicked.connect(self.getFile)
        self.gridLayout.addWidget(self.btnBrowse, 3, 8, 1, 1)

        # Pick A Output button
        self.btnOutput = QtWidgets.QPushButton(self.centralwidget)
        self.btnOutput.setObjectName(_fromUtf8("btnOutput"))
        self.btnOutput.clicked.connect(self.setOutput)
        self.gridLayout.addWidget(self.btnOutput, 4, 8, 1, 1)

        # Cleanup boolean
        self.CleanUp_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.CleanUp_chkBox.setObjectName(_fromUtf8("cleanUp"))
        self.CleanUp_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.CleanUp_chkBox))
        self.gridLayout.addWidget(self.CleanUp_chkBox, 6, 0, 1, 10)

        # Clean up percentage
        self.CleanUp_percentage = QtWidgets.QLineEdit(self.centralwidget)
        self.CleanUp_percentage.setObjectName(_fromUtf8("percent"))
        self.CleanUp_percentage.setPlaceholderText(".01")
        self.CleanUp_percentage.setText(".01")
        self.CleanUp_percentage.resize(20,10)
        self.gridLayout.addWidget(self.CleanUp_percentage, 7, 5, 1, 2)
        self.CleanUp_percentage.setDisabled(True)

        # Clean up percentage label
        self.CleanUp_percentage_label = QtWidgets.QLabel(self.centralwidget)
        self.CleanUp_percentage_label.setObjectName(_fromUtf8("percentLabel"))
        self.gridLayout.addWidget(self.CleanUp_percentage_label, 7, 1, 1, 4)
        self.CleanUp_percentage_label.setDisabled(True)

        # Loose sub-boolean
        self.Loose_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Loose_chkBox.setObjectName(_fromUtf8("loose"))
        self.Loose_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Loose_chkBox))
        self.gridLayout.addWidget(self.Loose_chkBox, 8, 1, 1, 8)
        self.Loose_chkBox.setDisabled(True)

        # Headless boolean
        self.Headless_chkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.Headless_chkBox.setObjectName(_fromUtf8("headless"))
        self.Headless_chkBox.stateChanged.connect(
            lambda: self.btnstate(self.Headless_chkBox))
        self.gridLayout.addWidget(self.Headless_chkBox, 5, 0, 1, 10)

        # Slider creation for Decimation
        # Slider only does ints. Changed to floats later on
        self.dec_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.dec_slider.setMinimum(0)
        self.dec_slider.setMaximum(9)
        self.dec_slider.setValue(0)
        self.dec_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.dec_slider.setTickInterval(1)
        # Sets the placement of the slider
        self.gridLayout.addWidget(self.dec_slider, 1, 9, 7, 3)
        # Connection for changes
        self.dec_slider.valueChanged.connect(self.sliderChange)
        # Percentage label
        self.slider_label = QtWidgets.QLabel(self.centralwidget)
        self.gridLayout.addWidget(self.slider_label, 3, 9, 1, 1)
        self.slider_label.setText("\n\n\t {}".format(self.decimateAmount))

        # Text label Decimation
        self.decimation = QtWidgets.QLabel(self.centralwidget)
        self.decimation.setObjectName(_fromUtf8("decimation"))
        self.gridLayout.addWidget(
            self.decimation, 0, 9, 1, 1)

        # Text label Choose Model to Process
        self.processModel = QtWidgets.QLabel(self.centralwidget)
        self.processModel.setObjectName(_fromUtf8("processModel"))
        self.gridLayout.addWidget(
            self.processModel, 0, 0, 1, 9, QtCore.Qt.AlignHCenter)

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

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        Handles the sizing when the user re-sizes the window. Keeps constraints

        :param MainWindow: Passes Main Window object to re-translate
        :return: self.
        """
        MainWindow.setWindowTitle(_translate("MainWindow", "RMIT", None))
        MainWindow.setWindowIcon(QtGui.QIcon(
           str(pathlib.Path(__file__).parent / 'ITACL-Patch-Final.png')))
        self.Process.setText(_translate("MainWindow", "Process", None))

        self.CleanUp_chkBox.setText(_translate(
            "MainWindow", "Clean Up: Removes small, high density objects", None))
        self.Loose_chkBox.setText(_translate(
            "MainWindow", "Separate objects by loose meshes: SLOW", None))
        self.Headless_chkBox.setText(_translate(
            "MainWindow", "Headless: Runs blender in the background", None))
        self.CleanUp_percentage_label.setText(_translate(
        "MainWindow", "Max Relative size to remove:", None))
        self.decimation.setText(_translate(
            "MainWindow", "<html><head/><body><p>"
            "<span style=\" font-size:10pt;\">"
            "<u>Decimation</u></span></p></body></html>", None))
        self.processModel.setText(_translate(
            "MainWindow", "<html><head/><body><p>"
            "<span style=\" font-size:12pt; font-weight:600;\">"
            "Choose Model to Process and Output Location</span></p></body></html>", None))
        self.btnBrowse.setText(_translate("MainWindow", "Choose Input", None))
        self.btnOutput.setText(_translate("MainWindow", "Choose Output", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionClose.setText(_translate("MainWindow", "Exit", None))

    def getFile(self):
        """
        The button used to pick a valid file for processing.
        Invokes the PyQT FileDialog, displays name in text box.

        :param MainWindow: Main window object
        :return: (str) path to file.
        """
        # Use the QT File Dialog system for selecting a file
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open File', '.', "Model files (*.dae *.obj *.stl *.fbx *.ply)")
        fname = open(filename[0], "r", encoding='utf-8', errors='ignore')
        self.textBrowser.setText(os.path.basename(fname.name))
        self.filePathIn = fname.name

        # Set the default ouput to be the same folder as the input
        self.filePathOut = os.path.dirname(self.filePathIn) + "/" + \
            os.path.splitext(os.path.basename(fname.name))[0] + ".gltf"
        self.textBrowser2.setText(self.filePathOut)
        fname.close()

    def setOutput(self):
        """
        The button used to set the output for the file.
        Invokes the PyQT FileDialog, displays name in text box.

        :param MainWindow: Main window object
        :return: (str) path to directory.
        """
        
        '''
        # Ensure we don't keep adding to this file path.
        self.filePathOut = os.path.splitext(
            os.path.basename(self.filePathIn))[0]

        # Set the default ouput to be the same folder as the input
        filenameOut = str(QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory"))
        if filenameOut != "":
            self.filePathOut = filenameOut + "/" + \
                os.path.splitext(self.filePathOut)[0] + '.gltf'
            self.textBrowser2.setText(self.filePathOut)
            print(self.filePathOut)
        '''
        # TODO: Add error checking, fix cancel issue
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Choose an export directory and file type',
            self.filePathOut,
            "Gltf (*.gltf);;FBX (*.fbx);;Collada (*.dae);;Wavefront (*.obj)")
        self.textBrowser2.setText(fileName[0])
        self.filePathOut = fileName[0]


    def sliderChange(self, value):
        """
        GUI slider for the decimation option. Works in 10% increments.
        :param value: Decimation value divided by 10 to record a percent.
        :return:
        """
        self.decimateAmount = value/10
        self.slider_label.setText("\n\n\t {} %".format(self.decimateAmount*100))

    # Stores the Decimation option the user chooses or cleanup option
    def btnstate(self, b):
        """
        Records the user choice of decimation and if headless

        :param b: the check box option chosen by user
        :return: bool type options
        """

        if b.text() == "Clean Up: Removes small, high density objects":
            self.cleanUp = b.isChecked()
            if b.isChecked():
                print(b.text() + " is selected")
                self.Loose_chkBox.setDisabled(False)
                self.CleanUp_percentage.setDisabled(False)
                self.CleanUp_percentage_label.setDisabled(False)
                self.loose = self.Loose_chkBox.isChecked()
                self.percent = self.CleanUp_percentage.text()
            else:
                print(b.text() + " is deselected")
                self.CleanUp_percentage.setDisabled(True)
                self.CleanUp_percentage_label.setDisabled(True)
                self.Loose_chkBox.setDisabled(True)
                self.loose = False
                self.percent = 0.0
        if b.text() == "Separate objects by loose meshes: CAUTION: can be slow":
            if b.isChecked():
                print(b.text() + " is selected")
                self.loose = True
            else:
                print(b.text() + " is deselected")
                self.loose = False
        if b.text() == "Headless: Runs blender in the background":
            if b.isChecked():
                print(b.text() + " is selected")
                self.headless = '-b'
            else:
                print(b.text() + " is deselected")
                self.headless = ''

    def processCollada(self):
        """
        When given a path, this function will process the file with Blender.
        This opens a 'subprocess' module that calls a process.

        :return:
        """
        with open('dataProcessingLogs.txt', 'w') as f:
            try:
                if self.filePathIn == '' or self.filePathOut == '':
                    raise Exception

                # 3 paths are required.
                # The current working directory where the executable exists
                # The driver script in the same current working directory
                # The location of blender that should be in the same directory tree
                # ** looks into multiple levels of the root directory
                # In this case BlenderPlugin/Blender/../Blender.exe
                cwdir = pathlib.Path(__file__).parent.resolve()
                scriptPath = cwdir.joinpath('RMIT_BlenderDriver.py')
                isBlenderHere = list(
                    cwdir.parent.glob('**/blender-2.81.0-8-28-19/blender.exe'))
                if isBlenderHere[0].exists():
                    blenderPath = str(isBlenderHere[0])
                else:
                    raise Exception

                # This is a silly fix because it will be sent as a none object without any value.
                if self.decimateAmount == 0.0:
                    self.decimateAmount = 0.09
                
                # safe input check
                self.percent = self.CleanUp_percentage.text()
                float(self.percent)

                # This is for Windows because of issues with subprocess clashing with PyInstaller
                # For detailed info go here. https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
                if hasattr(subprocess, 'STARTUPINFO'):
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    env = os.environ  # Windows doesn't search path by default.Make it.
                else:
                    si = None
                    env = None

                # Blender recognizes all arguments after -- as args for scripts.
                args = [
                    str(blenderPath), self.headless, '-P', str(scriptPath),
                    '--', '-i', self.filePathIn, '-e', self.filePathOut, '-d',
                    str(self.decimateAmount), '-c', str(self.cleanUp),
                    '-l', str(self.loose), '-x', str(self.percent)]
                if self.headless != '-b':  # remove headless option from args
                    del args[1]

                print(args)

                # Process instantiation for blender with options and script args
                p = subprocess.Popen(
                    args, cwd=cwdir, close_fds=True, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
                    startupinfo=si, env=env)
                stdout, stderr = p.communicate()
                f.write('Success: \n' + str(stdout) + '\n')
                f.write('Success: \n' + str(stderr) + '\n')
                f.write(str(cwdir) + '\n' + str(args) + '\n')
            except Exception as inst:
                f.write('Failed: ' + str(inst))
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText(str(inst))
                msg.setWindowTitle("RMIT")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()

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
