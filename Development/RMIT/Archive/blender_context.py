import bpy

#all the area types except 'EMPTY' from blender.org/api/blender_python_api_current/bpy.types.Area.html#bpy.types.Area.type
types = {'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'NLA_EDITOR', 'IMAGE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'TEXT_EDITOR', 'NODE_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER', 'USER_PREFERENCES', 'INFO', 'FILE_BROWSER', 'CONSOLE'}

#save the current area
area = bpy.context.area.type

#try each type
for type in types:
    #set the context
    bpy.context.area.type = type


    #print out context where operator works (change the ops below to check a different operator)
    if bpy.ops.export_scene.poll():
        print(type)

#leave the context where it was
bpy.context.area.type = area