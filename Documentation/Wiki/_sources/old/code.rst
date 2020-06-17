Documentation of Code
=======================

Below you will find the documentation for the code of this project.

Import Catia DAE(FOR BLENDER)
------------------------------
 .. py:function:: updateFile(fileName)

 This is the main function that reads every line in the file and calls various functions based on the tags. It runs the algorithm on the original imported file to create a temporary file, which is then imported into blender. The temporary file is deleted after successful import. The temporary file name takes the process id from the operating system in order to get a unique file name.

   Parameters:
     fileName: the original file name with path for the imported DAE file
   Returns:
     newfileName: The new file name with path for the modified temporary updated file.

 .. py:function:: convertSingleTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in)

 The function takes an input string and calls the appropriate convert function
 based on triangle/tristrips/trifans tag.
 This function is only for a mesh with single TEXCOORD semantic.
 Returns an output set of numbers without the tags, after applying the appropriate algorithm.

   Parameters:
      insideTriangles: boolean true if the <p> values belong to a triangle tag, else false
      insideTristrips: boolean true if the <p> values belong to a tristrips tag, else false
      insideTrifans: boolean true if the <p> values belong to a trifans tag, else false
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string

 .. py:function:: triangleToTriangleSingleTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags within the triangle tag.
 | This function is only for a mesh with single TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>0 0 19 1 20 2 1 3 24 4 25 5 25 5 2 6 1 3 26 7 2 6 25 5 3 8 27 9 28 10 28 10 4 11 3 8 29 12 4 11 28 10 1 3 17 13 18 14</p>

  Output: 0 0 0 19 19 1 20 20 2 1 1 3 24 24 4 25 25 5 25 25 5 2 2 6 1 1 3 26 26 7 2 2 6 25 25 5 3 3 8 27 27 9 28 28 10 28 28 10 4 4 11 3 3 8 29 29 12 4 4 11 28 28 10 1 1 3 17 17 13 18 18 14

   Parameters:
    insideTriangles: boolean true if the <p> values belong to a triangle tag, else false
    insideTristrips: boolean true if the <p> values belong to a tristrips tag, else false
    insideTrifans: boolean true if the <p> values belong to a trifans tag, else false
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: trifansToTriangleSingleTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags within the trifans tag.
 | This function is only for a mesh with single TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>19 0 18 1 22 2 21 3 20 4</p>

  Output: 19 19 0 18 18 1 22 22 2 19 19 0 22 22 2 21 21 3 19 19 0 21 21 3 20 20 4

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string


 .. py:function:: tristripsToTriangleSingleTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags
 | within the tristrips tag.
 | This function is only for a mesh with single TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm..

 Example:
  Input: <p>1 0 1 0 0 1 2 2 3 3</p>

  Output: 1 1 0 1 1 0 0 0 1 0 0 1 1 1 0 2 2 2 0 0 1 2 2 2 3 3 3

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: scaleDown(line_in)

 | The function takes an input string that extracts the numbers between > and </.
 | Returns an output string with the numbers scaled down by 25.4 along with its appropriate tags

  Parameters:
   line_in: the input string from one line of the file
  Returns:
   line_out: the output string

 .. py:function:: rotateValues(line_in)

 | The function takes an input string that extracts the numbers between the rotate tags.
 | Returns an output string by negating each number if the first number is -0.57735
 | There seems to be inconsistency with the pattern match for rotate, Therefore, this function is not used, but is left here for future updates to the rotate algorithm

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: triangleToTriangleNoTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags
 | within the triangle tag.
 | This function is only for a mesh with no TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>190 231 232 196 197 205 298 297 256 271 263 262</p>

  Output: 190 190 231 231 232 232 196 196 197 197 205 205 298 298 297 297 256 256 271 271 263 263 262 262

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: trifansToTriangleNoTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags within the trifans tag.
 | This function is only for a mesh with no TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>405 404 430 429 428 427 426 425 424 423 422 406</p>

  Output: 405 405 404 404 430 430 405 405 430 430 429 429 405 405 429 429 428 428 405 405 428 428 427 427 405 405 427 427 426 426 405 405 426 426 425 425 405 405 425 425 424 424 405 405 424 424 423 423 405 405 423 423 422 422 405 405 422 422 406 406

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: tristripsToTriangleNoTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags within the tristrips tag.
 | This function is only for a mesh with no TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>839 839 910 840 909 908</p>

  Output: 839 839 839 839 910 910 910 910 839 839 840 840 910 910 840 840 909 909 909 909 840 840 908 908

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string

 .. py:function:: convertNoTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in)

 | The function takes an input string and calls the appropriate convert function
 | based on triangle/tristrips/trifans tag.
 | This function is only for a mesh with no TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

   Parameters:
      insideTriangles: boolean true if the <p> values belong to a triangle tag, else false
      insideTristrips: boolean true if the <p> values belong to a tristrips tag, else false
      insideTrifans: boolean true if the <p> values belong to a trifans tag, else false
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string

 .. py:function:: tristripsToTriangleDoubleTEXCOORD(line_in)

 | The function takes an input string that extracts the numbers between the <p> tags
 | within the tristrips tag.
 | This function is only for a mesh with no TEXCOORD semantic.
 | Returns an output set of numbers without the tags, after applying the appropriate algorithm.

 Example:
  Input: <p>49 0 0 48 1 1 0 2 2 47 3 3 1 4 4 46 5 5 2 6 6 45 7 7 3 8 8 44 9 9 4 10 10 43 11 11 5 12 12 42 13 13 6 14 14 41 15 15 7 16 16 40 17 17 8 18 18 39 19 19 9 20 20 38 21 21 10 22 22 37 23 23 11 24 24 36 25 25 12 26 26 35 27 27 13 28 28 34 29 29 14 30 30 33 31 31 15 32 32 32 33 33 16 34 34 31 35 35 17 36 36 30 37 37 18 38 38 29 39 39 19 40 40 28 41 41 20 42 42 27 43 43 21 44 44 26 45 45 22 46 46 25 47 47 23 48 48 24 49 49</p>

  Output: 49 49 0 0 48 48 1 1 0 0 2 2 0 0 2 2 48 48 1 1 47 47 3 3 0 0 2 2 47 47 3 3 1 1 4 4 1 1 4 4 47 47 3 3 46 46 5 5 1 1 4 4 46 46 5 5 2 2 6 6 2 2 6 6 46 46 5 5 45 45 7 7 2 2 6 6 45 45 7 7 3 3 8 8 3 3 8 8 45 45 7 7 44 44 9 9 3 3 8 8 44 44 9 9 4 4 10 10 4 4 10 10 44 44 9 9 43 43 11 11 4 4 10 10 43 43 11 11 5 5 12 12 5 5 12 12 43 43 11 11 42 42 13 13 5 5 12 12 42 42 13 13 6 6 14 14 6 6 14 14 42 42 13 13 41 41 15 15 6 6 14 14 41 41 15 15 7 7 16 16 7 7 16 16 41 41 15 15 40 40 17 17 7 7 16 16 40 40 17 17 8 8 18 18 8 8 18 18 40 40 17 17 39 39 19 19 8 8 18 18 39 39 19 19 9 9 20 20 9 9 20 20 39 39 19 19 38 38 21 21 9 9 20 20 38 38 21 21 10 10 22 22 10 10 22 22 38 38 21 21 37 37 23 23 10 10 22 22 37 37 23 23 11 11 24 24 11 11 24 24 37 37 23 23 36 36 25 25 11 11 24 24 36 36 25 25 12 12 26 26 12 12 26 26 36 36 25 25 35 35 27 27 12 12 26 26 35 35 27 27 13 13 28 28 13 13 28 28 35 35 27 27 34 34 29 29 13 13 28 28 34 34 29 29 14 14 30 30 14 14 30 30 34 34 29 29 33 33 31 31 14 14 30 30 33 33 31 31 15 15 32 32 15 15 32 32 33 33 31 31 32 32 33 33 15 15 32 32 32 32 33 33 16 16 34 34 16 16 34 34 32 32 33 33 31 31 35 35 16 16 34 34 31 31 35 35 17 17 36 36 17 17 36 36 31 31 35 35 30 30 37 37 17 17 36 36 30 30 37 37 18 18 38 38 18 18 38 38 30 30 37 37 29 29 39 39 18 18 38 38 29 29 39 39 19 19 40 40 19 19 40 40 29 29 39 39 28 28 41 41 19 19 40 40 28 28 41 41 20 20 42 42 20 20 42 42 28 28 41 41 27 27 43 43 20 20 42 42 27 27 43 43 21 21 44 44 21 21 44 44 27 27 43 43 26 26 45 45 21 21 44 44 26 26 45 45 22 22 46 46 22 22 46 46 26 26 45 45 25 25 47 47 22 22 46 46 25 25 47 47 23 23 48 48 23 23 48 48 25 25 47 47 24 24 49 49

   Parameters:
    line_in: the input string from one line of the file
   Returns:
    line_out: the output string


README for Blender Script
---------------------------
**Instructions:**

First, copy the "import_catia_dae.py" file in this folder somewhere in your
local drive. Then, open up Blender, and go to File -> User Preferences and
click on the Add-ons tab. You should see the screen below.

.. image:: BLENDER\\image1.jpg
    :align: center

Click on Install Add-on from File ... and find the "import_catia_dae.py" file
from your local drive and click Install Add-on from File ... on the top right
like the screen below.

.. image:: BLENDER\\image2.jpg
    :align: center

Then, type import in the search box on the Add-ons tab in File -> User
Preferences like the screen below.

.. image:: BLENDER\\image3.jpg
    :align: center

Then, select the checkbox on Import-Export: Import Collada from CATIA
like shown below and click Save User Settings on the bottom left.

.. image:: BLENDER\\image4.jpg
    :align: center

Once this is done, close the User Preferences and go to File -> Import ->
Collada from CATIA like shown below.

.. image:: BLENDER\\image5.jpg
    :align: center

Then, you can import the appropriate file by clicking on the file and then
clicking import like shown below.

.. image:: BLENDER\\image6.jpg
    :align: center

RMIT GUI
---------
**For an overview of how this is utilized, please refer to the intro section of this wiki.**

 .. automodule:: RMITGUIProcess
    :members:

README for RMIT GUI
--------------------
Open the RMITGUIProcess.exe

 .. image:: RMITGUI\\image1.jpg
    :align: center

Select the Decimation Option and .dae file to process

 .. image:: RMITGUI\\image2.jpg
    :align: center

Make sure that an instance of 3ds max is open and click *process*.

 .. image:: RMITGUI\\image3.jpg
    :align: center

Ensure that the processed file is accurate and ready for export

 .. image:: RMITGUI\\image4.jpg
    :align: center