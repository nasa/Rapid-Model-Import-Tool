NEVA Tool User Guide
=======================

The main objective of the NEVA tool is to allow for seamless exporting of 3D models from CATIA into .DAE (COLLADA) and
.OBJ file formats. This is the first step in a process for which the end goal is to import the models into Unity to be
observed through virtual or augmented reality headsets. Therefore, it is imperative to know how to decimate models at
each step. The primary focus is to retain good visual quality while limiting unnecessary nodes, parts, or internal structure
that isn’t visible from an outside view. The following is a simple guide on how to use NEVA for this purpose.

| As an example, we will be using a manlift model for this tutorial. The .CAT design files and .CGR files for this model can be found at: V:\\V5Delmia\\PRODUCTS\\TRAN\MOV\\JLG E600JP
| *Note*: Assigned drive folder V:\\ may be different depending on your computer.

**Things to Know**

- COLLADA is a file format; .DAE (digital asset exchange) is its filename extension. In this tutorial the two are used interchangeably.
   - The COLLADA exporter only works for 3Ds Max's OpenCOLLADA importer available at https://github.com/KhronosGroup/OpenCOLLADA/tree/master/COLLADAMax
- OBJ or .OBJ (short for "object") is both a file format and an extension.
- Both CATIA and the NEVA tool are written in C++.
- 3D models in CATIA can be .CATProduct or .CGR file extensions. The NEVA tool can be used to export either, but the tool scripts vary slightly
- The *product hierarchy* is the tree of parts on the left-hand side of your CATIA window. It lists all the individual components of your model. If it is a design model (.CAT), you should be able to expand branches down to the “Sketch” function, while .CGR files will only show solids of the model and its geometry cannot be easily manipulated.

How to Export using NEVA
-----------------------------

- Open your chosen 3D model file in CATIA.
- Ensure that there are no unnecessary parts in your model.
   - i.e. an artificial shadow under a car, background/environment sphere, etc.
   - If there are any, delete them before you export to reduce file size. Do this by right-clicking on the part you wish to delete in the *product hierarchy* (see **Things to Know**, above), and then clicking **“Delete”**.
- Changing the mesh precision of your model
   - If you do not wish to change your model’s default mesh precision of 1mm, you may *skip this step* OR if the original model you are exporting from is a .CGR, meaning your model is already tessellated, you may *skip this step*.
   - If you *DO* wish to alter your model’s mesh precision and you are not exporting from a .CGR: Within CATIA, go to *Tools > Options > General > Compatibility > COLLADA*

.. image:: NEVA\\image1.jpg

Here, you may change **“Mesh Precision (mm)”**, allowing you to change the total number of polygons of the model. This is
useful for decimation purposes within CATIA itself, before even using NEVA to export to COLLADA or .OBJ.

- **IMPORTANT**: Make sure to clear the cache before *each new export* when you change the mesh precision. The easiest way to do this is to go to *NEVA > Export > Clear COLLADA* Cache. See step 4 for a screenshot of where this is located.
- Alternatively, you can also click the folder button and manually delete the folder listed in the COLLADA Cache Path by right-clicking on the folder, then clicking **“Delete”**.

.. image:: NEVA\\image2.jpg
   :scale: 100 %
   :alt: folder icon
   :align: center

- Click **"OK"** to save your changes and exit the window.

- Exporting your file
    - If you want to save as .OBJ, go to *NEVA > Export > Export OBJ File…*
    - If you want to save as .DAE, go to *NEVA > Export > Export COLLADA…*

.. image:: NEVA\\image3.jpg
    :align: center

- Next, you will be prompted by the COLLADA Export window to select **“Objects to Export”** and **“Coordinate Frame”**.
    - To do this, click on the text that says **“No Selection”** until it is highlighted in blue, then click on the part in the product hierarchy that you wish to select. Ensure that you select the same part for both of these. This ensures that your coordinate frame is uniform with the object you’re exporting, and is useful when bringing in the model to another program, such as 3DSMax or Blender.

.. image:: NEVA\\image4.jpg
    :align: center

- If you wish to export the entire model, select the highest branch in your product hierarchy for both of these.
- Click **“OK”** to exit the window.

- You will be prompted by the **“Select COLLADA File”** window to save your file.

.. image:: NEVA\\image5.jpg
    :align: center

- Select a location to save your file.
- Name your file in the **“File name:”** box.
- Click **“Save”** to exit the window.

- Now, you will see a status box that looks like this:

.. image:: NEVA\\image6.jpg

Once this box disappears, your file has been saved to its assigned location along with any
material/texture images and other necessary files!

How to Observe Your COLLADA or .OBJ Model in 3D
----------------------------------------------------

You can visually observe your exported model before even importing it into 3DsMax. This is useful for getting
a visual idea of how your mesh precision affects your model (such as the roundness of a tire, for example) so that you
can go back and re-export with different parameters before proceeding.

- Go to *Start > All Programs > NEVA > Model Viewer*

.. image:: NEVA\\image7.jpg
    :align: center

- Here, you will be prompted to select your model from your files. Select the .DAE or .OBJ file you wish to observe.
Within the **DVG Model Viewer**, you should be able to use all of the same CATIA controls (rotate, pan, zoom).

.. image:: NEVA\\image8.jpg
    :align: center

Above is an example of a COLLADA export directly from a CATIA design model. The Model Viewer shows the COLLADA model, while in the background we see the original CATIA file.

As you can see, there are some missing texture assignments on the COLLADA model – that kind of thing is why we’re doing this.

|

How to Observe Your COLLADA or .OBJ Model’s Source Code
---------------------------------------------------------
You can open up the .XML code for your NEVA-exported model file using any simple text reader. The recommended one is Notepad++.
