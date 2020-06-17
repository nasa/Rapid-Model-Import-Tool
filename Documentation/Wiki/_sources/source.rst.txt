Source
=======================

Below you will find the documentation for the code of this project.

GUI - RMITGUIProcess.py
------------------------------

This file utilizes the PyQt5 library to create the main GUI interface of RMIT.

 **Functions:**

    .. py:function:: setupUi(self, MainWindow)

    Description: Creates the GUI window.

    .. py:function:: retranslateUi(self, MainWindow)

    Description: Handles the resizing of the window to keep the GUI the same.

    .. py:function:: getFile(self)

    Description: Button used to pick a valid file for processing.

    .. py:function:: setOutput(self)

    Description: Button used to set output for file.

    .. py:function:: sliderChange(self, value)

    Description: GUI slider for the decimation option. Works in 10% increments.

    .. py:function:: btnstate(self,b)

    Description: Records the user choice of decimation and if in headless mode.

    .. py:function:: processFile(self)

    Description: Processes the selected file through Blender.




Driver - RMIT_BlenderDriver.py
------------------------------

This is the file that is injected into Blender and ran through its python interface.

 **Functions:**

    .. py:function:: resetBlend()

    Description: Clears the Blender scene of objects, meshes, cameras, etc.

    .. py:function:: timeUpdate(startTime, section, index)

    Description: Allows time logging of routines.

    .. py:function:: autopilot()

    Description: This takes in the arguments sent through ArgParserUtil.py and runs the settings given. This is only ran in headless mode.

    .. py:function:: smanualDriver()

    Description: This launches the GUI interface in Blender for running RMIT as normal.


Unit Test - RMIT_UnitTest.py
------------------------------

This file tests all the different use cases of RMIT to ensure stability at build.

 **Functions:**

    .. py:function:: suite(fileInput)

    Description: This runs through all the given tests and returns what passed and failed.


Setup - setup.py
------------------------------

This file builds the executable of RMIT.


Utils - /Utils
------------------------------
 ArgParserUtil.py
 *****************

Take the arguments from RMITGUIProcess and outputs them as their return values to RMIT_BlenderDriver.

 **Functions:**

    .. py:function:: argEval()

    Description: Get the args passed to blender after "--", all of which are ignored by blender so scripts may receive their own arguments.

controlWindow.py
****************

GUI that is spawned within Blender that runs various functions.

 **Functions:**

    .. py:function:: setupUi()

    Description: Creates the main window for the GUI

    .. py:function:: deparentRoutine(self)

    Description: De-Parent Routine runs the :ref:`Flatten Model Tree function<Flatten Model Tree>`. 

    .. py:function:: centerRoutine(self)

    Description: Center Routine runs the :ref:`Center Model function<Center Model>`. 

    .. py:function:: deleteRoutine(self)

    Description: Delete Routine runs the :ref:`Delete Hidden Objects function<Delete Hidden Objects>`. 

    .. py:function:: cleanRoutine(self)

    Description: Clean Routine runs the :ref:`Clean Small Components function<Clean up/Remove Small Components>`.

    .. py:function:: decimateRoutine(self)

    Description: Decimate Routine runs the :ref:`Decimation function<Decimation>`. 

    .. py:function:: exportRoutine(self)

    Description: Runs the export function based on input originally given by user.

errorLog.py
************

Creates a new GUI for error reporting and then opens an email interface.

 **Functions:**

    .. py:function:: errorReport()

    Description: Creates the main window for the GUI
    
    .. py:function:: b_crash()

    Description: Detects if there is a Blender crash file and returns true if there is.

    .. py:function:: on_click()

    Description: Grabs the latest info from the log file and creates a prompt for the user to email it to support.



import_catia_dae_v2.py
**********************

Processes a .dae file for import into Blender


importExport.py
****************

Both import and exports based on information given by the user.

 **Functions:**

    .. py:function:: modelImport(inputPath)

    Description: Imports the model depending on the extension type.

    .. py:function:: exportModels(filePath)

    Description: Exports the scene into a GLTF format by default, can be changed by user.

    .. py:function:: exportSelections(filePath)

    Description: Exports the user's selection into a GLTF format by default, can be changed by user.



modelPrep.py
*************

Contains most functions for model manipulation.

 **Functions:**

    .. py:function:: flatten(o)

    Description: Flatten executes the :ref:`Flatten Model Tree function<Flatten Model Tree>`. 

    .. py:function:: deParent()

    Description: De-Parent prepares the model for the :ref:`Flatten Model Tree function<Flatten Model Tree>`. 

    .. py:function:: centerModels(sepByLoose)

    Description: Center executes the :ref:`Center Model function<Center Model>`. 

    .. py:function:: deleteHidden()

    Description: Delete Hidden executes the :ref:`Delete Hidden Objects function<Delete Hidden Objects>`. 


operatorTest.py
****************

 **Functions:**

    .. py:function:: AssembleOverrideContextForView3dOps()

    Description: Iterates through the blender GUI's windows, screens, areas, regions to find the View3D space and its associated window.  Populate a 'oContextOverride context' that can be used with bpy.ops that require to be used from within a View3D (like most addon code that runs of View3D panels)

    .. py:function:: TestView3dOperatorFromPythonScript()

    Description: Run this from a python script and operators that would normally fail because they were not called from a View3D context will work.

processModels.py
*****************

 **Functions:**

    .. py:function:: apply_modifiers()

    Description: Executes all the modifies the user as selected

    .. py:function:: decimateModels(decRatio)

    Description: Decimate the models in the scene given
   
    .. py:function:: cleanUp(percent)

    Description: Removes all small objects such as screws from the scene.
        
    1. Record bounding box of the scene.
    2. Calculate percentage threshold for removal
    3. Compare items to removal threshold and mark for deletion
    4. Delete small object under threshold
 


