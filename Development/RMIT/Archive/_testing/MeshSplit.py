import bpy
"""
# Select object and save var
# Seperate by loose. 

ob = bpy.data.objects['MyMesh']
bpy.ops.object.select_all(action='DESELECT')
ob.select = True
bpy.context.scene.objects.active = ob
bpy.ops.mesh.separate(type='LOOSE')

# Define Directory
dir = bpy.path.abspath('//subdirectory/')

# Create Directory (If Necessary)
if not os.path.exists(dir): os.makedirs(dir)

# Export STLs
bpy.ops.export_mesh.stl(filepath = dir, batch_mode = 'OBJECT') """

# Inititial limit is 1mil face count
# First determine if Face Count of scene is over 1 million.
default_layer = bpy.context.scene.view_layers['View Layer']
scene_stats = bpy.context.scene.statistics(default_layer).split("|")
scene_face_count = [x for x in scene_stats if x.startswith(" Faces")]
if int(''.join(filter(str.isdigit, scene_face_count[0]))) > 1000000:
    print("True")

# Create a list of lists to store sections of the scene for export.
obj_list = sorted(bpy.data.objects, key=lambda obj: obj.name)
poly_limit, all_sections, obj_section = 0, [], []
for part in obj_list:
    if part.type == "MESH":
        if poly_limit < 2000:
            poly_limit += len(part.data.polygons)
            obj_section.append(part)
        else:
            obj_section.append(part)
            all_sections.append(obj_section)
            poly_limit, obj_section = 0, []
    else:
        continue
if len(obj_section) > 0:
    all_sections.append(obj_section)

print("stop")


# Export that selection into a temp file array. (.blends)
# Repeat until all objects are done.
# Process each .blend.
# Merge all .blends together.
# Export. 
# AKA Batch Option in RMIT. Check in Driver. 