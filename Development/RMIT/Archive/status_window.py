import sys
import os 
import bpy
import pathlib
import PyQt5.QtGui
import PyQt5.QtCore
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class Ui_MainWindow(object):
    def __init__(self):
        #This hack gets the output path still stored in sys.arg
        try:
            self._outPath = sys.argv[7]
        except:
            self._outPath = "Not Available"        #self._outPath = r"\\AVR-E\Users\AVR\RMIT_Models\Test_Models\OpenCOLLADA Models\Manlift\manlift.gltf"

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        # QWidget.setGeometry(xpos, ypos, width, height)
        MainWindow.resize(300, 150)
        MainWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
        MainWindow.setWindowIcon(PyQt5.QtGui.QIcon(
            str(pathlib.Path(__file__).parent.parent / 'ITACL-Patch-Final.png')))

        # Central Widget for RMIT
        self.centralwidget = PyQt5.QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget{background-color: #303030;}")
        self.gridLayout = PyQt5.QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridlayout")
        
        # Scene Stats Label 
        self.sceneStatsLabel = PyQt5.QtWidgets.QLabel(self.centralwidget)
        self.sceneStatsLabel.setObjectName("sceneStats")
        self.sceneStatsLabel.setAlignment(Qt.AlignCenter)
        self.sceneStatsLabel.setStyleSheet("QLabel{background-color: #505050; color: white; font: 16px;}")
        self.sceneStatsLabel.setText(self.getStatCount())
        self.gridLayout.addWidget(self.sceneStatsLabel, 0, 1, Qt.AlignTop)

        # User Instructions
        self.instructionsLabel = PyQt5.QtWidgets.QLabel(self.centralwidget)
        self.instructionsLabel.setObjectName("instructions")
        self.instructionsLabel.setAlignment(Qt.AlignCenter)
        self.instructionsLabel.setStyleSheet("QLabel{ color: white; font: 14px;}")
        self.instructionsLabel.setText(" Verify model for accuracy and make any final edits before selecting \n'Proceed to Export'")
        self.gridLayout.addWidget(self.instructionsLabel, 1, 1, Qt.AlignTop)

        # Proceed to export button
        self.proceedExportButton = PyQt5.QtWidgets.QPushButton(self.centralwidget)
        self.proceedExportButton.setObjectName("proceedExport")
        self.proceedExportButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 6px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.proceedExportButton.setText("Proceed to Export")
        self.proceedExportButton.clicked.connect(self.exportClose)
        self.gridLayout.addWidget(self.proceedExportButton, 2, 1, Qt.AlignCenter)


        MainWindow.setCentralWidget(self.centralwidget)  
        self.retranslateUi(MainWindow)      

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(PyQt5.QtWidgets.QApplication.translate("MainWindow", "RMIT-Progress Status Window", None))
        #self.lineEdit.setText(PyQt4.QtGui.QApplication.translate("MainWindow", "c:/", None, PyQt4.QtGui.QApplication.UnicodeUTF8))
        #self.pushButton.setText(PyQt4.QtGui.QApplication.translate("MainWindow", "export", None, PyQt4.QtGui.QApplication.UnicodeUTF8))

    def getStatCount(self):
        indexList = [3,2,4,5]
        defaultLayer = bpy.context.scene.view_layers['View Layer']
        sceneStatList = bpy.context.scene.statistics(defaultLayer).split("|")
        sceneStatCount = [sceneStatList[i] for i in indexList]
        statString = "Current Scene Stats: " +"".join(sceneStatCount)
        return statString

    #slot function
    def exportClose(self):
        try:
            if ".gltf" in self._outPath:
                # rips the extension out before saving as a glb
                # we hard set some defaults for our exporter
                bpy.ops.export_scene.gltf(
                    filepath=os.path.splitext(self._outPath)[0],
                    export_format='GLTF_SEPARATE', export_apply=False)
            elif ".fbx" in self._outPath:
                bpy.ops.export_scene.fbx(
                    filepath=self._outPath)
            elif ".dae" in self._outPath:
                bpy.ops.wm.collada_export(
                    filepath=self._outPath)
            elif ".obj" in self._outPath:
                bpy.ops.export_scene.obj(
                    filepath=self._outPath)
            else:
                raise RuntimeError("File path/extension not valid")
        except Exception as e:
            self.instructionsLabel.setText(str(e))
        return
        #app.beep()
        #self.centralwidget.cl
        # note that at this point, I think the Qt app
        # is technically still 'running'

class qt_window(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        PyQt5.QtWidgets.QMainWindow.__init__(self)

        #Sets Ui_MainWindow to self.controls
        self.controls = Ui_MainWindow()
        self.controls.setupUi(self)
        
        self.show()

class PyQtEventLoopOp(bpy.types.Operator):
    bl_idname = "wm.pyqt_event_loop"
    bl_label = "PyQt Event Loop"
    _timer = None
    _window = None

    # Modal with processEvents
    def modal(self, context, event):
        if event.type == 'TIMER':
            #Process the events for my qt stuff
            self.window.controls.sceneStatsLabel.setText(
                self.window.controls.getStatCount())
            #self.window.controls.filePath()
            self._event_loop.processEvents()
            self._application.sendPostedEvents(None, 0)
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Create an instance of the window app
        self._application = PyQt5.QtWidgets.QApplication.instance()
        # First object is named blender since at first it is none
        if self._application is None:
            self._application = PyQt5.QtWidgets.QApplication(['blender'])
        self._event_loop = PyQt5.QtCore.QEventLoop()
        
        # exec("return_inst = qt_window()", locals(), globals())
        self.window = qt_window()

        # Standard Blender Op Stuff
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(PyQtEventLoopOp)

def unregister():
    bpy.utils.unregister_class(PyQtEventLoopOp)

def run():
    try:
        register()
        bpy.ops.wm.pyqt_event_loop()
    except:
        bpy.ops.wm.pyqt_event_loop()

