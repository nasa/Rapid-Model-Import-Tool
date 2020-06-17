Features
=======================

This section will layout all that you need to know to work with and interact with RMIT at an end user perspective

Workflow 
------------------------------
To start using RMIT you will launch the RMIT.exe application. This will lead you into the RMIT launch window as seen below.
The first thing to do is select an import file and export file as seen below

.. figure:: _images\\RMIT3.png
    :align: center

    Import Export Area

After selecting the import and export location the next step is to either disable or enable the headless mode.
**Headless mode** will run everything in the background with the settings set by the user.
Available settings enabled in headless mode are described in the features section.

If a user runs RMIT in its normal function blender will open and the following window will appear.

.. figure:: _images\\RMIT2.png
    :align: center

    The Blender window of RMIT

The user can then run the various functions listed within the GUI or run Blender as normally.
For these functions if the user has no objects selected it will be run on the entire model. 
If the user has a single or multiple object selected the functions will be run on just that selection.
A function can be undone by running ctrl-z.
When the user is done interacting with both Blender and RMIT they may run the export function, and then close the program.



.. _FileTypes:

Exporting/Importing and File Types
----------------------------------------
RMIT natively imports the following file types:
************************************************

.. csv-table:: RMIT Import Types
    :header: "File Format", "RMIT import Compatibility"
    
    ".dae (COLLADA)", "Only OpenCOLLADA format"
    ".fbx", "fbx version 7100 or newer."
	".gltf (Graphic Language Transmission Format)", "Fully Compatible"
	".glb", "Fully Compatible"    
    ".obj (Wavefront)", "Fully Compatible"
    ".ply (Stanford)", "Fully Compatible"
    ".stl", "Fully Compatible"
    

RMIT natively exports the following file types:
************************************************

.. csv-table:: RMIT Export Types
    :header: "File Format"
    
    ".dae (COLLADA)"
    ".fbx"
	".gltf (Graphic Language Transmission Format)"
    ".obj (Wavefront)"
    ".stl"
    


By default RMIT will export in .gltf format





Functions
------------------------------

RMIT has several customized features that allow you to edit and clean your model:

Clean up/Remove Small Components
********************************
The Remove Small Components Function will create a bounding box of the scene, and will remove objects that are smaller than the input ratio to the scene bounding box.

You would use this function if you did not care about small details of your model.

Extract Object
******************
The Extract Object function loops through all objects and then their hierarchy it then removes the hierarchy starting with the head and then
empty objects are removed. After the function is run all objects will be within the same hierarchy level.

You would use this function if you did not care about the hierarchy of your model.

Delete Hidden Objects
**********************
The Delete Hidden Objects Function will delete any object not seen from the exterior of the selection.

You would use this function if you did not need to see the internals of your model or break it apart in any way.

Decimation
***********
The Decimation Function will reduce the polygon count using the default blender decimation algorithm.

You would use this function if your model was too complex for your application or if you care more about the speed of your application than quality.


Separate Loose Meshes
**********************
The Separate Loose Meshes function will break up a mesh into smaller components if there are non connecting complete meshes.
A good example would be if there are two spheres that are not touching but share the same mesh, these would be made into seperate objects with this function.

You would use this function if you wanted to interact with what appear to be seperate objects within your model.

Center Model
**********************
The Center Model function will move the origin of each object to the center of its mesh

You would use this function if you plan on applying transformations to a certain object in your application


Merge Meshes
**********************
The Merge Meshes Function will merge any mesh together into a single object as well as removing duplicate materials.

You would use this function if you did not want to take apart your model, and wanted to make it much more light weight.


Headless Mode
**********************
Headless mode can run all these functions without opening blender. This is extremely useful if you know exactly how you want to process your model.
The functions will be ran on all the objects. The order of the functions ran is the following:

Extract Objet/Delete any relation (This will remove and non mesh objects)
Remove hidden
Seperate Loose Meshes
Remove Small objects (you will set the ratio)
Merge all objects together
Center Objects
Decimation (you will set the amount)




