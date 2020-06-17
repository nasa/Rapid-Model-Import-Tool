import bpy
import bmesh
import math, time
import numpy as np
from mathutils import Matrix, Vector
import sys
import mathutils
import os
import pathlib
#sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))
from operatorTest import AssembleOverrideContextForView3dOps

def apply_modifiers():
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Apply Modifiers")

    # get evaluated dependency graph
    dg = bpy.context.evaluated_depsgraph_get()
    
    for o in bpy.data.objects:
        if o.type == 'MESH':
            # get objects evaluated form (with modifiers applied)
            o_eval = o.evaluated_get(dg)

            # remove modifiers
            o.modifiers.clear()

            # set current data to the version with modifiers applied 
            o.data = bpy.data.meshes.new_from_object(o_eval)
    return True

'''
Links similar/exact materials together
'''
def linkMaterials(objList):
    #Create empty dictionary materials, key will be roughness + color. Value will be an array of materials
    dictMaterials = {}
    for obj in objList:  
        #We only want things with materials
        if obj.type == "MESH":
            #Loop through all the materials in the object
            for mat in obj.material_slots.values():
                #getting the color values out
                color = [0,0,0]
                nodes = mat.material.node_tree.nodes
                principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
                color[0] = principled.inputs['Base Color'].default_value[0]
                color[1] = principled.inputs['Base Color'].default_value[1]
                color[2] = principled.inputs['Base Color'].default_value[2]
                name = str(mat.material.roughness + color[0] + color[1] + color[2])
                #Creating new entry if material does not exist
                if name not in dictMaterials:
                    matList = []
                    dictMaterials[name] = matList
                #inserting material
                dictMaterials[name].append(mat)
    #linking similar materials
    for matList in dictMaterials:
        for mat in dictMaterials[matList]:
            if mat != dictMaterials[matList][0]:
                mat.link = "OBJECT"
                mat.material = dictMaterials[matList][0].material
    return True




'''
Merges meshes, if none are selected merges all. Will merge the mesh to the highest object in the selection
'''
def mergeModels():
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext,message="Undo Decimate Models")

    # If user does not select, all objs are decimated. Otherwise, only dec the selected
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    # We want to know if the user selected all the objects or not
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False
        # select all objects
        for o in objList:
            if o.parent not in objList:
                #Lets see how many kids this object has, and select them
                selectAllChild(o)

    #Update object List
    objList = [o for o in bpy.context.scene.objects if o.select_get()]
    #Create empty list for knowing what to delete at a later time
    emptyList = []
    #merge similar materials
    linkMaterials(objList)
    #Setting up link object
    linkObj = None
    parObj = None
    #Finding what to merge and what to delete
    for obj in objList:  
        #Delete anything thats not a mesh
        if obj.type != "MESH":
            emptyList.append(obj)
            obj.select_set(False)
        #We need on random mesh object to merge as the "parent"
        else:
            linkObj = obj
    
    #Merging, if all the objects are empty will just delete them.
    if linkObj != None:
        overrideContext['selected_objects'] = objList
        overrideContext['active_object'] = linkObj
        bpy.ops.object.join(overrideContext)
        bpy.ops.object.join_uvs(overrideContext)   
        #Getting all currently selected objects and deselecting them
        selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
        for obj in selObjs:
            obj.select_set(False)
        #Finding parent object
        parObj = getParent(linkObj,objList)
        linkObj.select_set(True)
        #Deparenting
        deParent()
        overrideContext['selected_objects'] = linkObj
        overrideContext['active_object'] = parObj
        #Reparenting, these kids have been through a lot
        bpy.ops.object.parent_set(overrideContext, type="OBJECT")
    #Remove the empties
    for obj in emptyList:
        if obj.type == "EMPTY" and obj != parObj:
            bpy.data.objects.remove(obj, do_unlink=True)


    #If selected all then unselect all
    if (selectAll == True):
        bpy.ops.object.select_all(action='DESELECT')
    #Update
    bpy.context.view_layer.update()
    bpy.ops.ed.undo_push(overrideContext,message="Undo Decimate Models")
    return True

'''
Everyone loves recursion, finds the head of the object sent)
'''
def getParent(obj, objlist):
    if obj.parent not in objlist:
        return(obj)
    return getParent(obj.parent, objlist)

def decimateModels(decRatio):
    """
    Decimate the models in the scene given

    Parameters:
    ----------
    param1 (str): Decimation Ratio: This is range from 0.0 > 0.9
    Returns
    ----------
    """
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext,message="Undo Decimate Models")

    # If user does not select, all objs are decimated. Otherwise, only dec the selected
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
   
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False    
        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)

    objList = [o for o in bpy.context.scene.objects if o.select_get()]

    #Decimation loops
    for obj in objList:
        #Remove modifier if it already exists
        if obj.modifiers:
            obj.modifiers.clear()

        # Get dimensions for possible cleanup
        x = obj.dimensions[0]
        y = obj.dimensions[1]
        if obj.type == "MESH":
            modDec = obj.modifiers.new("Decimate", type="DECIMATE")
            face_count = len(obj.data.polygons)
            if (face_count > 0):
                # function to increase poly reduction on higher poly models
                # but reduce reduction on lower ones (compared to decRatio * startfaces)
                # endfaces = startfaces ^ ((8 + 2 * decRatio) / 10)
                # High Bound: 99%, Mid Bound: 53, Low Bound: 29%
                target_face_count = math.ceil(math.pow(face_count, (8 + 2 * (1-decRatio)) / 10))
                modDec.ratio = target_face_count / float(face_count)
            modDec.use_collapse_triangulate = True
    
    #If selected all then unselect all
    if (selectAll == True):
        bpy.ops.object.select_all(action='DESELECT')
   
    # Scene update causes blender to slow down over time. Use outside loops and only when necessary.
    # https://blenderartists.org/t/python-slowing-down-over-time/569534/7 
    bpy.context.view_layer.update()
    bpy.ops.ed.undo_push(overrideContext,message="Undo Decimate Models")

    #bpy.context.area.type = originalType
    return True


def cleanUp(percent):
    """
    Removes all small objects such as screws from the scene.
        1. Record bounding box of the scene.
        2. Calculate percentage threshold for removal
        3. Compare items to removal threshold and mark for deletion
        4. Delete small object under threshold
    Utility calls scene objects, thus no input or output.
    
    Paramaters:
    ----------
    ----------
    """
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Small Object Removal")

    """
    An objects bounding box has 8 vertices. This is dimension 1.
    Dimension 2 is the xyz coord for the chosen vertex.
(-++)2*---------6*(+++)   
     / |        /|
(--+)1*--------5*|(+-+)
     | |       | |
     | |       | |
(-+-)| /*3-----|/*7(++-)
(---)*0--------*4(+--)

    """
    
    #Run only on the selected or if non-selected run on all
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False
        #Selecting all children
        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)

    objList = [o for o in bpy.context.scene.objects if o.select_get()]

    # get max and min bounds
    mins = np.array([0, 0, 0])
    maxs = np.array([0, 0, 0])
    for o in objList:
        if o.type == 'MESH':
			# i represent the x,y,z coord of the specified vertex
            for i in range(3):
				# record a scene wide min/max boundary
                if o.bound_box[0][i] < mins[i]: mins[i] = o.bound_box[0][i]
                if o.bound_box[6][i] > maxs[i]: maxs[i] = o.bound_box[6][i]

    # check if no objects
    minCheck = np.array([0,0,0]) == mins
    maxCheck = np.array([0,0,0]) == maxs
    if minCheck.any() and maxCheck.any():
        return
    
    # calculate dimensions percent. We do by hand for accuracy
    minDimensions = abs((maxs - mins) * percent)
    
    # mark all targets under the size threshold
    targets = []
    largestObjSize = 0.0
    largestObj = ""
    for obj in objList:
        if obj.type == 'MESH':   
            # check if object dimensions fall under the defined threshold, comparing bounding boxes
            objx = abs(obj.bound_box[6][0] - obj.bound_box[0][0])
            objy = abs(obj.bound_box[6][1] - obj.bound_box[0][1])
            objz = abs(obj.bound_box[6][2] - obj.bound_box[0][2])
            #Always leave one object left, whatever is the largest
            if objx * objy * objz > largestObjSize:
                largestObj = obj
                largestObjSize = objx * objy * objz
            if objx <= minDimensions[0] and objy <= minDimensions[1] and objz <= minDimensions[2]:
                targets.append(obj.name_full)

    # remove all targets
    for name in targets:
        objMain = bpy.data.objects[name]
        #Don't delete the largest obj
        if objMain != largestObj:
            if objMain.children:
                objParent = objMain.parent
                #We are going to make sure removing the object does not break the model
                for child in objMain.children:
                    if child.parent == objMain:
                        tempMatrix = child.matrix_world
                        child.parent = objParent
                        child.matrix_world = tempMatrix                            
            bpy.data.objects.remove(objMain, do_unlink=True)

    #If selected all then unselect all
    if (selectAll == True):
        bpy.ops.object.select_all(action='DESELECT')

    # update scene
    bpy.context.view_layer.update()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Small Object Removal")
    return True

'''
Code for deleting objects hidden.
for o in allObjs:
        if not o.visible_get() or o.hide_viewport or o.hide_render:
            hiddenObjs.append(o)
    #No need to run if nothing is hidden    
    if not hiddenObjs == []:
        #un hide everything
        for o in hiddenObjs:
            o.hide_set(False)
            o.hide_viewport = False
            o.hide_render = False

        #Run only on the selected or if non-selected run on all
        selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
        allObjs, objList = [o for o in bpy.data.objects], []
        if len(selObjs) == 0:
            objList = allObjs
            selectAll = True
        else:
            objList = selObjs
            selectAll = False

        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)
            
        objList = [o for o in bpy.context.scene.objects if o.select_get()]
        
        delObjects = []
        # remove all targets
        for name in objList:
            print(name)
            if name in hiddenObjs:
                delObjects.append(name)

        for name in delObjects:
            objMain = bpy.data.objects[name.name_full]
            if objMain.children:
                objParent = objMain.parent
                #We are going to make sure removing the object does not break the model
                for child in objMain.children:
                    if child.parent == objMain:
                        tempMatrix = child.matrix_world
                        child.parent = objParent
                        child.matrix_world = tempMatrix                            
            bpy.data.objects.remove(objMain, do_unlink=True)
            objList.remove(objMain)
            hiddenObjs.remove(objMain)

        bpy.context.view_layer.update()
        #rehide
        for obj in hiddenObjs:
            obj.hide_set(True)'''


'''
Applies the clear-parent-keep-transform function to all mesh objects, removed anything else
'''
def deParent():
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo De-parenting")

    empties = []

    #Run only on the selected or if non-selected run on all
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False    
        #If no parent then flatten
        if objList[0].parent == None:
            selectAllChild(objList[0])
            objList = [o for o in bpy.context.scene.objects if o.select_get()]


    # tag head parents and empty objects for later
    for o in objList:
        #Dont think this is needed
        o.select_set(True)
        if o.type == 'EMPTY':
            empties.append(o)

    #Run the clear-keep-transform operation    
    overrideContext['active_object'] = objList[0]                 
    bpy.ops.object.parent_clear(overrideContext, type="CLEAR_KEEP_TRANSFORM")
   
    # apply all changes with scene update
    bpy.context.view_layer.update()
   
    # clean up empties
    for name in empties:
        if not name.children:
            bpy.data.objects.remove(name, do_unlink=True)

    
    #If selected all then unselect all
    if (selectAll == True):
        selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
        for obj in selObjs:
            obj.select_set(False)
    return True

'''
If any meshes are loose it creates its own seperate object, usefull if we have screws that are merged into an object
'''
def splitModels():
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Split Models")

    #Run only on the selected or if non-selected run on all
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False
        # select all objects
        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)
    
    bpy.ops.mesh.separate(overrideContext, type='LOOSE')
    
    #If selected all then unselect all
    if (selectAll == True):
        bpy.ops.object.select_all(action='DESELECT')
    return True

'''
Loops through and gets all children of given object
'''
def selectAllChild(obj):
    childMain = obj
    obj.select_set(True)
    if obj.children == None:
        return
    for child in obj.children:
        child.select_set(True)
        selectAllChild(child)

'''
Things to prepare model for decimation and cleanup:
1. deParent - Remove parent dependencies to simplify calculations
2. center all object origins - center the origin of each object to the center of its mesh
3. recenter objects to origin - move all the objects collectivly so that their combined center is at the origin
4. freeze transformations - apply the transformations so that each object is at <0,0,0> with rotation <0,0,0> and a scale of <1,1,1>
'''
def centerModels():
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Center Models")

    
    #Run only on the selected or if non-selected run on all
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False
        # select all objects
        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)

    objList = [o for o in bpy.context.scene.objects if o.select_get()]

    
    # set each objects origin to the center. Currently can mess things up, sometimes moves objects that aren't related
    #bpy.ops.object.origin_set(overrideContext, type='ORIGIN_GEOMETRY')    
    
    # calculate center of all mesh objects, we are going to use the world coordinate frame as a reference
    numObjs = 0
    for o in objList:
        if o.type == 'MESH':
            numObjs += 1
    x = 0
    y = 0
    z = 0
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0
    for obj in objList:
        if obj.type == 'MESH':
            if obj == objList[0]:
                v = []
                for i in range(4):
                    if i < 3:
                        v.append(obj.bound_box[0][i]) # x, y, z postions
                    else:
                        v.append(1)
                v = obj.matrix_world @ mathutils.Vector((v))
                x = v[0]
                y = v[1]
                z = v[2]
                min_x = x
                max_x = x
                min_y = y
                max_y = y
                min_z = z
                max_z = z
            for j in range(8):
                v = []
                for i in range(4):
                    if i < 3:
                        v.append(obj.bound_box[j][i]) # x, y, z postions
                    else:
                        v.append(1)
                v = obj.matrix_world @ mathutils.Vector((v))
                x = v[0]
                y = v[1]
                z = v[2]
                if x < min_x:
                    min_x = x
                elif x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                elif y > max_y:
                    max_y = y
                if z < min_z:
                    min_z = z
                elif z > max_z:
                    max_z = z

    bb1 = mathutils.Vector((min_x, min_y, min_z))
    bb8 = mathutils.Vector((max_x, max_y, max_z))
    bb18 = (bb1 + bb8)/2

    # center all mesh objects
    if numObjs > 0:
        cenMatrix = mathutils.Matrix(((0,0,0,bb18[0]),(0,0,0,bb18[1]),(0,0,0,bb18[2]),(0,0,0,0)))
        for o in objList:
            if o.parent not in objList: 
                o.matrix_world -= cenMatrix
                #If we are at a root object then we need to create a new object
                if o.type != "MESH" and not o.parent and o.children:
                    e = bpy.data.objects.new( o.name, None )

                    # due to the new mechanism of "collection"
                    bpy.context.scene.collection.objects.link( e )

                    # empty_draw was replaced by empty_display
                    o.empty_display_size = 2
                    o.empty_display_type = 'PLAIN_AXES'
                    o.parent = e
        
        # apply all changes with scene update
        bpy.context.view_layer.update()

    # freeze transformations
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    #If global objects make sure we unselect all
    if (selectAll == True):
        selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
        for obj in selObjs:
            obj.select_set(False)
    #bpy.ops.object.origin_set(overrideContext, type='ORIGIN_GEOMETRY', center='MEDIAN')        
    bpy.ops.ed.undo_push(overrideContext, message="Undo De-parenting")
    return True

'''
Simple function that deletes all hidden objects
'''
def deleteHidden():
    t11 = time.monotonic()
    overrideContext = AssembleOverrideContextForView3dOps()
    bpy.ops.ed.undo_push(overrideContext, message="Undo Delete Models")

    #Run only on the selected or if non-selected run on all
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    if len(selObjs) == 0:
        objList = allObjs
        selectAll = True
        bpy.ops.object.select_all(action='SELECT')
    else:
        objList = selObjs
        selectAll = False
        # select all objects
        for o in objList:
            if o.parent not in objList:
                selectAllChild(o)
    objList = [o for o in bpy.context.scene.objects if o.select_get()]
    #go through all objects in scene and mark what is hidden
    hiddenObjs = []
    
    bb_list = []
    outside = []
    view_layer = bpy.context.view_layer

    # creating custom override for mesh ops (will only be in VIEW_3D)
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.screen.screen_full_area(override)
                break
    bpy.ops.screen.back_to_previous()
    x = 0
    y = 0
    z = 0
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0
    bb05 = [0,0]
    bb02 = [0,0]
    bb72 = [0,0]
    bb75 = [0,0]
    bb16 = [0,0]
    bb07 = [0,0]
    bb00 = [0,0]
    bb11 = [0,0]
    bb22 = [0,0]
    bb33 = [0,0]
    bb44 = [0,0]
    bb55 = [0,0]
    bb66 = [0,0]
    bb77 = [0,0]
    # creates a "Maximum" bound box of all objects
    for obj in objList:
        if obj.type == 'MESH':
            if obj == objList[0]:
                v = []
                for i in range(4):
                    if i < 3:
                        v.append(obj.bound_box[0][i]) # x, y, z postions
                    else:
                        v.append(1)
                v = obj.matrix_world @ mathutils.Vector((v))
                x = v[0]
                y = v[1]
                z = v[2]
                min_x = x
                max_x = x
                min_y = y
                max_y = y
                min_z = z
                max_z = z
            for j in range(8):
                v = []
                for i in range(4):
                    if i < 3:
                        v.append(obj.bound_box[j][i]) # x, y, z postions
                    else:
                        v.append(1)
                v = obj.matrix_world @ Vector((v))
                x = v[0]
                y = v[1]
                z = v[2]
                if x < min_x:
                    min_x = x
                elif x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                elif y > max_y:
                    max_y = y
                if z < min_z:
                    min_z = z
                elif z > max_z:
                    max_z = z
    bb0 = Vector((min_x-1, min_y-1, min_z-1))
    bb1 = Vector((min_x-1, min_y-1, max_z+1))
    bb2 = Vector((min_x-1, max_y+1, max_z+1))
    bb3 = Vector((min_x-1, max_y+1, min_z-1))
    bb4 = Vector((max_x+1, min_y-1, min_z-1))
    bb5 = Vector((max_x+1, min_y-1, max_z+1))
    bb6 = Vector((max_x+1, max_y+1, max_z+1))
    bb7 = Vector((max_x+1, max_y+1, min_z-1))
    #Core faces
    bb05[0] = (bb0 + bb5)/2
    bb02[0] = (bb0 + bb2)/2
    bb72[0] = (bb7 + bb2)/2
    bb75[0] = (bb7 + bb5)/2
    bb16[0] = (bb1 + bb6)/2
    bb07[0] = (bb0 + bb7)/2
    bb00[0] = bb0
    bb11[0] = bb1
    bb22[0] = bb2
    bb33[0] = bb3
    bb44[0] = bb4
    bb55[0] = bb5
    bb66[0] = bb6
    bb77[0] = bb7
    #bb_list = [bb1, bb2, bb3, bb4, bb5, bb6, bb7, bb8, bb12, bb13, bb24, bb34, bb15, bb26, bb37, bb48, bb56, bb57, bb68, bb78, bb14, bb16, bb28, bb47, bb35, bb58]
    bb_list = [bb05,bb02,bb72,bb75,bb16,bb07,bb00,bb11,bb22,bb33,bb44,bb55,bb66,bb77]
    # Ray casting from all 26 points in bb_list to each object, if returns that current object, it is NOT hidden
    


    for obj in objList:
        for src in bb_list:
            if (obj in outside):
                break
            else:
                if obj.type == 'MESH':               
                    bb72[1] =  obj.matrix_world @  ((Vector(obj.bound_box[0]) + Vector(obj.bound_box[5]))/2)
                    bb75[1] =  obj.matrix_world @  ((Vector(obj.bound_box[0]) + Vector(obj.bound_box[2]))/2)
                    bb05[1] =  obj.matrix_world @  ((Vector(obj.bound_box[7]) + Vector(obj.bound_box[2]))/2)
                    bb02[1] =  obj.matrix_world @  ((Vector(obj.bound_box[7]) + Vector(obj.bound_box[5]))/2)
                    bb07[1] =  obj.matrix_world @  ((Vector(obj.bound_box[1]) + Vector(obj.bound_box[6]))/2)
                    bb16[1] =  obj.matrix_world @  ((Vector(obj.bound_box[0]) + Vector(obj.bound_box[7]))/2)
                    bb00[1] =  obj.matrix_world @ (Vector(obj.bound_box[0]))
                    bb11[1] =  obj.matrix_world @ (Vector(obj.bound_box[1]))
                    bb22[1] =  obj.matrix_world @ (Vector(obj.bound_box[2]))
                    bb33[1] =  obj.matrix_world @ (Vector(obj.bound_box[3]))
                    bb44[1] =  obj.matrix_world @ (Vector(obj.bound_box[4]))
                    bb55[1] =  obj.matrix_world @ (Vector(obj.bound_box[5]))
                    bb66[1] =  obj.matrix_world @ (Vector(obj.bound_box[6]))
                    bb77[1] =  obj.matrix_world @ (Vector(obj.bound_box[7]))

                    """
                    An objects bounding box has 8 vertices. This is dimension 1.
                    Dimension 2 is the xyz coord for the chosen vertex.
                (-++)2*---------6*(+++)   
                    / |        /|
                (--+)1*--------5*|(+-+)
                    | |       | |
                    | |       | |
                (-+-)| /*3-----|/*7(++-)
                (---)*0--------*4(+--)

                    """
                    """for bb in bb_list:
                        bpy.context.view_layer.objects.active = obj
                        direction = (bb[1] - src[0]).normalized()
                        #print(bb_list[j][1])
                        result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, src[0], direction)
                        if objectray == obj:
                            outside.append(obj)
                            break
                    """
                    for j in range(8):
                        bpy.context.view_layer.objects.active = obj
                        direction = (bb_list[j][1] - src[0]).normalized()
                        #print(bb_list[j][1])
                        result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, src[0], direction)
                        if objectray == obj:
                            outside.append(obj)
                            break                    
                    #To the center
                    #print(obj.location)
                    direction = ((obj.matrix_world @ obj.location) - src[0]).normalized()
                    result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, src[0], direction)
                    if objectray == obj:
                        outside.append(obj)
                        break
                    outside.append(objectray)

    #face 1 6 
    dv = (bb1 - bb0)/150
    dh = (bb4 - bb0)/150
    ds = (bb3 - bb0)
    for j in range(150):
        for i in range(150):
            origin = bb0 + (dv * j) + (dh * i)
            direction = (origin + ds).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)                              
            outside.append(objectray)
            origin = origin + ds
            direction = (-ds - origin).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)          
            outside.append(objectray)
    #face 2 5 
    dv = (bb3 - bb0)/150
    dh = (bb1 - bb0)/150
    ds = (bb4 - bb0)
    for j in range(150):
        for i in range(150):
            origin = bb0 + (dv * j) + (dh * i)
            direction = (origin + ds).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)                              
            outside.append(objectray)
            origin = origin + ds
            direction = (-ds - origin).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)          
            outside.append(objectray)
    #face 3 4 
    dv = (bb4 - bb0)/150
    dh = (bb3 - bb0)/150
    ds = (bb1 - bb0)
    for j in range(150):
        for i in range(150):
            origin = bb0 + (dv * j) + (dh * i)
            direction = (origin + ds).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)                              
            outside.append(objectray)
            origin = origin + ds
            direction = (-ds - origin).normalized()
            result, location, normal, faceIndex, objectray, matrix = bpy.context.scene.ray_cast(view_layer, origin, direction)          
            outside.append(objectray)

    deleteCount = 0 
    for name in objList:
        if name not in outside and name.type == 'MESH':
            objMain = bpy.data.objects[name.name_full]
            if objMain.children:
                objParent = objMain.parent
                #We are going to make sure removing the object does not break the model
                for child in objMain.children:
                    if child.parent == objMain:
                        tempMatrix = child.matrix_world
                        child.parent = objParent
                        child.matrix_world = tempMatrix                            
            bpy.data.objects.remove(objMain, do_unlink=True)
            deleteCount += 1 

    #If global objects make sure we unselect all
    if (selectAll == True):
        bpy.ops.object.select_all(action='DESELECT')
    t22 = time.monotonic()
    print('Deleted', deleteCount, 'objects')
    return True



'''
Function to implement proper selection before export
'''
def checkSelection():
    selObjs = [o for o in bpy.context.scene.objects if o.select_get()]
    allObjs, objList = [o for o in bpy.data.objects], []
    
    if len(selObjs) == 0:
        objList = allObjs
    else:
        objList = selObjs
    
    for o in objList:
        if o.parent not in objList:
            selectAllChild(o)
    objList = [o for o in bpy.context.scene.objects if o.select_get()]
    return objList

'''
Simple function to fix colors on imports that natively lose them
'''
def hex_to_rgb( hex_value ):
    b = (hex_value & 0xFF) / 255.0
    g = ((hex_value >> 8) & 0xFF) / 255.0
    r = ((hex_value >> 16) & 0xFF) / 255.0
    return r, g, b, 1

def colorCorrect():
    for obj in bpy.data.materials:
        if ("color_" in obj.name):
            #print(obj.name[6:12])
            hex_int = int(("0x" + obj.name[6:12]),16)
            color = hex_to_rgb(hex_int)
            specColor = [color[0],color[1],color[2]]
            nodes = obj.node_tree.nodes
            principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
            principled.inputs['Base Color'].default_value[0] = color[0]
            principled.inputs['Base Color'].default_value[1] = color[1]
            principled.inputs['Base Color'].default_value[2] = color[2]
            obj.diffuse_color = color
            obj.specular_color = specColor

'''
Simple function to scale models to 100%
'''
def scaleModels():

    for o in bpy.data.objects:
        o.scale[0] = 1
        o.scale[1] = 1
        o.scale[2] = 1

# code for running with VS Code or from inside blender
#if __name__ == '<run_path>' or __name__ == '__main__':
    #cleanUp(0.1)
    #decimateModels(0.2)
    #apply_modifiers()
    #deleteHidden()
    #print("Main")
