"""

Author: Arjun Ayyangar (Summer NIFS KSC Intern)
Date: 7/26/2018

09/06/18: Began updates, modularization to existing code. Implemented
function setLineTemp to modify line_in to conform to OpenCOLLADA standard.
Author: William Little

03/14/19: Removed all plugin information and left just the utility functions.
This will be called by a driver script to process dae files. 
Author: Joseluis Chavez
"""

"""
    IMPORT Section: Use Python import function to import functions and data used to perform Blender interface, 
    Python mathematics and operating system interface functions.
"""
"""
import bpy: A Blender module that provides Python with access to Blender data, classes, and functions. The
bpy module is required when dealing with Blender data. From the submodule bpy.props import StringProperty. 
From the submodule bpy_extras.ioutils import ImportHelper.
"""
import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


"""
import math: Import the Python math module so that the program can use predefined mathematical functions.
NOTE: the current program does not make use of radians, so the "from math import radians" statement is 
commented out (01/28/2019). Likewise, the Blender mathutils module and its submodule Matrix are not 
currently used.
"""
import math

"""
import os: Import Python operating system module to allow the program to interface with the OS, such as 
opening, reading, and closing files.
"""
import os


class Tagline:
    """
        Class Tagline: a class containing all the elements of a line of
        input COLLADA XML and the functions associated with processing that line of code so that the original
        COLLADA file is converted into the OPEN COLLADA format.
    """
    def __init__(self):
        """
            Method __init__: Automatically initialize all variables of the
            instance of Tagline when it is created.
        """
        self.line = ""
        self.new_line = ""
        self.inside_asset = False
        self.inside_library_visual_scenes = False
        self.inside_visual_scene = False
        self.inside_node = False
        self.inside_library_nodes = False
        self.inside_library_geometries = False
        self.inside_geometry = False
        self.inside_mesh = False
        self.inside_source = False
        self.is_uvparams = False
        self.inside_technique = False
        self.is_vertex = False
        self.inside_vertices = False
        self.inside_triangles = False
        self.is_tristrip = False
        self.tristrip_count = 0
        self.is_trifan = False
        self.trifan_count = 0
        self.is_triangle = False
        self.triangle_count = 0
        self.inside_library_effects = False
        self.inside_library_materials = False
        self.inside_scene = False
        self.line_triangle = ""
        self.line_vertex = ""
        self.triangle_texcoords = 0
        self.save_offset = 0
        self.save_triangle = ""
        self.save_vertex = ""
        self.save_normal = ""
        self.save_uv = ""
        self.save_texcoord_1 = ""
        self.save_texcoord_2 = ""
        self.save_tristrips_p = ""
        self.save_trifans_p = ""
        self.save_triangles_p = ""
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

    def fix_zero_count_param(self):
        temp_line = self.line
        temp_start = temp_line.find('count="0"')
        return temp_line[0:temp_start] + 'count="0"/>\n'

    def reformat_float_array_tag(self):
        """
            Method reformat_float_array_tag: If attributes ""magnitude" and/or "digits" are found in a float_array
            tag, remove them, save the updated string in self.new_line
        :return:
        """
        if self.is_vertex:
            temp_line = self.scale_metric()
            self.is_vertex = False
        else:
            temp_line = self.line
        if find_string('magnitude="', temp_line):
            temp_start = temp_line.find('magnitude="')
            temp_end = temp_line.find('>')
            temp_line = temp_line[0:temp_start] + temp_line[temp_end:]

        if find_string('digits="', temp_line):
            temp_start = temp_line.find('digits="')
            temp_end = temp_line.find('>')
            temp_line = temp_line[0:temp_start] + temp_line[temp_end:]

        return temp_line

    def scale_metric(self):
        """
            Method scale_metric: Find a character string representing a set of metric numbers (expressed in
            millimeters), convert each substring to its floating point equivalent, and convert that number to
            its English equivalent (expressed in inches), then reconvert back to a character string. Return the
            converted string to its calling function.
        :return:
        """
        begin_index = self.line.find('>') + 1
        end_index = self.line.find('</')
        line_temp_1 = self.line[begin_index:end_index]
        vertex_1 = [float(x) for x in line_temp_1.split()]
        vertex_2 = ""
        for i in range(0, len(list(vertex_1))):
            vertex_2 = vertex_2 + str(vertex_1[i] / 25.4) + " "
        vertex_2 = self.line[:begin_index] + vertex_2 + self.line[end_index:]
        return vertex_2

    def save_triangle_tag(self):
        """
            Method save_triangle_tag: If the tag for the current line of XML is a triangle, tristrip, or trifan,
            modify  the line to be a triangle tag, per OpenCOLLADA standard, save the line, and set the is_triangle,
            is_tristrip, or is_trifan boolean to True, based on which tag name is found.

        :return:
        """

        if find_string("<tristrips ", self.line):
            self.save_triangle = self.line.replace("<tristrips ", "<triangles ")
            self.is_tristrip = True
            self.tristrip_count += self.convert_count()
            return

        if find_string("<trifans ", self.line):
            self.save_triangle = self.line.replace("<trifans ", "<triangles ")
            self.is_trifan = True
            self.trifan_count += self.convert_count()
            return

        if find_string("<triangles ", self.line):
            self.save_triangle = self.line
            self.is_triangle = True
            self.triangle_count += self.convert_count()
            return

    def convert_count(self):
        """
        Function convert_count: find the 'count="xxx"' string in a triangle, tristrip, or trifan
        sturcture. Extract the string xxx, then convert it to an integer. Return the integer
        to the calling routine.
        :param:
        :return:
        """
        if find_string('count="', self.line):
            begin_index = self.line.find('"') + 1
            temp_line = self.line[begin_index:]
            end_index = temp_line.find('"')
            count_string = temp_line[:end_index]
            count_int = int(count_string)
            return count_int

    def save_input_tag(self):
        """
            Method save_input_tag: Upon finding an input tag, determine if the semantic attribute is VERTEX, NORMAL,
            UV, or TEXCOORD. Save the line for later processing. If TEXCOORD is found, increment the number of
            TEXCOORD attributes found for later processing.

        :return:
        """
        if find_string('semantic="VERTEX"', self.line):
            self.save_offset = 0
            self.save_vertex = self.line
            return
        if find_string('semantic="NORMAL"', self.line):
            self.save_offset = 1
            temp_int = str(self.save_offset)
            self.save_normal = self.line.replace('offset="0"', 'offset="' + temp_int + '"')
            return
        if find_string('semantic="UV"', self.line):
            return
        if find_string(' semantic="TEXCOORD" ', self.line):
            if find_string(' offset="1" ', self.line):
                self.triangle_texcoords += 1
                self.save_texcoord_1 = self.update_texcoord()
            if find_string(' offset="2" ', self.line):
                self.triangle_texcoords += 1
                self.save_texcoord_2 = self.update_texcoord()
            return

    def update_texcoord(self):
        """
            Method update_texcoord: Modify the line containing 'semantic="TEXCOORD"' to adhere to OpenCOLLADA
            standards.
        :return:
        """
        # print("update_texcoord: self.line: ", self.line)
        temp_line = self.line
        temp_int = self.save_offset + self.triangle_texcoords
        temp_char = str(temp_int)
        # print("temp_int: ", temp_int, " temp_char: ", temp_char)
        begin_index = temp_line.find('"')
        end_index = begin_index + 2
        temp_line = temp_line[:begin_index + 1] + temp_char + temp_line[end_index:]
        return temp_line

    def save_points(self):
        if self.is_triangle:
            if self.triangle_texcoords == 0:
                self.save_triangles_p = self.save_triangles_p + self.triangles_to_triangles_no_texcoord()
            elif self.triangle_texcoords == 1:
                self.save_triangles_p = self.save_triangles_p + self.triangles_to_triangles_single_texcoord()
        elif self.is_tristrip:
            if self.triangle_texcoords == 0:
                self.save_tristrips_p = self.save_tristrips_p + self.tristrips_to_triangles_no_texcoord()
            elif self.triangle_texcoords == 1:
                self.save_tristrips_p = self.save_tristrips_p + self.tristrips_to_triangles_single_texcoord()
            elif self.triangle_texcoords == 2:
                self.save_tristrips_p = self.save_tristrips_p + self.tristrips_to_triangles_dual_texcoord()
        elif self.is_trifan:
            if self.triangle_texcoords == 0:
                self.save_trifans_p = self.save_trifans_p + self.trifans_to_triangles_no_texcoord()
            elif self.triangle_texcoords == 1:
                self.save_trifans_p = self.save_trifans_p + self.trifans_to_triangles_single_texcoord()


    def triangles_to_triangles_no_texcoord(self):
        """
            Method triangles_to_triangles_no_texcoord: For every line of input coordinates found in a <triangle> tag
            containing no 'semantic="TEXCOORD"' attribute in an <input> tag, convert the coordinate string to
            the OpenCOLLADA format:

            for each coordinate point in a string:

                <p> x(0) x(1) x(2)... x(n) </p>

            convert to:

                <p> x(0) x(0) x(1) x(1) x(2) x(2) ... x(n) x(n) </p>
        :return:
        """
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        for i in range(0, len(list(vertex))):
            new_vertex = str(vertex[i]) + " " + str(vertex[i])
            temp_line_2 = temp_line_2 + new_vertex + " "
        return temp_line_2

    def tristrips_to_triangles_no_texcoord(self):
        """
            Method tristrips_to_triangles_no_texcoord:
        :return:
        """
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        new_vertex = ""
        mod = len(list(vertex)) % 4
        totals = len(list(vertex))
        max_index = totals - mod - 1
        for i in range(0, max_index - 1, 2):
            new_vertex = self.concat_vertices(vertex[i], vertex[i]) + " " + \
                         self.concat_vertices(vertex[i + 1], vertex[i + 1]) + " " + \
                         self.concat_vertices(vertex[i + 2], vertex[i + 2]) + " " + \
                         self.concat_vertices(vertex[i + 2], vertex[i + 2]) + " " + \
                         self.concat_vertices(vertex[i + 1], vertex[i + 1]) + " " + \
                         self.concat_vertices(vertex[i + 3], vertex[i + 3]) + " "
            temp_line_2 = temp_line_2 + new_vertex

        if mod == 1:
            temp_line_2 = temp_line_2 + self.concat_mod(vertex, max_index, -1, 0, 1)

        if mod == 2:
            temp_line_2 = temp_line_2 + self.concat_mod(vertex, max_index, -1, 0, 1) + \
                           self.concat_mod(vertex, max_index, 1, 0, 2)

        if mod == 3:
            temp_line_2 = temp_line_2 + self.concat_mod(vertex, max_index, -1, 0, 1) + \
                          self.concat_mod(vertex, max_index, 1, 0, 2) + \
                          self.concat_mod(vertex, max_index, 1, 2, 3)
        return temp_line_2

    def triangles_to_triangles_single_texcoord(self):
        """
            Method triangles_to_triangles_single_texcoord: For every line of input coordinates found in a
            <triangle> tag containing one 'semantic="TEXCOORD"' attribute in an <input> tag, convert the
            coordinate string to the OpenCOLLADA format:

            For each pair of coordinate points in a string

                <p> x(0) x(1) x(2) x(3) x(4) ... x(n) </p>

            the ordered pair x(a) x(a+1) converts to x(a) x(a) x(a+1) using an increment of 2 for each iteration
            through the list of numbers found within the <p> ... </p> tags.

            Thus, the line above converts to
                <p> x(0) x(0) x(1) x(2) x(2) x(3) x(4) x(4) x(5) ... x(n-1) x(n-1) x(n) </p>

        :return:
        """
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        for i in range(0, len(list(vertex)), 2):
            new_vertex = str(vertex[i]) + " " + str(vertex[i]) + " " + str(vertex[i + 1])
            temp_line_2 = temp_line_2 + new_vertex + " "
        return temp_line_2

    def tristrips_to_triangles_single_texcoord(self):
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        for i in range(0, len(list(vertex)) - 1, 4):
            if (i + 6) <= len(list(vertex)):
                new_vertex = str(vertex[i]) + " " + str(vertex[i]) + " " + str(vertex[i + 1]) + " " + \
                             str(vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 3]) + " " + \
                             str(vertex[i + 4]) + " " + str(vertex[i + 4]) + " " + str(vertex[i + 5])
                temp_line_2 = temp_line_2 + new_vertex + " "
            if (i + 8) <= len(list(vertex)):
                new_vertex = str(vertex[i + 4]) + " " + str(vertex[i + 4]) + " " + str(vertex[i + 5]) + " " + \
                             str(vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 3]) + " " + \
                             str(vertex[i + 6]) + " " + str(vertex[i + 6]) + " " + str(vertex[i + 7])
                temp_line_2 = temp_line_2 + new_vertex + " "
        return temp_line_2

    def tristrips_to_triangles_dual_texcoord(self):
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]

        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        new_vertex = ""
        for i in range(0, len(list(vertex)) - 6, 6):
            new_vertex = str(vertex[i]) + " " + str(vertex[i])
            if len(list(vertex)) > (i + 1):
                new_vertex = new_vertex + " " + str(vertex[i + 1])
            if len(list(vertex)) > (i + 2):
                new_vertex = new_vertex + " " + str(vertex[i + 2])
            if len(list(vertex)) > (i + 3):
                new_vertex = new_vertex + " " + str(vertex[i + 3]) + " " + str(vertex[i + 3])
            if len(list(vertex)) > (i + 4):
                new_vertex = new_vertex + " " + str(vertex[i + 4])
            if len(list(vertex)) > (i + 5):
                new_vertex = new_vertex + " " + str(vertex[i + 5])
            if len(list(vertex)) > (i + 6):
                new_vertex = new_vertex + " " + str(vertex[i + 6]) + " " + str(vertex[i + 6])
            if len(list(vertex)) > (i + 7):
                new_vertex = new_vertex + " " + str(vertex[i + 7])
            if len(list(vertex)) > (i + 8):
                new_vertex = new_vertex + " " + str(vertex[i + 8]) + " " + str(vertex[i + 6]) + " " + \
                str(vertex[i + 6]) + " " + str(vertex[i + 7]) + " " + str(vertex[i + 8])
            if len(list(vertex)) > (i + 9):
                new_vertex = new_vertex + " " + str(vertex[i + 3]) + " " + str(vertex[i + 3]) + " " + \
                    str(vertex[i + 4]) + " " + str(vertex[i + 5]) + " " + str(vertex[i + 9]) + \
                    " " + str(vertex[i + 9]) + " " + str(vertex[i + 10]) + " " + str(vertex[i + 11])
            temp_line_2 = temp_line_2 + new_vertex + " "

        return temp_line_2

    def trifans_to_triangles_no_texcoord(self):
        """
            Method trifans_to_triangles_no_texcoord: For every line of input coordinates found in a <trifans> tag
            containing no 'semantic="TEXCOORD"' attribute in an <input> tag, convert the coordinate string to
            the OpenCOLLADA format:

            For the string
                <p> x(0) x(1) x(2) x(3) ... x(n) </p>

            convert any given subset  x(m) x(m+1) to:
                x(0) x(0) x(m) x(m) x(m+1) x(m+1)
        :return:
        """
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        for i in range(1, len(list(vertex)) - 1):
            new_vertex = str(vertex[0]) + " " + str(vertex[0]) + " " + \
                         str(vertex[i]) + " " + str(vertex[i]) + " " + \
                         str(vertex[i + 1]) + " " + str(vertex[i + 1]) + " "
            temp_line_2 += new_vertex
        return temp_line_2

    def trifans_to_triangles_single_texcoord(self):
        """
            Method trifans_to_triangles_single_texcoord: For every line of input coordinates found in a
            <trifans> tag containing one 'semantic="TEXCOORD"' attribute in an <input> tag, convert the
            coordinate string to the OpenCOLLADA format:

            For the points in a coordinate string
                <p> x(0) x(1) x(2) x(3) x(4) x(5) ... x(n) </p>
            convert any given sequence of points x(m) x(m+1) x(m+2) x(m +3) to
                x(0) x(0) x(1) x(1) x(m) x(m) x(m+1) x(m+1) x(m+2) x(m+2) x(m+3)
        :return:
        """
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        for i in range(2, len(list(vertex)) - 3, 2):
            new_vertex = str(vertex[0]) + " " + str(vertex[0]) + " " + \
                         str(vertex[1]) + " " + \
                         str(vertex[i]) + " " + str(vertex[i]) + " " +  \
                         str(vertex[i + 1]) + " " + \
                         str(vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + \
                         str(vertex[i + 3]) + " "
            temp_line_2 += new_vertex
        return temp_line_2

    def concat_mod(self, vertex, max_index, i1, i2, i3):
        """
            Method concat_mod:
        :param vertex:
        :param max_index:
        :param i1:
        :param i2:
        :param i3:
        :return:
        """
        return self.concat_vertices(vertex[max_index + i1], vertex[max_index + i1]) + " " + \
               self.concat_vertices(vertex[max_index + i2], vertex[max_index + i2]) + " " + \
               self.concat_vertices(vertex[max_index + i3], vertex[max_index + i3]) + " "

    def concat_vertices(self, vertex1, vertex2):
        """
            Method concat_vertices:
        :param vertex1:
        :param vertex2:
        :return:
        """
        return str(vertex1) + " " + str(vertex2)

    def pad_string(self):
        """
            Method pad_string: When an input line contains a number of blank characters, return a string
            of blank characters to pad an edited line that is to be written to the output file
        :return: A substring of blanks
        """
        return self.line[0:self.line.find('<')]

    def modify_count(self):

        temp_int_1 = len(list(map(int, self.save_triangles_p.split()))) + \
                     len(list(map(int, self.save_tristrips_p.split()))) + \
                     len(list(map(int, self.save_trifans_p.split())))
        temp_int_2 = 1
        if self.triangle_texcoords == 0:
            temp_int_2 = math.floor(temp_int_1 / 6)
        elif self.triangle_texcoords == 1:
            temp_int_2 = math.floor(temp_int_1 / 9)
        elif self.triangle_texcoords == 2:
            if self.is_tristrip:
                temp_int_2 = math.floor(temp_int_1 / 12)
        temp_str = str(temp_int_2)
        begin_index = self.save_triangle.find('count="') + 7
        end_index = self.save_triangle.find(' material="') - 1
        self.save_triangle = self.save_triangle[0:begin_index] + temp_str + self.save_triangle[end_index:]

    def write_triangles(self, outfile):
        """
            Function write_triangles: Write the output <triangles ... > tag and children tags when the closing tag
            is found.
        :param outfile:
        :return:
        """
        if len(self.save_triangle) != 0:
            outfile.write(self.save_triangle)
            if self.save_vertex != "":
                outfile.write(self.save_vertex)
            if self.save_normal != "":
                outfile.write(self.save_normal)
            if self.save_texcoord_1 != "":
                outfile.write(self.save_texcoord_1)
            if self.save_texcoord_2 != "":
                outfile.write(self.save_texcoord_2)
            outfile.write(self.pad_string() +
                          "     <p>" +
                          self.save_tristrips_p +
                          self.save_trifans_p +
                          self.save_triangles_p +
                          "</p>\n")
            outfile.write(self.pad_string() + "</triangles>\n")

    def reset_all(self):
        """
            Method reset_all: Once a <triangles>, <tristrips> or <trifans> tag has been fully reformatted and
            written to the output file, reset all saved data to default.
        :return:
        """
        self.save_triangle = ""
        self.tristrip_count = 0
        self.trifan_count = 0
        self.triangle_count = 0
        self.save_vertex = ""
        self.save_normal = ""
        self.save_uv = ""
        self.save_texcoord_1 = ""
        self.save_texcoord_2 = ""
        self.save_offset = 0
        self.save_tristrips_p = ""
        self.save_trifans_p = ""
        self.save_triangles_p = ""
        self.triangle_texcoords = 0
        self.is_triangle = False
        self.is_tristrip = False
        self.is_trifan = False


def update_file(fileName):
    """
   This is the main function that reads every line in the file and calls various functions based on the tags. It runs
   the algorithm on the original imported file to create a temporary file, which is then imported into blender.
   The temporary file is deleted after successful import. The temporary file name takes the process id from the
   operating system in order to get a unique file name.
   Parameters:
       fileName: the original file name with path for the imported DAE file
   Returns:
       new_file_name: The new file name with path for the modified temporary updated file.
   """

    # Clear the Blender system console
    os.system("cls")

    # Set the directory path to the input COLLADA file, open for reading
    filedir = os.path.dirname(fileName)
    infile = open(fileName, 'r')
    print("fileName :", fileName)

    # Read the input file into the content object
    content = infile.readlines()
    new_file_name = filedir + '/temp_' + str(os.getpid()) + '.dae'
    print("new_file_name: ", new_file_name)
    outfile = open(new_file_name, 'w')
    # Initialize variables

    # Create xml object from Tagline class, use to retain data while processing input COLLADA file
    xml = Tagline()

    # Loop through each line of the import file
    for line_in in content:

        # Store the unedited line_in in the xml object
        xml.store_line(line_in)

        # Find the input string "<unit": Substitute inches for millimeters.
        # Note: This substitution is global for wherever the unit tag is found.
        if find_string("<unit ", xml.line):
            xml.new_line = xml.pad_string() + '<unit name="inch" meter="0.0254"/>\n'
            outfile.write(xml.new_line)
            continue

        # Find the input string "<translate>": convert values from metric (millimeters) to English (inches)
        # Note: This conversion is global for wherever the translate tag is found.
        if find_string("<translate>", xml.line):
            xml.new_line = xml.scale_metric()
            outfile.write(xml.new_line)  # Scale down translate values by a factor of 25.4
            continue

        # Find the input string "<asset>": Set xml.inside_asset to TRUE
        if find_string("<asset>", xml.line):
            xml.inside_asset = write_to_outfile(xml, outfile, True)
            continue

        # Find the input string "</asset>": Set xml.inside_asset to FALSE
        if find_string("</asset>", xml.line):
            xml.inside_asset = write_to_outfile(xml, outfile, False)
            continue

        # Find the input string "<library_visual_scenes>": Set xml.inside_library_visual_scenes to TRUE
        if find_string("<library_visual_scenes>", xml.line):
            xml.inside_library_visual_scenes = write_to_outfile(xml, outfile, True)
            continue

        # Print any unprocessed line inside library_visual_scenes to outfile.
        if xml.inside_library_visual_scenes:
            outfile.write(xml.line)

            # Close out tag when </library_visual_scenes> is found.
            if find_string("</library_visual_scenes>", xml.line):
                xml.inside_library_visual_scenes = False

            continue

        # Find the input string "<library_nodes ": Set xml.inside_library_nodes to TRUE
        if find_string("<library_nodes ", xml.line):
            xml.inside_library_nodes = write_to_outfile(xml, outfile, True)
            continue

        # Find any unprocessed line with in library_nodes: write to outfile.
        if xml.inside_library_nodes:
            outfile.write(xml.line)
            # Find the input string "</library_nodes ": Set xml.inside_library_nodes to FALSE, exit tag.
            if find_string("</library_nodes>", xml.line):
                xml.inside_library_nodes = False
            continue

        # Find the input string "<library_geometries ": Save library attributes
        if find_string("<library_geometries ", xml.line):
            xml.extract_geometry_library_name()
            xml.inside_library_geometries = write_to_outfile(xml, outfile, True)
            continue

        # Boolean xml.inside_library_geometries is TRUE: Process contents of <library_geometries> tag.
        if xml.inside_library_geometries:

            # Find the input string "<geometry ": Set xml.inside_geometry to TRUE
            if find_string("<geometry ", xml.line):
                xml.inside_geometry = write_to_outfile(xml, outfile, True)
                continue

            if xml.inside_geometry:

                # Find the input string "<mesh>": Set xml.inside_mesh to TRUE
                if find_string("<mesh>", xml.line):
                    if xml.inside_geometry:
                        xml.inside_mesh = write_to_outfile(xml, outfile, True)
                        continue

                # Process tags inside mesh
                if xml.inside_mesh:

                    # Find the input string "<source ": Set xml.inside_source to TRUE, delete name attributes.
                    if find_string("<source ", xml.line):
                        if xml.inside_mesh:
                            xml.inside_source = True
                            process_source(xml, outfile)
                            continue

                    if xml.inside_source:

                        if not xml.is_uvparams:

                            # Find the input string "<float_array": delete "digits" and "magnitude" attributes,
                            # convert float array values from metric to English
                            if find_string("<float_array ", xml.line):
                                process_float_array(xml, outfile)
                                continue

                            if find_string("<technique_common>", xml.line):
                                xml.inside_technique = write_to_outfile(xml, outfile, True)
                                continue

                            if xml.inside_technique:
                                outfile.write(xml.line)
                                if find_string("</technique_common>", xml.line):
                                    xml.inside_technique = False

                        # Find the input string "</source>": Close out the source tag.
                        if find_string("</source>", xml.line):
                            xml.inside_source = False

                            if xml.is_uvparams:
                                xml.is_uvparams = False
                            else:
                                outfile.write(xml.line)

                    # Find the input string "<vertices ": write the line to the output file.
                    if find_string("<vertices ", xml.line):
                        if xml.inside_mesh:
                            xml.inside_vertices = write_to_outfile(xml, outfile, True)
                        continue

                    if xml.inside_vertices:
                        outfile.write(xml.line)
                        if find_string("</vertices>", xml.line):
                            xml.inside_vertices = False
                        continue

                    # Find the input string "<triangles ": process the triangle object.
                    if find_string("<tristrips ", xml.line) \
                            or find_string("<trifans ", xml.line) \
                            or find_string("<triangles ", xml.line):
                        process_triangle(xml)
                        continue

                    if xml.inside_triangles:

                        if find_string("<input ", xml.line):
                            xml.save_input_tag()
                            continue

                        if find_string("<p>", xml.line):
                            xml.save_points()
                            continue

                        if find_string("</triangles>", xml.line) \
                                or find_string("</tristrips>",  xml.line) \
                                or find_string("</trifans>", xml.line):
                            process_close_triangle(xml)
                            continue

                    # Find the input string "</mesh>": Close out the mesh tag. Update the tristrips/trifans/triangles
                    # found in the current mesh, write to file.
                    if find_string("</mesh>", xml.line):
                        process_close_mesh(xml, outfile)
                        continue

                if find_string("</geometry>", xml.line):
                    xml.inside_geometry = write_to_outfile(xml, outfile, False)
                    continue

            # Find the input string "</library_geometries>": Close out library_geometries tag.
            if find_string('</library_geometries>', xml.line):
                xml.inside_library_geometries = write_to_outfile(xml, outfile, False)
                continue

    # TEMPORARY: Send any line outside the library_geometries tag to outfile. REMOVE when required.
        if not xml.inside_library_geometries:
            outfile.write(xml.line)
            continue

    infile.close()
    outfile.close()
    return new_file_name

# End of main routine: Begin main support functions.


def process_source(xml, outfile):
    """
    Function process_source: When a <source ... > tag is found, test for 'name = "vertices"',
    'name="normals"', 'name="texcoords"', or 'name="uvparams"' attributes. Modify the output to remove
    the attributes and write the updated tag to outfile. If 'name="uvparams"' attribute is found, set a
    flag and do not process the line. Further processin on uvparams will occur later.
    :param xml:
    :param outfile:
    :return:
    """
    if find_string(' name="vertices"', xml.line):
        xml.new_line = xml.line.replace(' name="vertices"', "")
        xml.is_vertex = True
        outfile.write(xml.new_line)

    if find_string(' name="normals"', xml.line):
        xml.new_line = xml.line.replace(' name="normals"', "")
        outfile.write(xml.new_line)

    if find_string(' name="texcoords"', xml.line):
        xml.new_line = xml.line.replace(' name="texcoords"', "")
        outfile.write(xml.new_line)

    if find_string(' name="uvparams"', xml.line):
        xml.is_uvparams = True


def process_float_array(xml, outfile):
    #  If count = 0 is found, then account for the missing </float_array> tag
    if find_string(' count="0"', xml.line):
        xml.new_line = xml.fix_zero_count_param()
        outfile.write(xml.new_line)
    else:
        xml.new_line = xml.reformat_float_array_tag()
        outfile.write(xml.new_line)


def process_triangle(xml):
    if xml.inside_mesh:
        xml.inside_triangles = True
        xml.save_triangle_tag()


def process_close_triangle(xml):
    xml.inside_triangles = False
    xml.is_triangle = False
    xml.is_tristrip = False
    xml.is_trifan = False
    xml.triangle_texcoords = 0


def process_close_mesh(xml, outfile):
    """
    Function process_close_mesh: When a "</mesh> tag is found, process the data for all triangles, tristrips, and
    trifans found within the <mesh> tag.
    :param xml:
    :param outfile:
    :return:
    """
    xml.inside_mesh = False
    xml.inside_triangles = False
    xml.modify_count()
    if xml.triangle_count + xml.tristrip_count + xml.trifan_count != 0:
        xml.write_triangles(outfile)
    xml.reset_all()
    outfile.write(xml.line)


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

def write_to_outfile(xml, outfile, state):
    """
    Function write_to_outfile: write the current tag line to outfile without any further editing,
    return the input state to the calling function.
    :param xml:
    :param outfile:
    :param state:
    :return:
    """
    outfile.write(xml.line)
    return state

