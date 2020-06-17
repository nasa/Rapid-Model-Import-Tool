import bpy
import os
import bpy
import time
import math

from .Utils.ArgParserUtil import argEval
from .Utils.import_catia_dae_v2 import update_file
from .Utils.resetPositions import resetObjectPositions

def resetBlend():
    """
    Clears the blender scene of objects, meshes and cameras.
    """
    override = bpy.context.copy()
    override['selected_objects'] = list(bpy.context.scene.objects)
    bpy.ops.object.delete(override)
    return

def importModels(inputPath):
    """
    Imports the model depending on the extension type.

    Parameters
    ----------
    param1 (str): path of the input file

    Returns
    -------
    """
    if ".obj" in inputPath:
        bpy.ops.import_scene.obj(filepath=inputPath)
    elif ".fbx" in inputPath:
        bpy.ops.import_scene.fbx(filepath=inputPath)
    elif ".ply" in inputPath:
        bpy.ops.import_mesh.ply(filepath=inputPath)
    elif ".stl" in inputPath:
        bpy.ops.import_mesh.stl(filepath=inputPath)
    elif ".dae" in inputPath:
        # Process through Arjun script to update dae to newest standards
        tempDAE = update_file(inputPath)
        bpy.ops.wm.collada_import(filepath=tempDAE)
        os.remove(tempDAE)
    else:
        raise RuntimeError("Unknown extension: %s" %
                        os.path.splitext(inputPath)[1])
    return


def decimateModels(decRatio):
    """
    Decimate the models in the scene given.

    Parameters:
    ----------
    param1 (str): Decimation Ratio: This is range from 0.0 > 0.9
    Returns
    ----------
    """
    # switch from decimation loss perspective to remaining perspective
    decRatio = 1 - decRatio

    for obj in bpy.data.objects:
        # Get dimensions for possible cleanup
        x = obj.dimensions[0]
        y = obj.dimensions[1]
        if obj.type == "MESH":
            modDec = obj.modifiers.new("Decimate", type="DECIMATE")
            ## modDec.face_count == 0 ??
            face_count = len(obj.data.polygons)
            if (face_count > 0):
                # function to increase poly reduction on higher poly models
                # but reduce reduction on lower ones (compared to decRatio * startfaces)
                # endfaces = startfaces ^ ((8 + 2 * decRatio) / 10)
                target_face_count = math.ceil(math.pow(face_count, (8 + 2 * decRatio) / 10))
                modDec.ratio = target_face_count / float(face_count)

            modDec.use_collapse_triangulate = True
    #Scene update causes blender to slow down over time. Use outside loops and only when necessary.
    # https://blenderartists.org/t/python-slowing-down-over-time/569534/7 
    bpy.context.view_layer.update()
    return


def cleanUp():
    """
    Removes all small objects such as screws from the scene.
    Utility calls scene objects, thus no input or output.

    Paramaters:
    ----------
    ----------
    """
    for obj in bpy.context.scene.objects:
        x = obj.dimensions[0]
        y = obj.dimensions[1]

        if obj.type == "MESH":
            if x < 0.2 and y < 0.2:
                modDec = obj.modifiers.new("Decimate", type="DECIMATE")
                if modDec.face_count > 500:
                    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.update()
    return


def exportModels(outputPath):
    """
    Exports the scene into a GLTF format.

    Parameters:
    ----------
    param1 (str): path of the export file
    Returns
    -------
    """
    if ".gltf" in outputPath:
        # rips the extension out before saving as a glb
        # we hard set some defaults for our exporter
        bpy.ops.export_scene.gltf(
            filepath=os.path.splitext(outputPath)[0],
            export_format='GLTF_SEPARATE', export_apply=True)
    elif ".fbx" in outputPath:
        bpy.ops.export_scene.fbx(
            filepath=outputPath)
    elif ".dae" in outputPath:
        bpy.ops.wm.collada_export(
            filepath=outputPath)
    elif ".obj" in outputPath:
        bpy.ops.export_scene.obj(
            filepath=outputPath)
    else:
        raise RuntimeError("File path/extension not valid")
    return


class BlenderDriver(bpy.types.Operator):
    bl_label = "Blender Driver"
    bl_idname = "rmit.run"
    bl_description = "RMIT Driver"

    # these are the command line parameters
    # use self.<param> to access in execute
    inputPath: bpy.props.StringProperty(name="inputPath", default=os.path.join(os.getcwd(), r"E:\Ben Fairlamb\inputs\CM Int & Ext.fbx"))
    outputPath: bpy.props.StringProperty(name="outputPath", default=os.path.join(os.getcwd(), r"E:\Ben Fairlamb\outputs\CM Int & Ext.gltf"))
    decRatio: bpy.props.FloatProperty(name="decRatio", default=0.5)
    cleanUp: bpy.props.BoolProperty(name="cleanUp", default=False)

    # Total Complexity: O(5n)
    def execute(self, context):
        startTime = time.time()
        # Run command line through Argument Parser Utility.
        #inputPath, outputPath, decRatio, cleanUpBool = argEval()
        # This is now done in starter script and passed in as params

        # Clear the blender scene of all items.
        resetBlend()                            # O(n)

        # Import the models based on their file type
        importModels(self.inputPath)                 # O(n)

        # Delete tiny objects that are not needed
        if self.cleanUp is True:
            cleanUp()                           # O(n)

        # Decimate models to a count between 2k and 1k per part
        if self.decRatio > 0.09:
            decimateModels(self.decRatio)            # O(n)


        # set objects to origin and apply transformations
        resetObjectPositions()                  # O(n)

        # Export the models based on their file type
        # exportModels(self.outputPath)                # O(n)

        elapsedTime = time.time() - startTime
        print("\nTime it took: " + str(elapsedTime) + "\n")

        return {'FINISHED'}