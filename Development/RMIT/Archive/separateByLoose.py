import bpy

def SeparateByLoose():
    for o in bpy.data.objects:
        o.select_set(True)
    
    bpy.ops.mesh.separate(type='LOOSE')
    
    for o in  bpy.data.objects:
        o.select_set(False)


if __name__ == '<run_path>' or __name__ == '__main__':
    SeparateByLoose()