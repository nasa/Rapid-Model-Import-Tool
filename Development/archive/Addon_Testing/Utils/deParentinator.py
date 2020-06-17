import bpy
from mathutils import Matrix

# flatten each child object and their children
def flatten(o):
    for c in o.children:
        c.matrix_world = o.matrix_world @ c.matrix_world
        c.parent = None
        flatten(c)

# start recursive process and create outer loop so nothing is missed
def deParent():
    for o in bpy.data.objects:
        if o.parent != None:
            while o.parent != None:
                o = o.parent
            
            flatten(o)
    
    bpy.context.view_layer.update()


# code for running with VS Code
if __name__ == '<run_path>' or __name__ == '__main__':
    deParent()