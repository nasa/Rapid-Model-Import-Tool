import bpy
from datetime import datetime
import os

def exportSections(filepath):
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
                bpy.ops.export_scene.gltf(filepath=filepath + str(name), export_format='GLTF_SEPARATE', export_selected=True)
                
                # deselect selected objects
                for j in range(start, i+1):
                    bpy.data.objects[j].select_set(False) # setter not list set

                # reset for next export
                start = i+1
                polyCount = 0
    
    print('took ' + str((datetime.now() - startTime).seconds) + ' seconds total to export to ' + str(name) + ' files')

if __name__ == '<run_path>' or __name__ == '__main__':
    exportSections('E:\\Ben Fairlamb\\outputs\\Separate Test\\')