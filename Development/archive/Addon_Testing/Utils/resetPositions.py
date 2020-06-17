import bpy
import mathutils
import bmesh
from mathutils import Vector
from mathutils import Matrix

from .deParentinator import deParent


# reset all objects to the origin (by average position)
def resetObjectPositions():
    # de parent all objects
    deParent()

	# function vars
    objCenters = {}
    center = Vector((0,0,0))
    numObjects = 0

    # loop 1: Get the centers
    for o in bpy.data.objects:
        # skip non mesh objects when calculating
        if o.type != 'MESH':
            continue
        else:
            numObjects += 1
            numVerts = 0
            objCenters[o.name_full] = Vector((0,0,0))
            for v in o.data.vertices:
                numVerts += 1
                objCenters[o.name_full] += o.matrix_world @ v.co

            if numVerts > 0:
                objCenters[o.name_full] /= numVerts
                center += objCenters[o.name_full]

    if numObjects <= 0:
        return

    center /= numObjects

    # loop 2: apply the centers
    centerMat = Matrix.Translation(-center)
    for o in bpy.data.objects:
        if o.type != 'MESH':
            o.location -= center
        else:
            # generate center origin matrix
            worldInvert = Matrix.copy(o.matrix_world)
            Matrix.invert(worldInvert)
            worldInvert.translation = Vector((0,0,0))
            dis = worldInvert @ (o.matrix_world.translation - objCenters[o.name_full])
            origin = Matrix.Translation(dis)

            # apply transformations
            # move to center @ zero transformations @ recenter object's origin
            o.matrix_world.translation = objCenters[o.name_full]
            o.data.transform(centerMat @ o.matrix_world @ origin)
            o.matrix_world = Matrix.Identity(4)
            o.data.update()


if __name__ == "<run_path>" or __name__ == "__main__":
    print()
    resetObjectPositions()