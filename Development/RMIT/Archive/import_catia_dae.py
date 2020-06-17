"""
Author: Arjun Ayyangar (Summer NIFS KSC Intern)
Date: 7/26/2018

09/06/18: Began updates, modularization to existing code. Implemented
function setLineTemp to modify line_in to conform to OpenCOLLADA standard.
Author: William Little
"""
import bpy
import fileinput;
import math
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import os
from math import radians
from mathutils import Matrix

bl_info = {
    "name": "Import Collada from CATIA 09/17/18 b",
    "author": "Arjun Ayyangar",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "Import Collada files from CATIA V5 + ",
    "category": "Import-Export"
}

def import_collada(path):
    bpy.ops.wm.collada_import(filepath=path)


def load(operator, context, **args):
    filepath = args["filepath"]
    name = os.path.split(filepath)[-1].split(".")[0]
    parts = os.path.splitext(filepath)
    ext = parts[1].lower()
    if ext == ".dae":
        import_collada(updateFile(filepath))

        #
        # Delete temporary file here: Comment out
        # the next line if temporary file requires
        # inspection post processing.
        #
        # os.remove(updateFile(filepath))

    else:
        raise RuntimeError("Unknown extension: %s" % ext)
    return {"FINISHED"}

class Tagline:
    """
        Class Tagline: a class containing all the elements of a line of
        input COLLADA XML.
    """
    def __init__(self):
        """
            Method __init__: Automatically initialize all variables of the
            instance of Tagline when it is created.
        """
        self.line = ""
        self.inside_asset = False
        self.inside_library_visual_scenes = False
        self.inside_library_nodes = False
        self.inside_visual_scene = False
        self.inside_node = False
        self.inside_mesh = False
        self.inside_triangles = False
        self.inside_tristrips = False
        self.inside_trifans = False
        self.found_triangles = False
        self.found_tristrips = False
        self.found_trifans = False
        self.found_uv = False
        self.line_triangle = ""
        self.line_vertex = ""
        self.texcoord1 = ""
        self.texcoord2 = ""
        self.line_out = ""
        self.line_orig_out = ""
        self.tag_count = 0
        self.geometry_library_name = ""
        self.geometry_library_id = ""
        self.geometry_library_id_num = 0

    def store_line(self, line_in):
        """
            Method store_line: Store the current input xml line in the
            object for future processing.
        :param line_in:
        :return:
        """
        self.line = line_in

    def extract_geometry_library_name(self):
        """
            Method extract_geometry_library_name: Extract the name of the input
            geometry library for use in creating names and ID's.
        :return:
        """
        self.geometry_library_id_num = 0
        index1 = self.line.find('name="')
        if index1 != -1:
            index_start = index1 + 6
        else:
            self.geometry_library_name = "geometry"
            self.geometry_library_id = self.geometry_library_name + str(self.geometry_library_id_num)
            self.geometry_library_id_num += 1
            return
        index2 = self.line.find(".")
        if index2 != -1:
            index_end = index2
        else:
            index_end = len(self.line) - 1

        self.geometry_library_name = self.line[index_start:index_end]
        self.geometry_library_id = self.geometry_library_name + str(self.geometry_library_id_num)
        self.geometry_library_id_num = self.geometry_library_id_num + 1
        self.line_out = '<library_geometries name="' + self.geometry_library_name + '" id="' + self.geometry_library_id + '">'


class ImportCATIA(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.catia"
    bl_label = "Import"
    filter_glob = StringProperty(
        default="*.dae",
        options={"HIDDEN"})

    def execute(self, context):
        keywords = self.as_keywords()
        return load(self, context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportCATIA.bl_idname, text="Collada from CATIA")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)




def updateFile(fileName):
    """
   This is the main function that reads every line in the file and calls various functions based on the tags. It runs
   the algorithm on the original imported file to create a temporary file, which is then imported into blender.
   The temporary file is deleted after successful import. The temporary file name takes the process id from the
   operating system in order to get a unique file name.
   Parameters:
       fileName: the original file name with path for the imported DAE file
   Returns:
       newfileName: The new file name with path for the modified temporary updated file.
   """

    # Clear the Blender system console
    os.system("cls")

    # Set the directory path to the input COLLADA file, open for reading
    filedir = os.path.dirname(fileName)
    infile = open(fileName, 'r')
    print("fileName :", fileName)

    # Read the input file into the content object
    content = infile.readlines()
    newfileName = filedir + '/temp_' + str(os.getpid()) + '.dae'
    print("newfileName: ", newfileName)
    outfile = open(newfileName, 'w')
    # Initialize variables

    # Create xml object from Tagline class, use to retain data while processing input COLLADA file
    xml = Tagline()

    insideMesh = False  # True if the line is inside a mesh tag
    insideTriangles = False  # True if the line is inside a triangles tag
    insideTristrips = False  # True if the line is inside a tristrips tag
    insideTrifans = False  # True if the line is inside a trifans tag
    strOut = ""  # Placeholder string before building the actual line output
    line_triangle = ""  # Save off the new triangle line after converting
    line_vertex = ""  # Save off the new vertex line after converting
    line_normal = ""  # Save off the new normal line after converting
    line_texcoord1 = ""  # Save off the new first texcoord line after converting
    line_texcoord2 = ""  # Save off the new second texcoord line after converting
    line_out = ""  # Save off modified info
    line_orig_out = ""  # Save off the original info
    tagCount = 0  # Add to the count if triangles/tristrips/trifans are found with TEXCOORD semantic
    foundTristrips = False  # True if tristrips tag is found inside the mesh
    foundTrifans = False  # True if trifans tag is found inside the mesh
    foundTriangles = False  # True if triangles tag is found inside the mesh
    foundUV = False  # True if semantic="UV" is found inside the mesh

    # Loop through each line of the import file
    for line_in in content:

        # Store the unedited line_in in the xml object
        xml.store_line(line_in)
        # print("xml.line: ", xml.line)

        # Find the input string "<unit": Substitute inches for millimeters.
        # Note: This substitution is global for wherever the unit tag is found.
        if find_string("<unit ", line_in):
            outfile.write(line_in[0:line_in.find('<')] + '<unit name="inch" meter="0.0254"/>\n')
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "<translate>": convert values from metric (millimeters) to English (inches)
        # Note: This conversion is global for wherever the translate tag is found.
        if find_string("<translate>", line_in):
            outfile.write(scaleDown(line_in))  # Scale down translate values by a factor of 25.4
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "<asset>": Set xml.inside_asset to TRUE
        if find_string("<asset>", line_in):
            outfile.write(line_in)
            xml.inside_asset = True
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "</asset>": Set xml.inside_asset to FALSE
        if find_string("</asset>", line_in):
            outfile.write(line_in)
            xml.inside_asset = False
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "<library_visual_scenes>": Set xml.inside_library_visual_scenes to TRUE
        if find_string("<library_visual_scenes>", line_in):
            xml.inside_library_visual_scenes = True
            outfile.write(line_in)
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "</library_visual_scenes>": Set xml.inside_library_visual_scenes to FALSE
        if find_string("</library_visual_scenes>", line_in):
            xml.inside_library_visual_scenes = False
            outfile.write(line_in)
            # print("xml.line: ", xml.line)
            continue
        # Find the input string "<library_nodes ": Set xml.inside_library_nodes to TRUE
        if find_string("<library_nodes ", line_in):
            xml.inside_library_nodes = True
            outfile.write(line_in)
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "</library_nodes ": Set xml.inside_library_nodes to FALSE
        if find_string("</library_nodes>", line_in):
            xml.inside_library_nodes = False
            outfile.write(line_in)
            # print("xml.line: ", xml.line)
            continue

        # Find the input string "<library_geometries": Save library attributes
        if find_string("<library_geometries", line_in):
            xml.extract_geometry_library_name()
            # print("xml.geometry_library_name: ", xml.geometry_library_name)
            # print("xml.geometry_library_id: ", xml.geometry_library_id)
            # print("xml.line_out: ", xml.line_out)

        # Left these lines commented for future rotate algorithm updates
        # if not (line_in.find("<rotate>") == -1):
        #   outfile.write(rotateValues(line_in))
        #   continue
        line_in = line_in.replace(' name="vertices">', ">")
        line_in = line_in.replace(' name="normals">', ">")
        line_in = line_in.replace(' name="texcoords">', ">")

        # Find the input string "uvparams": Set foundUV boolean to TRUE
        if find_string('"uvparams"', line_in):
            foundUV = True
            continue

        if (foundUV):
            if line_in.find("</source>") != -1:
                foundUV = False
            continue

        # Find the input string "<mesh>": Set insideMesh boolean to TRUE
        if find_string("<mesh>", line_in):
            insideMesh = True

        # Find the input string "<float_array": convert float array values from metric to English
        if find_string("<float_array", line_in):
            #  If count = 0 is found, then account for the missing </float_array> tag
            if find_string('count="0"', line_in):
                outfile.write(fixZeroCountParam(line_in))
                continue
            elif not find_string('count="0"', line_in):  # line_in.find('count="0"') == notFound:
                outfile.write(remove_float_array_attributes(line_in))
                continue

        # Write all the triangles/semantic lines before closing out the mesh tag
        if find_string("</mesh>", line_in):
            #  if line_in.find("</mesh>") != notFound:
            # Calculate and update the count attribute for the output triangles tag
            process_mesh(line_texcoord1, line_texcoord2, line_out, line_orig_out, foundTriangles,
                         foundTristrips, foundTrifans, line_vertex, line_normal, line_triangle, outfile)

            # Reinitialize all the variables again for the next mesh
            insideMesh = False
            strOut = ""
            line_triangle = ""
            line_vertex = ""
            line_normal = ""
            line_texcoord1 = ""
            line_texcoord2 = ""
            line_out = ""
            line_orig_out = ""
            tagCount = 0
            foundTristrips = False
            foundTrifans = False
            foundTriangles = False
            foundUV = False

        # If line is outside the mesh tags, write as is
        if not (insideMesh):
            outfile.write(line_in)
            continue

        # Find the input string "<triangles": start of triangle tag
        if find_string("<triangles ", line_in):
            insideTriangles = True
            foundTriangles = True
            tagCount = tagCount + 1

        # Find the input string "</triangles>": end of triangle tag
        if find_string("</triangles>", line_in):
            line_in = ""
            insideTriangles = False

        # Find the input string "<tristrips ": start of tristrips tag
        if find_string("<tristrips ", line_in):
            line_in = line_in.replace("tristrips", "triangles")
            insideTristrips = True
            foundTristrips = True
            tagCount = tagCount + 1

        # Find the input string "</tristrips>": end of tristrips tag
        if find_string("</tristrips>", line_in):
            line_in = ""
            insideTristrips = False

        # Find the input string "<trifans ": start of trifans tag
        if find_string("<trifans ", line_in):
            line_in = line_in.replace("trifans", "triangles")
            insideTrifans = True
            foundTrifans = True
            tagCount = tagCount + 1

        # Find end of trifans tag
        if find_string("</trifans>", line_in):
            line_in = ""
            insideTrifans = False

        # Find the input string 'semantic="UV"': Semantic UV, ignore it
        if find_string('semantic="UV" ', line_in):
            line_in = ""

        # Write input line as is, if not inside the tristrips/trifans/triangles tag
        if insideTristrips == False and insideTrifans == False and insideTriangles == False:
            outfile.write(line_in)
            continue

        # Assume no TEXCOORD semantic, but save off original line in case it is found
        if find_string("<p>", line_in):
            line_out = line_out + convertNoTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in)
            line_orig_out = line_orig_out + line_in
            continue

        strOut = line_in.replace("tristrips", "triangles")
        strOut = strOut.replace("trifans", "triangles")

        if find_string('<triangles', strOut):
            line_triangle = strOut
            strOut = ""

        # Find the input string 'semantic="VERTEX" ': Semantic VERTEX
        if find_string('semantic="VERTEX" ', strOut):
            line_vertex = strOut
            strOut = ""

        # Find the input string 'semantic="NORMAL" ': Semantic NORMAL
        if find_string('semantic="NORMAL" ', strOut):
            strOut = strOut.replace('<input offset="0" semantic="NORMAL"', '<input offset="1" semantic="NORMAL"')
            line_normal = strOut
            strOut = ""

        # Find the input string 'semantic="TEXCOORD" ': Semantic TEXCOORD
        if find_string('semantic="TEXCOORD" ', strOut):
            strOut = modify_semantic_TEXCOORD(strOut)
            if line_texcoord1 == "":
                line_texcoord1 = line_texcoord1 + "\n" + strOut
            else:
                if tagCount <= 1:
                    line_texcoord2 = line_texcoord2 + "\n" + strOut
            strOut = ""

        # Write the converted string
        outfile.write(strOut)
    infile.close()
    outfile.close()
    return newfileName

# End of main routine: Begin main support functions.


def fixZeroCountParam(line_in):
    """
    Function fixZeroCountParam: if line_in contains a <float array> tag with zero elements,
    modify the line to insert a 'count="0"/>\n' closing. Return the modified string to the
    main procedure.
    """
    temp_out = line_in
    temp_start = temp_out.find('count="0"')
    return temp_out[0:temp_start] + 'count="0"' + "/>\n"


def remove_float_array_attributes(line_in):
    """
    Function remove_float_array_attributes: If the magnitude attribute of the
    float array is set to 1, call function scaleDown. Remove the magnitude and
    digits attributes from the array's definition.
    """
    # print("remove_float_array_attributes:")
    tmpOut = line_in
    # Scale down float array values if magnitude is not 1
    # if line_in.find('magnitude="1"') == -1:
    # 10/10/18: Modify logic to accept all magnitudes
    if not find_string('magnitude="1"', line_in):
        #  if find_string("magnitude=", line_in):
        tmpOut = scaleDown(line_in)
        # print(" tmpOut: ", tmpOut)
    # Remove magnitude attributes from float_array tag
    tmpStart = tmpOut.find(" magnitude")
    if not (tmpStart == -1):
        tmpEnd = tmpOut.find('>')
        tmpOutNew = tmpOut[0:tmpStart] + tmpOut[tmpEnd:]
        tmpOut = tmpOutNew
    # Remove digits attributes from float_array tag
    tmpStart = tmpOut.find(" digits")
    if not (tmpStart == -1):
        tmpEnd = tmpOut.find('>')
        tmpOutNew = tmpOut[0:tmpStart] + tmpOut[tmpEnd:]
        tmpOut = tmpOutNew
    return tmpOut


def process_mesh(line_texcoord1, line_texcoord2, line_out, line_orig_out, foundTriangles,
                 foundTristrips, foundTrifans, line_vertex, line_normal, line_triangle, outfile):
    """
    Function process_mesh: process all the elements found inside the <mesh> and </mesh> tags.
    :param line_texcoord1:
    :param line_texcoord2:
    :param line_out:
    :param line_orig_out:
    :param foundTriangles:
    :param foundTristrips:
    :param foundTrifans:
    :param line_vertex:
    :param line_normal:
    :param line_triangle:
    :param outfile:
    :return:
    """
    intCount = 1
    if not (line_texcoord2 == ""):
        # Convert the original line if two TEXCOORDs are found
        if foundTristrips == True:
            line_out = tristripsToTriangleDoubleTEXCOORD(line_orig_out)
            # print("line_out: ", line_out, " (close_out_mesh_1)")
            intCount = len(list(map(int, line_out.split()))) / 12
    else:
        if not (line_texcoord1 == ""):
            convertSingleTEXCOORD(foundTriangles, foundTristrips, foundTrifans, line_orig_out)
            intCount = len(list(map(int, line_out.split()))) / 9
        else:
            intCount = len(list(map(int, line_out.split()))) / 6
    if not (line_out == ""):
        # Find the original Count attribute
        startNum = line_triangle.find('count="') + 7
        endNum = line_triangle.find('" material=')
        strCountWithDecimal = str(intCount)
        strDecimalPosition = strCountWithDecimal.find('.')
        strCountWithoutDecimal = strCountWithDecimal[0:strDecimalPosition]
        # Write the line after replacing the new Count attribute
        outfile.write(line_triangle[0:startNum] + strCountWithoutDecimal + line_triangle[endNum:])
        # Write the individual semantic lines
        outfile.write(line_vertex)
        outfile.write(line_normal)
        outfile.write(line_texcoord1)
        outfile.write(line_texcoord2)
        outfile.write("<p>" + line_out + "</p>\n</triangles>\n")
    return intCount


def modify_semantic_TEXCOORD(strOut):
    """
    Function modify_semantic_TEXCOORD: modify the output string str_temp to the requisite
    Open COLLADA format and return the result.
    :param strOut:
    :return:
    """
    str_temp = strOut.replace(' set="0"', "")
    str_temp = strOut.replace('<input offset="2" semantic="TEXCOORD"', '<input offset="3" semantic="TEXCOORD"')
    return str_temp.replace('<input offset="1" semantic="TEXCOORD"', '<input offset="2" semantic="TEXCOORD"')


def convertSingleTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in):
    """
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
   """
    if (insideTriangles):
        return (triangleToTriangleSingleTEXCOORD(line_in))
    if (insideTristrips):
        return (tristripsToTriangleSingleTEXCOORD(line_in))
    if (insideTrifans):
        return (trifansToTriangleSingleTEXCOORD(line_in))
    return (line_in)



def triangleToTriangleSingleTEXCOORD(line_in):
    """
   The function takes an input string that extracts the numbers between the <p> tags 
   within the triangle tag. 
   This function is only for a mesh with single TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Example:
      Input: <p>0 0 19 1 20 2 1 3 24 4 25 5 25 5 2 6 1 3 26 7 2 6 25 5 3 8 27 9 28 10 28 10 4 11 3 8 29 12 4 11 28 10 1 3 17 13 18 14</p>
      Output: 0 0 0 19 19 1 20 20 2 1 1 3 24 24 4 25 25 5 25 25 5 2 2 6 1 1 3 26 26 7 2 2 6 25 25 5 3 3 8 27 27 9 28 28 10 28 28 10 4 4 11 3 3 8 29 29 12 4 4 11 28 28 10 1 1 3 17 17 13 18 18 14
   Parameters:
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(0, len(list(vertex)), 2):
        newVertex = str(vertex[i]) + " " + str(vertex[i]) + " " + str(vertex[i + 1])
        line_out = line_out + newVertex + " "
    return line_out.strip()


def trifansToTriangleSingleTEXCOORD(line_in):
    """
   The function takes an input string that extracts the numbers between the <p> tags 
   within the trifans tag. 
   This function is only for a mesh with single TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Example:
      Input: <p>19 0 18 1 22 2 21 3 20 4</p>
      Output: 19 19 0 18 18 1 22 22 2 19 19 0 22 22 2 21 21 3 19 19 0 21 21 3 20 20 4
   Parameters:
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(2, len(list(vertex)) - 3, 2):
        newVertex = str(vertex[0]) + " " + str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[i]) + " " + str(
            vertex[i]) + " " + str(vertex[i + 1]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(
            vertex[i + 3])
        line_out = line_out + newVertex + " "
    return line_out.strip()


def tristripsToTriangleSingleTEXCOORD(line_in):
    """
   The function takes an input string that extracts the numbers between the <p> tags 
   within the tristrips tag. 
   This function is only for a mesh with single TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Example:
      Input: <p>1 0 1 0 0 1 2 2 3 3</p>
      Output: 1 1 0 1 1 0 0 0 1 0 0 1 1 1 0 2 2 2 0 0 1 2 2 2 3 3 3
   Parameters:
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(0, len(list(vertex)) - 1, 4):
        if ((i + 6) <= len(list(vertex))):
            newVertex = str(vertex[i]) + " " + str(vertex[i]) + " " + str(vertex[i + 1]) + " " + str(
                vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 3]) + " " + str(
                vertex[i + 4]) + " " + str(vertex[i + 4]) + " " + str(vertex[i + 5])
            line_out = line_out + newVertex + " "
        if ((i + 8) <= len(list(vertex))):
            newVertex = str(vertex[i + 4]) + " " + str(vertex[i + 4]) + " " + str(vertex[i + 5]) + " " + str(
                vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 3]) + " " + str(
                vertex[i + 6]) + " " + str(vertex[i + 6]) + " " + str(vertex[i + 7])
            line_out = line_out + newVertex + " "
    return line_out.strip()


def scaleDown(line_in):
    """
     The function takes an input string that extracts the numbers between > and </.
     Returns an output string with the numbers scaled down by 25.4 (convert millimeters to inches)
     along with its appropriate tags
     Parameters:
        line_in: the input string from one line of the file
     Returns:
         line_out: the output string
     """
    startNum = line_in.find('>')
    endNum = line_in.find('</')
    line_tmp = line_in[startNum + 1:endNum - 1]
    try:
        vertex = [float(x) for x in line_tmp.split()]
    except:
        print("Exception: line_tmp: ", line_tmp)
    line_out = line_in[0:startNum + 1]
    for i in range(0, len(list(vertex))):
        vertex[i] /= 25.4
        strVertex = str(vertex[i])
        line_out = line_out + strVertex + " "
    if not (line_in.find(' 0</') == -1):
        line_out = line_out + "0"
    line_out = line_out + line_in[endNum:]
    return line_out


def rotateValues(line_in):
    """
     The function takes an input string that extracts the numbers between the rotate tags.
     Returns an output string by negating each number if the first number is -0.57735
     There seems to be inconsistency with the pattern match for rotate, Therefore, this
     function is not used, but is left here for future updates to the rotate algorithm
     Parameters:
        line_in: the input string from one line of the file
     Returns:
         line_out: the output string
     """
    line_tmp = setLineTemp(line_in, "<rotate>", "</rotate>")
    value = [float(x) for x in line_tmp.split()]
    line_out = "<rotate>"
    if (value[0] == -0.57735):
        for i in range(0, 4):
            value[i] = - value[i]
            strVertex = str(value[i])
            line_out = line_out + strVertex + " "
        line_out = line_out + "</rotate>"
    else:
        line_out = line_in
    return line_out


if __name__ == "__main__":
    register()





def convertNoTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in):
    """
   The function takes an input string and calls the appropriate convert function
   based on triangle/tristrips/trifans tag.
   This function is only for a mesh with no TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Parameters:
      insideTriangles: boolean true if the <p> values belong to a triangle tag, else false
      insideTristrips: boolean true if the <p> values belong to a tristrips tag, else false
      insideTrifans: boolean true if the <p> values belong to a trifans tag, else false
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    if (insideTriangles):
        return (triangleToTriangleNoTEXCOORD(line_in))
    if (insideTristrips):
        return (tristripsToTriangleNoTEXCOORD(line_in))
    if (insideTrifans):
        return (trifansToTriangleNoTEXCOORD(line_in))
    return (line_in)


def triangleToTriangleNoTEXCOORD(line_in):
    """
    The function takes an input string that extracts the numbers between the <p> tags
    within the triangle tag.
    This function is only for a mesh with no TEXCOORD semantic.
    Returns an output set of numbers without the tags, after applying the appropriate algorithm.
    Example:
       Input: <p>190 231 232 196 197 205 298 297 256 271 263 262</p>
       Output: 190 190 231 231 232 232 196 196 197 197 205 205 298 298 297 297 256 256 271 271 263 263 262 262
    Parameters:
       line_in: the input string from one line of the file
    Returns:
       line_out: the output string
    """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(0, len(list(vertex))):
        newVertex = str(vertex[i]) + " " + str(vertex[i])
        line_out = line_out + newVertex + " "
    return line_out  # .strip()


def tristripsToTriangleNoTEXCOORD(line_in):
    """
   The function takes an input string that extracts the numbers between the <p> tags 
   within the tristrips tag. 
   This function is only for a mesh with no TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Example:
      Input: <p>839 839 910 840 909 908</p>
      Output: 839 839 839 839 910 910 910 910 839 839 840 840 910 910 840 840 909 909 909 909 840 840 908 908
   Parameters:
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    new_vertex = ''
    mod = len(list(vertex)) % 4
    # print("mod: ", mod)
    totals = len(list(vertex))
    # print("totals: ", totals)
    max_index = len(list(vertex)) - mod - 1
    # print("max_index: ", max_index)
    # for i in range(0, len(list(vertex)) - 6, 6):
    for i in range(0, max_index - 1, 2):
        new_vertex = concat_vertices(vertex[i], vertex[i]) + " " + \
                     concat_vertices(vertex[i + 1], vertex[i + 1]) + " " + \
                     concat_vertices(vertex[i + 2], vertex[i + 2]) + " " + \
                     concat_vertices(vertex[i + 2], vertex[i + 2]) + " " + \
                     concat_vertices(vertex[i + 1], vertex[i + 1]) + " " + \
                     concat_vertices(vertex[i + 3], vertex[i + 3]) + " "
        line_out = line_out + new_vertex

    if mod == 1:
        return line_out  + concat_mod(vertex, max_index, -1, 0, 1)

    if mod == 2:
        return line_out + concat_mod(vertex, max_index, -1, 0, 1) + \
                          concat_mod(vertex, max_index, 1, 0, 2)

    if mod == 3:
        return line_out  + concat_mod(vertex, max_index, -1, 0, 1) + \
                           concat_mod(vertex, max_index, 1, 0, 2) + \
                           concat_mod(vertex, max_index, 1, 2, 3)

    return line_out  # .strip()


def concat_mod(vertex, max_index, i1, i2, i3):
    """
    Function concat_mod: If the modulus of the length of a sequence of tristrip vertices
    is greater than 0, return the concatenated "left over" vertices to the end of the line_out
    variable in the calling routine.
    :param vertex:
    :param max_index:
    :param i1:
    :param i2:
    :param i3:
    :return:
    """
    return concat_vertices(vertex[max_index + i1], vertex[max_index + i1]) + " " + \
           concat_vertices(vertex[max_index + i2], vertex[max_index + i2]) + " " + \
           concat_vertices(vertex[max_index + i3], vertex[max_index + i3]) + " "


def concat_vertices(vertex1, vertex2):
    """
    Function concat_vertices: Concatenate two input vertices separated by a blank character
    and return the resulting string.
    :param vertex1:
    :param vertex2:
    :return:
    """
    return str(vertex1) + " " + str(vertex2)


def trifansToTriangleNoTEXCOORD(line_in):
    """
    The function takes an input string that extracts the numbers between the <p> tags
    within the trifans tag.
    This function is only for a mesh with no TEXCOORD semantic.
    Returns an output set of numbers without the tags, after applying the appropriate algorithm.
    Example:
       Input: <p>405 404 430 429 428 427 426 425 424 423 422 406</p>
       Output: 405 405 404 404 430 430 405 405 430 430 429 429 405 405 429 429 428 428 405 405 428 428 427 427 405 405 427 427 426 426 405 405 426 426 425 425 405 405 425 425 424 424 405 405 424 424 423 423 405 405 423 423 422 422 405 405 422 422 406 406
    Parameters:
       line_in: the input string from one line of the file
    Returns:
       line_out: the output string
    """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(1, len(list(vertex)) - 1):
        newVertex = str(vertex[0]) + " " + str(vertex[0]) + " " + \
                    str(vertex[i]) + " " + str(vertex[i]) + " " + \
                    str(vertex[i + 1]) + " " + str(vertex[i + 1])
        line_out = line_out + newVertex + " "
    return line_out


def tristripsToTriangleDoubleTEXCOORD(line_in):
    """
   The function takes an input string that extracts the numbers between the <p> tags 
   within the tristrips tag. 
   This function is only for a mesh with no TEXCOORD semantic.
   Returns an output set of numbers without the tags, after applying the appropriate algorithm.
   Example:
      Input: <p>49 0 0 48 1 1 0 2 2 47 3 3 1 4 4 46 5 5 2 6 6 45 7 7 3 8 8 44 9 9 4 10 10 43 11 11 5 12 12 42 13 13 6 14 14 41 15 15 7 16 16 40 17 17 8 18 18 39 19 19 9 20 20 38 21 21 10 22 22 37 23 23 11 24 24 36 25 25 12 26 26 35 27 27 13 28 28 34 29 29 14 30 30 33 31 31 15 32 32 32 33 33 16 34 34 31 35 35 17 36 36 30 37 37 18 38 38 29 39 39 19 40 40 28 41 41 20 42 42 27 43 43 21 44 44 26 45 45 22 46 46 25 47 47 23 48 48 24 49 49</p>
      Output: 49 49 0 0 48 48 1 1 0 0 2 2 0 0 2 2 48 48 1 1 47 47 3 3 0 0 2 2 47 47 3 3 1 1 4 4 1 1 4 4 47 47 3 3 46 46 5 5 1 1 4 4 46 46 5 5 2 2 6 6 2 2 6 6 46 46 5 5 45 45 7 7 2 2 6 6 45 45 7 7 3 3 8 8 3 3 8 8 45 45 7 7 44 44 9 9 3 3 8 8 44 44 9 9 4 4 10 10 4 4 10 10 44 44 9 9 43 43 11 11 4 4 10 10 43 43 11 11 5 5 12 12 5 5 12 12 43 43 11 11 42 42 13 13 5 5 12 12 42 42 13 13 6 6 14 14 6 6 14 14 42 42 13 13 41 41 15 15 6 6 14 14 41 41 15 15 7 7 16 16 7 7 16 16 41 41 15 15 40 40 17 17 7 7 16 16 40 40 17 17 8 8 18 18 8 8 18 18 40 40 17 17 39 39 19 19 8 8 18 18 39 39 19 19 9 9 20 20 9 9 20 20 39 39 19 19 38 38 21 21 9 9 20 20 38 38 21 21 10 10 22 22 10 10 22 22 38 38 21 21 37 37 23 23 10 10 22 22 37 37 23 23 11 11 24 24 11 11 24 24 37 37 23 23 36 36 25 25 11 11 24 24 36 36 25 25 12 12 26 26 12 12 26 26 36 36 25 25 35 35 27 27 12 12 26 26 35 35 27 27 13 13 28 28 13 13 28 28 35 35 27 27 34 34 29 29 13 13 28 28 34 34 29 29 14 14 30 30 14 14 30 30 34 34 29 29 33 33 31 31 14 14 30 30 33 33 31 31 15 15 32 32 15 15 32 32 33 33 31 31 32 32 33 33 15 15 32 32 32 32 33 33 16 16 34 34 16 16 34 34 32 32 33 33 31 31 35 35 16 16 34 34 31 31 35 35 17 17 36 36 17 17 36 36 31 31 35 35 30 30 37 37 17 17 36 36 30 30 37 37 18 18 38 38 18 18 38 38 30 30 37 37 29 29 39 39 18 18 38 38 29 29 39 39 19 19 40 40 19 19 40 40 29 29 39 39 28 28 41 41 19 19 40 40 28 28 41 41 20 20 42 42 20 20 42 42 28 28 41 41 27 27 43 43 20 20 42 42 27 27 43 43 21 21 44 44 21 21 44 44 27 27 43 43 26 26 45 45 21 21 44 44 26 26 45 45 22 22 46 46 22 22 46 46 26 26 45 45 25 25 47 47 22 22 46 46 25 25 47 47 23 23 48 48 23 23 48 48 25 25 47 47 24 24 49 49
   Parameters:
      line_in: the input string from one line of the file
   Returns:
      line_out: the output string
   """
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    newVertex = ''
    for i in range(0, len(list(vertex)) - 6, 6):
        newVertex = str(vertex[i]) + " " + str(vertex[i])
        if (len(list(vertex)) > (i + 1)):
            newVertex = newVertex + " " + str(vertex[i + 1])
        if (len(list(vertex)) > (i + 2)):
            newVertex = newVertex + " " + str(vertex[i + 2])
        if (len(list(vertex)) > (i + 3)):
            newVertex = newVertex + " " + str(vertex[i + 3]) + " " + str(vertex[i + 3])
        if (len(list(vertex)) > (i + 4)):
            newVertex = newVertex + " " + str(vertex[i + 4])
        if (len(list(vertex)) > (i + 5)):
            newVertex = newVertex + " " + str(vertex[i + 5])
        if (len(list(vertex)) > (i + 6)):
            newVertex = newVertex + " " + str(vertex[i + 6]) + " " + str(vertex[i + 6])
        if (len(list(vertex)) > (i + 7)):
            newVertex = newVertex + " " + str(vertex[i + 7])
        if (len(list(vertex)) > (i + 8)):
            newVertex = newVertex + " " + str(vertex[i + 8]) + " " + str(vertex[i + 6]) + " " + str(
                vertex[i + 6]) + " " + str(vertex[i + 7]) + " " + str(vertex[i + 8])
        if (len(list(vertex)) > (i + 9)):
            newVertex = newVertex + " " + str(vertex[i + 3]) + " " + str(vertex[i + 3]) + " " + str(
                vertex[i + 4]) + " " + str(vertex[i + 5]) + " " + str(vertex[i + 9]) + " " + str(
                vertex[i + 9]) + " " + str(vertex[i + 10]) + " " + str(vertex[i + 11])
        line_out = line_out + newVertex + " "

    return line_out.strip()


def setLineTemp(line_in, openTag, closeTag):
    """
    Function setLineTemp: replace opening and closing XML tags in line_in with openTag and closeTag
    parameters, return updated line_temp to calling method.
    """

    line_temp = line_in.replace(openTag, "")
    line_temp = line_temp.replace(closeTag, "")
    return line_temp


def find_string(target, line_in):
    """
    Function find_string:  search input line_in for an instance of string target. If the string is
    not found, return False. Otherwise, return True
    :param target:
    :param line_in:
    :return:
    """
    if line_in.find(target) == -1:
        return False
    else:
        return True



