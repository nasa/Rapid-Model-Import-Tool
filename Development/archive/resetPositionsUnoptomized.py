import bpy
import mathutils
import bmesh
from mathutils import Vector
from mathutils import Matrix

def setOriginPosition(ob, pos):
    # get displacement of object
    #print()
    displacement = ob.matrix_world.translation - pos
    #print(displacement)
    
    # multiply displacement by object's local to world matrix's inverse
    #print()
    world = Matrix.copy(ob.matrix_world)
    Matrix.invert(world)
    #print(world)
    
    #print()
    world = Matrix.to_3x3(world)
    #print(world)
    
    #print()
    dis = world @ displacement
    #print(dis)
    mat = Matrix.Translation(dis)
    
    # apply transformation
    me = ob.data
    #print()
    #print(ob.matrix_world)
    me.transform(mat)
    #print(ob.matrix_world)

    # update data and return object to location
    me.update()
    ob.matrix_world.translation = pos
    
    #print()
    #print(ob.location)
    #print(pos)


# reset Object origins (by average vertex location)
def resetObjectOrigins():
    #print()
    for o in bpy.data.objects:        
        # check if object has mesh
        verts = []
        if o.type == 'MESH':
            verts = o.data.vertices
        
        # calculate object's center
        numVerts = 0
        avgPos = Vector((0,0,0))
        for v in verts:
            numVerts += 1
            avgPos += o.matrix_world @ v.co
            #print(o.matrix_world @ v.co)

        # update object's origin (if mesh)
        if numVerts != 0:
            avgPos /= numVerts
            setOriginPosition(o,avgPos)


# reset all objects to the origin (by average position)
def resetObjectPositions():
    # reset origins of all objects to object
    #print()
    resetObjectOrigins()
    #print()
    
    # calculate center of all objects
    numObjects = 0
    avgPos = Vector((0,0,0))
    for o in bpy.data.objects:
        numObjects += 1
        avgPos += o.location
        #print(avgPos)
        #print(i.location)

    # move all objects to origin based on calculated objects center
    #print()
    #print(avgPos)
    #print(i.location)
    if numObjects != 0:
        #print(avgPos)
        avgPos /= numObjects
        #print(avgPos)
        for o in bpy.data.objects:
            #print(o.matrix_world)
            o.matrix_world = Matrix.Translation(-avgPos) @ o.matrix_world
            #print(o.matrix_world)

            
            # zero out transform (of meshes only)
            
            if o.type == 'MESH':
                #print(o.matrix_world)
                for v in o.data.vertices:
                    v.co = o.matrix_world @ v.co
                
                o.matrix_world = Matrix.Identity(4)
        

print()
resetObjectPositions()