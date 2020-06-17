import sys
import os 
import bpy
import pathlib
import time
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QMainWindow, QApplication, QStyle, QErrorMessage, QSpacerItem, QSizePolicy

class Ui_MainWindow(object):
    def __init__(self):
        pass

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(300, 200)
        #MainWindow.setWindowFlags(Qt.WindowStaysOnTopHint)
        try:
            try:
                MainWindow.setWindowIcon(QtGui.QIcon(
                    str(pathlib.Path(__file__).parent.parent.parent / 'ITACL-Patch-Final.ico')))
            except:
                MainWindow.setWindowIcon(QtGui.QIcon(
                    str(pathlib.Path(__file__).parent.parent / 'ITACL-Patch-Final.ico')))
        except:
            pass
        self.exportPath = ""

        # Central Widget for RMIT
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget{background-color: #303030;}")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridlayout")

        # Scene Stats Label 
        self.sceneStatsLabel = QLabel(self.centralwidget) 
        self.sceneStatsLabel.setObjectName("sceneStats")
        self.sceneStatsLabel.setStyleSheet("QLabel{background-color: #505050; color: white; font: 16px;}")
        self.sceneStatsLabel.setText(self.getStatCount())
        # Grid layout is (self, row, column, rowSpan, ColSpan, Alignment)
        self.gridLayout.addWidget(self.sceneStatsLabel, 0, 1, 1, 4, Qt.AlignCenter)

        # The Current Status
        self.statusLabel = QLabel(self.centralwidget)
        
        self.statusLabel.setObjectName("status")
        self.statusLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.statusLabel.setText("\n\t     Import Complete\nPlease proceed with processing and export\n\n")
        self.gridLayout.addWidget(self.statusLabel, 1, 0, 1, 4, Qt.AlignCenter)

        # !-------------------DE-PARENT------------------------------------------------!
        # De-Parent Label
        self.deParentLabel = QLabel(self.centralwidget)
        self.deParentLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.deParentLabel.setText("Remove from hierarchy")
        self.gridLayout.addWidget(self.deParentLabel, 3, 1, 1, 1, Qt.AlignLeft)
        # Info Button
        self.deParentInfo = QPushButton(self.centralwidget)
        infoIcon = QtGui.QIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.deParentInfo.setIcon(infoIcon)
        self.deParentInfo.setToolTip("This function will remove objects from their heiracy, if nothing is selected it will run on all mesh objects\n" + 
                                     "It also removes all empty nodes while preserving the transformations.")
        self.deParentInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.deParentInfo, 3, 0, 1, 1, Qt.AlignRight)
        # De-Parent Button
        self.deParentButton = QPushButton(self.centralwidget)
        self.deParentButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.deParentButton.setText("     Extract     ")
        self.deParentButton.clicked.connect(self.deparentRoutine)
        self.gridLayout.addWidget(self.deParentButton, 3, 3, 1, 1, Qt.AlignRight)
        # !-------------------DE-PARENT_END--------------------------------------------!

        # !-------------------CENTER---------------------------------------------------!
        # Center Label
        self.centerLabel = QLabel(self.centralwidget)
        self.centerLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.centerLabel.setText("Center model to world origin")
        self.gridLayout.addWidget(self.centerLabel, 4, 1, 1, 1, Qt.AlignLeft)
        # Info Button
        self.centerInfo = QPushButton(self.centralwidget)
        self.centerInfo.setIcon(infoIcon)
        self.centerInfo.setToolTip("This operation will take the models local origin and center it to the worlds origin.")
        self.centerInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.centerInfo, 4, 0, 1, 1, Qt.AlignRight)
        # Center Button
        self.centerButton = QPushButton(self.centralwidget)
        self.centerButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.centerButton.setText("     Center     ")
        self.centerButton.clicked.connect(self.centerRoutine)
        self.gridLayout.addWidget(self.centerButton, 4, 3, 1, 1, Qt.AlignRight)
        # !-------------------CENTER_END----------------------------------------------!

        # !-------------------DELETE_HIDDEN-------------------------------------------!
        # Delete Label
        self.deleteHidden = QLabel(self.centralwidget)
        self.deleteHidden.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.deleteHidden.setText("Delete hidden objects")
        self.gridLayout.addWidget(self.deleteHidden, 5, 1, 1, 1, Qt.AlignLeft)
        # Delete Button
        self.deleteInfo = QPushButton(self.centralwidget)
        self.deleteInfo.setIcon(infoIcon)
        self.deleteInfo.setToolTip("This operation will delete all hidden objects")
        self.deleteInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.deleteInfo, 5, 0, 1, 1, Qt.AlignRight)
        # Delete Button
        self.deleteButton = QPushButton(self.centralwidget)
        self.deleteButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.deleteButton.setText("Delete Hidden")
        self.deleteButton.clicked.connect(self.deleteRoutine)
        self.gridLayout.addWidget(self.deleteButton, 5, 3, 1, 1, Qt.AlignRight)
        # !-------------------DELETE_HIDDEN_END---------------------------------------!

        # !-------------------Split Mesh--------------------------------------!
        # Split Label
        self.splitLabel = QLabel(self.centralwidget)
        self.splitLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.splitLabel.setText("Split loose meshes")
        self.gridLayout.addWidget(self.splitLabel, 6, 1, 1, 2, Qt.AlignLeft)
        # Info Button
        self.splitInfo = QPushButton(self.centralwidget)
        self.splitInfo.setIcon(infoIcon)
        self.splitInfo.setToolTip("This operation will split any meshes that are not connected into seperate objects" + \
                                  "\nThis is useful for when you may need to interact with individual parts of objects")
        self.splitInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.splitInfo, 6, 0, 1, 1, Qt.AlignRight)
        # Split Button
        self.splitButton = QPushButton(self.centralwidget)
        self.splitButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.splitButton.setText("       Split      ")
        self.splitButton.clicked.connect(self.splitRoutine)
        self.gridLayout.addWidget(self.splitButton, 6, 3, 1, 1, Qt.AlignRight)
        # !-------------------SPLIT_END----------------------------------!

        # !-------------------Merge Mesh--------------------------------------!
        # Merge Label
        self.mergeLabel = QLabel(self.centralwidget)
        self.mergeLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.mergeLabel.setText("Merge meshes")
        self.gridLayout.addWidget(self.mergeLabel, 7, 1, 1, 1, Qt.AlignLeft)
        # Info Button
        self.mergeInfo = QPushButton(self.centralwidget)
        self.mergeInfo.setIcon(infoIcon)
        self.mergeInfo.setToolTip("This operation will merge the meshes into a single object" + \
                                  "\nThis is useful for when you do not care about part components")
        self.mergeInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.mergeInfo, 7, 0, 1, 1, Qt.AlignRight)
        # Clean Up Button
        self.mergeButton = QPushButton(self.centralwidget)
        self.mergeButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.mergeButton.setText("      Merge     ")
        self.mergeButton.clicked.connect(self.mergeRoutine)
        self.gridLayout.addWidget(self.mergeButton, 7, 3, 1, 1, Qt.AlignRight)
        # !-------------------Merge_END----------------------------------!
     
        # !-------------------REMOVE SMALL PARTS--------------------------------------!
        # Clean Up Label
        self.cleanLabel = QLabel(self.centralwidget)
        self.cleanLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.cleanLabel.setText("Remove small components: ratio range(0 -> 99.9)")
        self.gridLayout.addWidget(self.cleanLabel, 8, 1, 1, 1, Qt.AlignLeft)
        # Info Button
        self.cleanInfo = QPushButton(self.centralwidget)
        self.cleanInfo.setIcon(infoIcon)
        self.cleanInfo.setToolTip("This operation will remove all objects of a relative size which is compared to the models overall size." + \
                                  "\nThis is useful for removing objects such as screws, bolts and other small items.")
        self.cleanInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.cleanInfo, 8, 0, 1, 1, Qt.AlignRight)
        #Clean Up Input
        self.cleanInput = QLineEdit(self.centralwidget)
        self.cleanInput.setStyleSheet("QLineEdit{background-color: white;}")
        self.cleanInput.setFixedWidth(50)
        self.cleanInput.setFixedHeight(30)    
        font = self.cleanInput.font()
        font.setPointSize(12)
        self.cleanInput.setFont(font)
        self.cleanInput.setText("0.00")
        self.gridLayout.addWidget(self.cleanInput,8, 2, 1, 1, Qt.AlignLeft)
        # Clean Up Button
        self.cleanButton = QPushButton(self.centralwidget)
        self.cleanButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.cleanButton.setText("    Remove    ")
        self.cleanButton.clicked.connect(self.cleanRoutine)
        self.gridLayout.addWidget(self.cleanButton, 8, 3, 1, 1, Qt.AlignRight)
        # !-------------------REMOVE_SMALL_PARTS_END----------------------------------!
       
        # !-------------------DECIMATE------------------------------------------------!
        #Decimate Text
        self.decimateLabel = QLabel(self.centralwidget)
        self.decimateLabel.setStyleSheet("QLabel{ color: white; font: 16px;}")
        self.decimateLabel.setText("Input decimation: percentage range(0 -> 99.9)")
        self.gridLayout.addWidget(self.decimateLabel,9, 1, 1, 1, Qt.AlignLeft)
        # Info Button
        self.decimateInfo = QPushButton(self.centralwidget)
        self.decimateInfo.setIcon(infoIcon)
        self.decimateInfo.setToolTip("This operation will un-subdivide the triangle count of the model." + \
                                     "\nThe method uses 'edge-collapsing'. This will reduce overall model density.")
        self.decimateInfo.setStyleSheet("QPushButton{border: 0px}")
        self.gridLayout.addWidget(self.decimateInfo, 9, 0, 1, 1, Qt.AlignRight)
        #Decimate Input
        self.decimateInput = QLineEdit(self.centralwidget)
        self.decimateInput.setStyleSheet("QLineEdit{background-color: white;}")
        self.decimateInput.setFixedWidth(50)
        self.decimateInput.setFixedHeight(30)    
        font = self.decimateInput.font()
        font.setPointSize(12)
        self.decimateInput.setFont(font)
        self.decimateInput.setText("0.00")
        self.gridLayout.addWidget(self.decimateInput,9, 2, 1, 1, Qt.AlignLeft)
        # Decimate Button
        self.decimateButton = QPushButton(self.centralwidget)
        self.decimateButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.decimateButton.setText("   Decimate   ")
        self.decimateButton.clicked.connect(self.decimateRoutine)
        self.gridLayout.addWidget(self.decimateButton, 9, 3, 1, 1, Qt.AlignRight)
        # !-------------------DECIMATE-END---------------------------------------------!

        # !---------------------UNDO-----------------------------------------------!
        self.undoButton = QPushButton(self.centralwidget)
        self.undoButton.setObjectName("undo")
        self.undoButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 18px; padding: 6px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.undoButton.setText("Undo")
        self.undoButton.clicked.connect(self.undoRoutine)
        self.gridLayout.addWidget(self.undoButton,11, 3, 1, 1, Qt.AlignLeft)
        # !-------------------UNDO_END-----------------------------------------------!
                
        # !---------------------REDO-------------------------------------------------!
        self.redoButton = QPushButton(self.centralwidget)
        self.redoButton.setObjectName("redo")
        self.redoButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 18px; padding: 6px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.redoButton.setText("Redo")
        self.redoButton.clicked.connect(self.redoRoutine)
        self.gridLayout.addWidget(self.redoButton,11, 3, 1, 1, Qt.AlignRight)
        # !-------------------REDO_END-----------------------------------------------!

        # !---------------------SPACER-------------------------------------------------!
        self.spaceItem = QSpacerItem(10, 25, QSizePolicy.Expanding)
        self.gridLayout.addItem(self.spaceItem, 10, 1, 1, 1)
        # !---------------------SPACER_END----------------------------------------------!

        # !---------------------EXPORT-----------------------------------------------!
        self.proceedExportButton = QPushButton(self.centralwidget)
        self.proceedExportButton.setObjectName("proceedExport")
        self.proceedExportButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 18px; padding: 6px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
        self.proceedExportButton.setText("Proceed to Export")
        self.proceedExportButton.clicked.connect(self.exportRoutine)
        self.gridLayout.addWidget(self.proceedExportButton, 11, 0, 1, 4, Qt.AlignCenter)
        # !-------------------EXPORT_END---------------------------------------------!
        
        MainWindow.setCentralWidget(self.centralwidget)  
        self.retranslateUi(MainWindow)      

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QApplication.translate("MainWindow", "RMIT Control Window", None))

    def getStatCount(self):
        indexList = [3,2,4,5]
        defaultLayer = bpy.context.scene.view_layers['View Layer']
        sceneStatList = bpy.context.scene.statistics(defaultLayer).split("|")
        sceneStatCount = [sceneStatList[i] for i in indexList]
        fileName = os.path.basename(self.exportPath)
        statString = os.path.splitext(fileName)[0] + "".join(sceneStatCount)
        return statString

    # De-Parent Routine Call aka the Batman Routine Call
    def deparentRoutine(self):
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import deParent
            print("Starting Extract")
            startTime = [time.time()]
            deParent()
            print(timeUpdate(startTime, "Extract", 0))
            self.deParentButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
            self.statusLabel.setText("<b>   <font color='green'><center>Extract Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText(" <font color='red'>Flatten Node Tree: Failed:" + str(e) + "</font>")
        return
    
    # Split routine
    def splitRoutine(self):
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import splitModels
            print("Starting split")
            startTime = [time.time()]
            splitModels()
            print(timeUpdate(startTime, "Split", 0))
            self.deParentButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
            self.statusLabel.setText("<b>   <font color='green'><center>Split Model Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Split Models: Failed:" + str(e) + "</font>")
        return

    # Split routine
    def mergeRoutine(self):
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import mergeModels
            print("Starting merge")
            startTime = [time.time()]
            mergeModels()
            print(timeUpdate(startTime, "Merge", 0))
            self.deParentButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
            self.statusLabel.setText("<b>   <font color='green'><center>Merge Model Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Merge Models: Failed:" + str(e) + "</font>")
        return

    # Center Routine Call
    def centerRoutine(self):
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import centerModels
            print("Starting center models")
            startTime = [time.time()]
            centerModels()
            print(timeUpdate(startTime, "Center", 0))
            self.centerButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
            self.statusLabel.setText("<b>   <font color='green'><center>Center Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Center Models: Failed:" + str(e) + "</font>")
        return

    # Delete Routine Call
    def deleteRoutine(self):
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import deleteHidden
            print("Starting delete hidden")
            startTime = [time.time()]
            deleteHidden()
            print(timeUpdate(startTime, "Delete", 0))
            self.deleteButton.setStyleSheet("QPushButton{background-color: #606060; color: white; font: 16px; padding: 5px; \
                                                border-style: outset; border-color: white; border-radius: 6px; border-width: 1px;} \
                                                QPushButton:pressed {background-color: #303030; border-color: gray;}")
            self.statusLabel.setText("<b>   <font color='green'><center>Delete Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Delete Models: Failed:" + str(e) + "</font>")
        return

    # CleanUp Routine Call
    def cleanRoutine(self):
        try:
            if not self.cleanInput.text():
                raise TypeError("Please input a value")
            if float(self.cleanInput.text()) < 0:
                raise ValueError("Input can not be negative")
            if float(self.cleanInput.text()) > 99.99:
                raise ValueError("Input is out of bounds")
            self.statusLabel.setText(
                "\n\t     Import Complete\nPlease proceed with processing and export\n\n")
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import cleanUp
            print("Starting cleaning")
            startTime = [time.time()]
            cleanUp((float(self.cleanInput.text()) / 100))
            print(timeUpdate(startTime, "Clean up", 0))
            self.statusLabel.setText("<b>   <font color='green'><center>Clean Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Part Removal Failed:" + str(e) + "</font>")
        return

    # Decimation Routine Call
    def decimateRoutine(self):
        try:    
            if not self.decimateInput.text():
                raise TypeError("Please input a value")
            if float(self.decimateInput.text()) < 0:
                raise ValueError("Input can not be negative")
            if float(self.decimateInput.text()) > 99.99:
                raise ValueError("Input is out of bounds")
            self.statusLabel.setText(
                "\n\t     Import Complete\nPlease proceed with processing and export\n\n")
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import decimateModels
            print("Starting decimation")
            startTime = [time.time()]
            decimateModels((float(self.decimateInput.text()) / 100))
            print(timeUpdate(startTime, "Decimate", 0))
            self.statusLabel.setText( "<b>   <font color='green'><center> Decimate Function Successfully Ran</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Decimation Failed:" + str(e) + "</font>")
        return
 
    # Undo Routine Call
    def undoRoutine(self):
        bpy.context.view_layer.update()
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from operatorTest import AssembleOverrideContextForView3dOps
            oContext = AssembleOverrideContextForView3dOps()
            bpy.ops.ed.undo(oContext)
            self.statusLabel.setText( "<b>   <font color='green'><center> Undo Successful</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Undo Failed:" + str(e) + "</font>")
        return
   
    # Redo Routine Call
    def redoRoutine(self):
        bpy.context.view_layer.update()
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from operatorTest import AssembleOverrideContextForView3dOps
            oContext = AssembleOverrideContextForView3dOps()
            bpy.ops.ed.redo(oContext)
            self.statusLabel.setText( "<b>   <font color='green'><center> Redo Successful</center></font></b>Please proceed with processing and export<br>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Redo Failed:" + str(e) + "</font>")
        return
    
    # Export Routine Call
    def exportRoutine(self):
        bpy.context.view_layer.update()
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
            from processModels import apply_modifiers
            apply_modifiers()
            from importExport import exportModels            
            exportModels(self.exportPath)
            self.statusLabel.setText("<b>   <font color='green'><center>Export Complete</center></font></b>")
        except Exception as e:
            self.statusLabel.setText("<font color='red'>Export Failed:\nPerform an action prior to Export or Export manually</font>")
        return


class qt_window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        #Sets Ui_MainWindow to self.controls
        self.controls = Ui_MainWindow()
        self.controls.setupUi(self)
        
        self.show()
        #self._exec()

class PyQtEventLoopOp2(bpy.types.Operator):
    bl_idname = "wm.pyqt_event_loop2"
    bl_label = "PyQt Event Loop2"
    _timer = None
    _window = None
    exPath: bpy.props.StringProperty()

    # Modal with processEvents
    def modal(self, context, event):
        if event.type == 'TIMER':
            #Process the events for my qt stuff
            self.window.controls.sceneStatsLabel.setText(
                self.window.controls.getStatCount())
            self.window.controls.exportPath = self.exPath
            #self._event_loop.processEvents() #Removed because it was freezing the blender window
            self._application.sendPostedEvents(None, 0)
        return {'PASS_THROUGH'}

    def execute(self, context):
        # Create an instance of the window app
        self._application = QApplication.instance()
        # First object is named blender since at first it is none
        if self._application is None:
            self._application = QApplication(['blender'])
        
        self._event_loop = QEventLoop()
        self.window = qt_window()

        # Standard Blender Op Stuff
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

def timeUpdate(startTime, section, index):
    """
    Allows time logging of routines
    """
    elapsedTime = time.time() - startTime[index]
    tUpdate = section + " Time: " + str(elapsedTime) + " seconds"
    startTime.append(time.time())
    return tUpdate

def runController(path):
    try:
        bpy.utils.register_class(PyQtEventLoopOp2)
        bpy.ops.wm.pyqt_event_loop2('EXEC_DEFAULT',exPath=path)
        return True
    except:
        bpy.ops.wm.pyqt_event_loop2('EXEC_DEFAULT',exPath=path)
        return False

if __name__ == '<run_path>' or __name__ == '__main__':
    outputPath = r"\\AVR-E\Users\AVR\RMIT_Models\ML\FBX\testFBX\0A_ASEU_Mechanism_1.gltf"
    runController(outputPath)