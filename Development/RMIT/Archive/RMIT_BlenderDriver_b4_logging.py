"""
Author: Joseluis Chavez IT_C1
Date: 2/21/2019

Driver for RMIT: Rapid Model Import Tool

RMIT provides several functions

1. Import Engineering models into a a headless (NO GUI)
mode for processing
2. Pass arguments for decimation depending on model density.
3. Clean up model?
4. Export into a GLTF format. Thus ready for a game engine
"""
import sys
import os
import bpy
import time

# **Script uses blender python paths. We must add modules to sys path**
sys.path.append(os.path.dirname(__file__))
from Utils.ArgParserUtil import argEval
from Utils.import_catia_dae_v2 import update_file
from Utils.modelPrep import centerModels, deParent
from Utils.importExport import modelImport, exportModels, exportSections
from Utils.processModels import decimateModels, cleanUp, apply_modifiers

def resetBlend():
    """
    Clears the blender scene of objects, meshes and cameras....
    """
    override = bpy.context.copy()
    override['selected_objects'] = list(bpy.context.scene.objects)
    bpy.ops.object.delete(override)
    return

def timeUpdate(startTime, section, index, f):
    """
    Allows time logging, saved to time_log.txt
    """
    elapsedTime = time.time() - startTime[index]
    f.write(section + " Time: " + str(elapsedTime) + " seconds\n")
    startTime.append(time.time())
    return

def autoPilot():
    log_file = open('time_log.txt', 'w')    
    # Start up the automated processings.
    try:
        startTime = [time.time()]
        # Run command line through Argument Parser Utility.
        # This will capture the input and output files while starting up blender
        inputPath, outputPath, decRatio, cleanUpBool, loose, percent = argEval()

        # because vs code is addicted to caching
        #inputPath = "//AVR-E/Users/AVR/RMIT_Models/ML/FBX/testFBX/0A_ASEU_Mechanism_1.FBX"
        #outputPath = r"\\AVR-E\Users\AVR\RMIT_Models\ML\FBX\testFBX\0A_ASEU_Mechanism_1.gltf"
        #decRatio = percent = 0.0
        #cleanUpBool = None
        #loose = False
        #headless = sys.argv[1]

        # Clear the blender scene of all items.
        resetBlend()                                    # O(1)

        #-------------Routine 1: Start Import---------------#
        try:    
            modelImport(inputPath)
        except Exception as e:
            print("Aborting import, please check log file for error")
            log_file.write("\nImport Error: " +str(e)+ "\n")
        timeUpdate(startTime, "Import", 0, log_file)    # O(n)
        #-------------------End Import----------------------#


        #-------------Routine 2: Start Prep-----------------#
        try:    # Try to take objects to origin and apply transformations
            deParent()
            centerModels(loose)                  # O(n)
        except Exception as e:
            print("Aborting model prep, please check log file for error")
            log_file.write("\nModel Prep Error: " +str(e)+ "\n")
        #-------------------End Prep------------------------#


        #-------------Routine 3: Start Clean----------------#
        try:    # Try to clean up the objects in scene
            # TODO: See function for current issues
            # Delete tiny objects that are not needed
            if cleanUpBool:
                cleanUp(percent)                         # O(n)
        except Exception as e:
            print("Aborting clean up, please check log file for error")
            log_file.write("\nClean Up Error: " +str(e)+ "\n")
        #------------------End Clean------------------------#


        #-------------Routine 4: Start Decimate-------------#
        try:    # Try to decimate the models in the scene
            if decRatio > 0.09:
                decimateModels(decRatio)                 # O(n)
        except Exception as e:
            print("Aborting decimation, please check log file for error")
            log_file.write("\Decimation Error: " +str(e)+ "\n")
        timeUpdate(startTime, "Processing", 1, log_file)
        #------------------End Decimate---------------------#


         #-------------Routine 5: Start Apply Mods-------------#
        try:    # Try to apply the modifiers to the models prior to exporting
            # TODO: Add a checkpoint window that allows the user make last minute changes prior to export.
            if decRatio > 0.09:
                # TODO: replace with bpy.ops
                apply_modifiers()                       # O(n)
        except Exception as e:
            print("Aborting Apply Modifiers, please check log file for error")
            log_file.write("\Apply Mods Error: " +str(e)+ "\n")
        timeUpdate(startTime, "Apply Modifiers", 2, log_file)
        #-------------------End Apply Mods---------------------#
        

         #-------------Routine 6: Start Export-----------------#
        try:    # Try to export the models to a previously determined format
            exportModels(outputPath)                    # O(n)
        except Exception as e:
            print("Aborting import, please check log file for error")
            log_file.write("\Export Error: " +str(e)+ "\n")
        timeUpdate(startTime, "Export", 3, log_file)
        timeUpdate(startTime, "Total", 0, log_file)
         #------------------End Export-------------------------#

    except Exception as e:
        print(e)
        log_file.write("\nScript Error: " +str(e)+ "\n")
    print("RMIT Processing is complete")
    log_file.close()
    return

def manualDriver():
    # This is the argument for blenders headless mode
    if sys.argv[1] == '-b':
        autoPilot()
        return

    # Begins processing
    log_file = open('time_log.txt', 'w')

    # Check if PyQt5 is available, otherwise go autopilot
    PyQt5 = False
    try:
        from Utils import controlWindow
        PyQt5 = True
    except ImportError as e:
        print(e)
        log_file.write("\n PyQt5 error, going autopilot captain: " +str(e)+ "\n")
        autoPilot()
    
    # Toggle the console
    try:   
        bpy.ops.wm.console_toggle() #Double call sends it to blender and then in front of gui.
        bpy.ops.wm.console_toggle() #Requires the correct context. Add logic to ensure this.
    except Exception as e:
        print("Wrong context error for console")
    
    # Start up the controlled processings.
    try:
        startTime = [time.time()]

        # Run command line through Argument Parser Utility.
        # This will capture the input and output files while starting up blender
        inputPath, outputPath, decRatio, cleanUpBool, loose, percent = argEval()

        # because vs code is addicted to caching
        #inputPath = "//AVR-E/Users/AVR/RMIT_Models/ML/FBX/testFBX/0A_ASEU_Mechanism_1.FBX"
        #outputPath = r"\\AVR-E\Users\AVR\RMIT_Models\ML\FBX\testFBX\0A_ASEU_Mechanism_1.gltf"

        # Clear the blender scene of all items.
        resetBlend()                                    # O(1)

        #-------------Routine 1: Start Import---------------#
        try:    
            modelImport(inputPath)
        except Exception as e:
            print("Aborting import, please check log file for error")
            log_file.write("\nImport Error: " +str(e)+ "\n")
        timeUpdate(startTime, "Import", 0, log_file)    # O(n)
        #-------------------End Import----------------------#

        #-------Transfer Control to RMIT Control Window-----#
        try:
            controlWindow.runController(outputPath)
        except Exception as e:
            print("Control window failed: " + str(e))
        #--------------End Control Window-------------------#

        # Show status window if it imports it's available
        #if PyQt5 is True:
            #from Utils.testPyQt import using_q_runnable
            #using_q_runnable()
    except Exception as e:
        print(e)
        log_file.write("\nScript Error: " +str(e)+ "\n")
    
    log_file.close()
    return

manualDriver()
