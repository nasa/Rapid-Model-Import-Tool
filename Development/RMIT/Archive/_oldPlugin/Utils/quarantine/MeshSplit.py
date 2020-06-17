import bpy

# Select object and save var
# Seperate by loose. 

ob = bpy.data.objects['MyMesh']
bpy.ops.object.select_all(action='DESELECT')
ob.select = True
bpy.context.scene.objects.active = ob
bpy.ops.mesh.separate(type='LOOSE')