"""
Author: Joseluis Chavez IT_C1
Date: 2/21/2019
0
Driver for RMIT: Rapid Model Import Tool

RMIT provides several functions

1. Import Engineering models into a a headless (NO GUI)
mode for processing
2. Pass arguments for decimation depending on model density.
3. Clean up model
4. Export into a GLTF format. Thus ready for a game engine
"""
import sys
import os
import bpy
import time
import logging
import pathlib
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


# **Script uses blender python paths. We must add modules to sys path**
try:
    sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + r"\lib" + r"\Utils")
    from ArgParserUtil import argEval
    from import_catia_dae_v2 import update_file
    from importExport import modelImport, exportModels, exportSections
    from processModels import *
    import errorLog as err
except Exception:
    sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + r"\Utils")
    from ArgParserUtil import argEval
    from import_catia_dae_v2 import update_file
    from importExport import modelImport, exportModels, exportSections
    from processModels import *
    import errorLog as err

def resetBlend():
    """
    Clears the blender scene of objects, meshes and cameras....
    """
    override = bpy.context.copy()
    override['selected_objects'] = list(bpy.context.scene.objects)
    bpy.ops.object.delete(override)
    return

def timeUpdate(startTime, section, index):
    """
    Allows time logging of routines
    """
    elapsedTime = time.time() - startTime[index]
    tUpdate = section + " Time: " + str(elapsedTime) + " seconds"
    startTime.append(time.time())
    return tUpdate

def autoPilot():
    # Establish logging for blender code
    logger = logging.getLogger(__name__)
    
    logger.info("Starting autopilot") 
    # Start up the automated processings.
    try:
        startTime = [time.time()]
        # Run command line through Argument Parser Utility.
        # This will capture the input and output files while starting up blender
        inputPath, outputPath, dec, decPercent, clean, cleanPercent, hidden, flatten, merge, center, split = argEval()
        logger.debug("Args: %s, %s, %s, %d, %s, %d, %s, %s, %s, %s, %s" % (
            inputPath, outputPath, dec, decPercent, clean, cleanPercent, hidden, flatten, merge, center, split))

        # because vs code is addicted to caching
        #inputPath = "//AVR-E/Users/AVR/RMIT_Models/ML/FBX/testFBX/0A_ASEU_Mechanism_1.FBX"
        #outputPath = r"\\AVR-E\Users\AVR\RMIT_Models\ML\FBX\testFBX\0A_ASEU_Mechanism_1.gltf"
        #decRatio = percent = 0.0
        #cleanUpBool = None
        #loose = False
        #headless = sys.argv[1]

        # Clear the blender scene of all items.
        logger.debug("Try to reset blender scene")
        print("Try to reset blender scene")
        resetBlend()                                    # O(1)
        logger.info("Blender scene has been reset")
        print("Blender scene has been reset")

        #-------------Routine 1: Start Import---------------#
        logger.debug("Attempting to import the model")
        print("Attempting to import the model")
        try:    
            modelImport(inputPath)
        except Exception as e:
            logger.exception("Import Error:")
            print("Import Error")
            err.errorReport()
            exit(1)
            return
        logger.info(timeUpdate(startTime, "Import", 0))
        print(timeUpdate(startTime, "Import", 0))
        #-------------------End Import----------------------#
       


        #-------------Routine 2: Flatten-----------------#
        logger.debug("Attempting to flatten the model tree")
        print("Attempting to flatten the model tree")
        try:    # Try to take objects to origin and apply transformations
            if flatten:
                deParent()
            else:
                logger.debug("flatten skipped")
                print("flatten skippsed")                
        except Exception as e:
            logger.exception("Flatten Error:")
            print("Flatten Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Flatten", 1))
        print(timeUpdate(startTime, "Flatten", 1))
        #-------------------End Prep------------------------#

        #-------------Routine 3: delete hidden----------------#
        logger.debug("Attempting to delete hidden")
        print("Attempting to delete hidden")
        try:    # Try to take objects to origin and apply transformations
            if hidden:
                deleteHidden()
            else:
                logger.debug("delete hidden skipped")
                print("delete hidden skipped")                
        except Exception as e:
            logger.exception("Delete hidden error:")
            print("Delete hidden error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Hidden", 2))
        print(timeUpdate(startTime, "Hidden", 2))
        #-------------------End Prep------------------------#

        #-------------Routine 4: split mesh----------------#
        logger.debug("Attempting to split mesh")
        print("Attempting to split mesh")
        try:    # Try to take objects to origin and apply transformations
            if split:
                splitModels()
            else:
                logger.debug("split mesh skipped")
                print("split mesh skipped")                
        except Exception as e:
            logger.exception("Split error:")
            err.errorReport("Split error")
        logger.info(timeUpdate(startTime, "Split", 3))
        print(timeUpdate(startTime, "Split", 3))
        #-------------------End Prep------------------------#

        #-------------Routine 5: Start Clean----------------#
        logger.debug("Attempting to remove small objects")
        print("Attempting to remove small objects")
        try:    # Try to clean up the objects in scene
            if clean:
                cleanUp(cleanPercent)    
            else:
                logger.debug("remove small objects skipped")
                print("remove small objects skipped")        
        except Exception as e:
            logger.exception("CleanUp Error:")
            print("CleanUp Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "CleanUp", 4))
        print(timeUpdate(startTime, "CleanUp", 4))
        #------------------End Clean------------------------#
  

         #-------------Routine 6: Merge objects----------------#
        logger.debug("Attempting to merge objects")
        print("Attempting to merge objects")
        try:    # Try to clean up the objects in scene
            if merge:
                mergeModels()         
            else:
                logger.debug("merge objects skipped")
                print("merge objects skipped")     
        except Exception as e:
            logger.exception("Merge Error:")
            print("Merge Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Merge", 5))
        print(timeUpdate(startTime, "Merge", 5))
        #------------------End Clean------------------------#    


        #-------------Routine 7: Center object----------------#
        logger.debug("Attempting to center objects")
        print("Attempting to center objects")
        try:    # Try to clean up the objects in scene
            if center:
                centerModels()
            else:
                logger.debug("center objects skipped")
                print("center objects skipped") 
        except Exception as e:
            logger.exception("Center Error:")
            print("Center Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Center", 6))
        print(timeUpdate(startTime, "Center", 6))
        #------------------End Clean------------------------#     

        #-------------Routine 8: Start Decimate-------------#
        logger.debug("Attempting to decimate the model")
        print("Attempting to decimate the model")
        try:    # Try to decimate the models in the scene
            if dec:
                print(decPercent)
                decimateModels(decPercent)                 # O(n)
            else:
                logger.debug("decimate the model skipped")
                print("decimate the model skipped") 
        except Exception as e:
            logger.exception("CleanUp Error:")
            print("CleanUp Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Decimation", 7))
        print(timeUpdate(startTime, "Decimation", 7))
        #------------------End Decimate---------------------#


         #-------------Routine 9: Start Apply Mods-------------#
        logger.debug("Attempting to apply modifiers")
        print("Attempting to apply modifiers")
        try:    # Try to apply the modifiers to the models prior to exporting
            if dec:
                # TODO: replace with bpy.ops
                apply_modifiers()                       # O(n)
            else:
                logger.debug("apply modifiers skipped")
                print("apply modifiers skipped") 
        except Exception as e:
            logger.exception("Apply modifiers Error:")
            print("Apply modifiers Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Apply Mods", 8))
        print(timeUpdate(startTime, "Apply Mods", 8))
        #-------------------End Apply Mods---------------------#
        

        #-------------Routine 10: Start Export-----------------#
        logger.debug("Attempting to export model")
        print("Attempting to export model")
        try:    # Try to export the models to a previously determined format
            checkSelection()
            exportModels(outputPath)                    # O(n)
        except Exception as e:
            logger.exception("Export Model Error:")
            print("Export Model Error")
            err.errorReport()
        logger.info(timeUpdate(startTime, "Export", 9))
        print(timeUpdate(startTime, "Export", 9))
        logger.info(timeUpdate(startTime, "Total", 0))
        print(timeUpdate(startTime, "Total", 0))
         #------------------End Export-------------------------#

    except Exception as e:
        print(e)
        logger.exception("RMIT auto pilot failed: ")
        exit(1)
        return False
    print("RMIT Auto Processing is Complete")
    exit(0)
    return True

def manualDriver():
    # Establish logging for blender code
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)   
    formatter = logging.Formatter('%(module)s : %(lineno)d : %(asctime)s : %(levelname)s : %(message)s')    
    file_handler = logging.FileHandler('RMIT.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)  
    logger.addHandler(file_handler)
    
    # This is the argument for blenders headless mode
    if sys.argv[1] == '-b':
        return autoPilot()

    # Check if PyQt5 is available, otherwise go autopilot
    logger.debug("Starting up RMIT and importing modules")
    PyQt5 = False
    try:
        try:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + r"\lib" + r"\Utils")
            import controlWindow
        except Exception:
            sys.path.append(str(pathlib.Path(__file__).parent.resolve()) + r"\Utils")
            import controlWindow
        PyQt5 = True
    except ImportError as e:
        logger.exception("PyQt5 error, going autopilot captain:")
        #log_file.write("\n PyQt5 error, going autopilot captain: " +str(e)+ "\n")
        autoPilot()
        bpy.ops.wm.console_toggle() #Double call sends it to blender and then in front of gui.
        bpy.ops.wm.console_toggle() #Requires the correct context. Add logic to ensure this.
        print("If you reached here. The control window failed to start. Check the logs.")
        exit(1)
        return
    
    # Toggle the console
    try:   
        bpy.ops.wm.console_toggle() #Double call sends it to blender and then in front of gui.
        bpy.ops.wm.console_toggle() #Requires the correct context. Add logic to ensure this.
        logger.info("Console context is correct.")
    except Exception as e:
        logger.exception("Wrong context error for console.")
        err.errorReport()
        #print("Wrong context error for console")
    logging.info("Start up is complete")

    # Start up the controlled processings.
    try:
        logger.debug("Gathering variables from sys\n")
        startTime = [time.time()]

        try:
            # Run command line through Argument Parser Utility.
            # This will capture the input and output files while starting up blender
            logger.debug("Incoming args: %s\n" % sys.argv)
            inputPath, outputPath, dec, decPercent, clean, cleanPercent, hidden, flatten, merge, center, split = argEval()
            logger.debug("Args: %s, %s, %s, %d, %s, %d, %s, %s, %s, %s, %s" % (
                inputPath, outputPath, dec, decPercent, clean, cleanPercent, hidden, flatten, merge, center, split))
        except Exception as e:
            logger.exception("Failed to get arguments from RMIT GUI. Aborting")
            err.errorReport()
            exit(1)
            return

        # Clear the blender scene of all items.
        logger.debug("Try to reset blender scene")
        resetBlend()                                    # O(1)
        logger.info("Blender scene has been reset")

        #-------------Routine 1: Start Import---------------#
        logger.debug("Attempting to import the model")
        try:  
            modelImport(inputPath)
        except Exception as e:
            logger.exception("Import Error:")
            err.errorReport()
            exit(1)
            return
        logger.info(timeUpdate(startTime, "Import", 0))
        #-------------------End Import----------------------#
        
        #Save current import state
        bpy.ops.ed.flush_edits()
        overrideContext = AssembleOverrideContextForView3dOps()

        #-------Transfer Control to RMIT Control Window-----#
        logger.debug("Attempting to run Control Window")
        try:
            controlWindow.runController(outputPath)
            logger.info("Control Window is a go. Proceed to process")
        except Exception as e:
            logger.exception("Control window failed")
            err.errorReport()
        #--------------End Control Window-------------------#
        #this closes: exit(0)

    except Exception as e:
        logger.exception("Script Error:")
        err.errorReport()
    #exit(0)
    if -10010 == int(decPercent) and -11100 == cleanPercent:
        exit(0)
    return

manualDriver()