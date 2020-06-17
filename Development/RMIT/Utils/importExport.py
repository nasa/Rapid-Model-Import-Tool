import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
from import_catia_dae_v2 import update_file
from operatorTest import AssembleOverrideContextForView3dOps
from processModels import checkSelection, scaleModels
import bpy
import os
import re
from datetime import datetime


def modelImport(inputPath):
    """
    Imports the model depending on the extension type.

    Parameters
    ----------
    param1 (str): path of the input file

    Returns
    -------
    """
    overrideContext = AssembleOverrideContextForView3dOps()
    # Temp change context to View_3D to use importer.
    # Not needed if ran from command line?????
    if bpy.context.area is not None:
        area = bpy.context.area
        old_type = area.type
        area.type = 'VIEW_3D'

    if ".obj" in inputPath or ".OBJ" in inputPath:
        bpy.ops.import_scene.obj(filepath=inputPath)
    elif ".fbx" in inputPath or ".FBX" in inputPath:
        bpy.ops.import_scene.fbx(filepath=inputPath)
    elif ".glb" in inputPath or ".GLB" in inputPath or "gltf" in inputPath or "GLTF" in inputPath:
        bpy.ops.import_scene.gltf(filepath=inputPath)
    elif ".ply" in inputPath or ".PLY" in inputPath:
        bpy.ops.import_mesh.ply(filepath=inputPath)
    elif ".stl" in inputPath or ".STL" in inputPath:
        bpy.ops.import_mesh.stl(filepath=inputPath)
    elif ".dae" in inputPath or ".DAE" in inputPath:
        # Process through Arjun script to update dae to newest standards
        tempDAE = update_file(inputPath)
        bpy.ops.wm.collada_import(filepath=inputPath)
        os.remove(tempDAE)
    else:
        raise RuntimeError("Unknown extension: %s" %
                           os.path.splitext(inputPath)[1])
        return False
        
    bpy.ops.view3d.view_all(overrideContext)
    #We do not want everything selected
    bpy.ops.object.select_all(action='DESELECT')
    return True

def exportModels(outputPath):
    """
    Exports the scene into a GLTF format.

    Parameters:
    ----------
    param1 (str): path of the export file
    Returns
    -------
    """
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Export")
    overrideContext['selected_objects'] = checkSelection()
    if ".gltf" in outputPath:
        bpy.ops.export_scene.gltf(overrideContext,
            filepath=outputPath,
            export_format='GLTF_SEPARATE',export_selected=True)
    elif ".fbx" in outputPath:
        bpy.ops.export_scene.fbx(overrideContext,
            filepath=outputPath, bake_space_transform=False,use_selection=True)
    elif ".dae" in outputPath:
        bpy.ops.wm.collada_export(overrideContext,
            filepath=outputPath,selected=True)
    elif ".obj" in outputPath:
        bpy.ops.export_scene.obj(overrideContext,
            filepath=outputPath,use_selection=True)
    elif ".stl" in outputPath:
        bpy.ops.export_mesh.stl(overrideContext,
            filepath=outputPath,use_selection=True)
    else:
        raise RuntimeError("File path/extension not valid")
        return False
    return True

def exportSections(filepath):
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Export Sections")

    startTime = datetime.now()

    # make containing folder
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    
    # deselect all objects
    for o in bpy.data.objects:
        o.select_set(False)

    # create variables used throughout export
    name = 0
	
	# poly count is tris because decimate has triangulate
    polyCount = 0
    start = 0

    # export in sections
    objLength = len(bpy.data.objects)
    for i in range(objLength):
        # add object
        o = bpy.data.objects[i]
        if o.type == "MESH":
            o.select_set(True)
            polyCount += len(o.data.polygons)
            
            # check polycount
            if polyCount >= 1000000 or i >= objLength - 1:
                # export with next name
                name += 1
                bpy.ops.export_scene.gltf(overrideContext,
                    filepath=filepath + str(name), 
                    export_format='GLTF_SEPARATE', 
                    export_selected=True)
                
                # deselect selected objects
                for j in range(start, i+1):
                    bpy.data.objects[j].select_set(False) # setter not list set

                # reset for next export
                start = i+1
                polyCount = 0
    
    print('took ' + str((datetime.now() - startTime).seconds) + ' seconds total to export to ' + str(name) + ' files')
    return

# code for running with VS Code or from inside blender
if __name__ == '<run_path>' or __name__ == '__main__':
    inputPath = r"\\AVR-E\Users\AVR\RMIT_Models\Test_Models\inputs\Manlift.dae"
    outputPath = r"\\AVR-E\Users\AVR\RMIT_Models\Test_Models\inputs\Manlift.gltf"
    testExportPath = r'\\AVR-E\Users\AVR\RMIT_Models\Test_Models\outputs'
    #modelImport(inputPath)
    exportModels(outputPath)
    #exportSections(testExportPath)