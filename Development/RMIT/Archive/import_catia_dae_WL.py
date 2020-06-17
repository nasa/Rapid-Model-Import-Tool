"""
Author: Arjun Ayyangar (Summer NIFS KSC Intern)
Date: 7/26/2018

09/06/18: Began updates, modularization to existing code. Implemented
function setLineTemp to modify line_in to conform to OpenCOLLADA standard.
Author: William Little
"""
import bpy
import fileinput
import math
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
import os
from math import radians
from mathutils import Matrix

bl_info = {
    "name": "Import Collada from CATIA 10/31/2018",
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

    def reformat_float_array_tag(self):
        """
            Method reformat_float_array_tag: If attributes ""magnitude" and/or "digits" are found in a float_array
            tag, remove them, save the updated string in self.new_line
        :return:
        """
        # print("reformat_float_array_tag")
        # print("self.line: ", self.line[0:100])
        if self.is_vertex:
            temp_line = self.scale_metric()
            self.is_vertex = False
        else:
            temp_line = self.line
        # print("temp_line(1): ", temp_line[0:100])
        if find_string('magnitude="', temp_line):
            temp_start = temp_line.find('magnitude="')
            temp_end = temp_line.find('>')
            temp_line = temp_line[0:temp_start] + temp_line[temp_end:]

        if find_string('digits="', temp_line):
            temp_start = temp_line.find('digits="')
            temp_end = temp_line.find('>')
            temp_line = temp_line[0:temp_start] + temp_line[temp_end:]

        # print("temp_line(2): ", temp_line[0:100])
        return temp_line

    def scale_metric(self):
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
        # print("save_triangle_tag: line: ", self.line)

        if find_string("<tristrips ", self.line):
            self.save_triangle = self.line.replace("<tristrips ", "<triangles ")
            self.is_tristrip = True
            self.tristrip_count = 0
            return

        if find_string("<trifans ", self.line):
            self.save_triangle = self.line.replace("<trifans ", "<triangles ")
            self.is_trifan = True
            self.trifan_count = 0
            return

        if find_string("<triangles ", self.line):
            self.save_triangle = self.line
            self.is_triangle = True
            self.triangle_count = 0
            return

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
            # self.save_uv = self.line
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
        # print("self.save_offset: ", self.save_offset, " self.triangle_texcoords: ", self.triangle_texcoords)
        temp_int = self.save_offset + self.triangle_texcoords
        temp_char = str(temp_int)
        # print("temp_int: ", temp_int, " temp_char: ", temp_char)
        begin_index = temp_line.find('"')
        end_index = begin_index + 2
        temp_line = temp_line[:begin_index + 1] + temp_char + temp_line[end_index:]
        # if find_string(' set="0"', temp_line):
        #     temp_line = temp_line.replace(' set="0"', "")
        # if find_string(' set="1"', temp_line):
        #     temp_line = temp_line.replace(' set="1"', "")
        # print("temp_line: ", temp_line)
        return temp_line

    def save_points(self):
        # begin_index = self.line.find(">") + 1
        # end_index = self.line.find("</") - 1
        # temp_p = self.line[begin_index:end_index]
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
        # print("self.triangle_to_triangle_no_texcoord(self): ", self.line)
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
        # print("self.tristrips_to_triangles_no_texcoord(self): ", self.line)
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        new_vertex = ""
        mod = len(list(vertex)) % 4
        # print("mod: ", mod)
        totals = len(list(vertex))
        # print("totals: ", totals)
        max_index = totals - mod - 1
        # print("max_index: ", max_index)
        # for i in range(0, len(list(vertex)) - 6, 6):
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
            temp_line_2 =  temp_line_2 + self.concat_mod(vertex, max_index, -1, 0, 1) + \
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
        # print("self.triangle_to_triangle_single_texcoord(self): ", self.line)
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
        # print("tristrips_to_triangles_single_texcoord: ")
        # print("line: ", self.line)
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        # print("len(list(vertex)): ", len(list(vertex)))
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
        # print("temp_line_2: ", temp_line_2)
        return temp_line_2

    def tristrips_to_triangles_dual_texcoord(self):
        # print("tristrips_to_triangles_dual_texcoord: ")
        # print("line: ", self.line)
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]

        vertex = [int(x) for x in temp_line_1.split()]
        temp_line_2 = ""
        # print("len(list(vertex)): ", len(list(vertex)))
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

        # print("temp_line_2: ", temp_line_2)
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
        # print("trifans_to_triangles_single_texcoord: ")
        # print("self.line: ", self.line)
        begin_index = self.line.find(">") + 1
        end_index = self.line.find("</")  # - 1
        temp_line_1 = self.line[begin_index:end_index]
        vertex = [int(x) for x in temp_line_1.split()]
        # print("len(list(vertex)): ", len(list(vertex)))
        temp_line_2 = ""
        for i in range(2, len(list(vertex)) - 3, 2):
            new_vertex = str(vertex[0]) + " " + str(vertex[0]) + " " + \
                         str(vertex[1]) + " " + \
                         str(vertex[i]) + " " + str(vertex[i]) + " " +  \
                         str(vertex[i + 1]) + " " + \
                         str(vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + \
                         str(vertex[i + 3]) + " "
            temp_line_2 += new_vertex
        # print("temp_line_2: ", temp_line_2)
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
        # print("1. modify_count: self.save_triangle: ", self.save_triangle)
        # print("self.is_triangle: ", self.is_triangle, " .is_tristrip: ", self.is_tristrip, " .is_trifan: ", self.is_trifan)
        # print("self.triangle_texcoords: ", self.triangle_texcoords)
        # print("self.save_texcoord_1: ", self.save_texcoord_1, " .save_texcoord_2: ", self.save_texcoord_2)
        # print("modify_count: self.save_p: ", self.save_p)

        # NOTE: Rethink this line. Is this the correct way of determining what the final count of
        # vertices that will go into the count attribute of the triangle set?
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
        # print("modify_count: temp_int_1: ", temp_int_1, " temp_int_2: ", temp_int_2, " temp_str: ", temp_str)
        begin_index = self.save_triangle.find('count="') + 7
        end_index = self.save_triangle.find(' material="') - 1
        self.save_triangle = self.save_triangle[0:begin_index] + temp_str + self.save_triangle[end_index:]
        # print("2. modify_count: self.save_triangle: ", self.save_triangle)

    def write_triangles(self, outfile):
        """
            Function write_triangles: Write the output <triangles ... > tag and children tags when the closing tag
            is found.
        :param outfile:
        :return:
        """
        outfile.write(self.save_triangle)
        if self.save_vertex != "":
            outfile.write(self.save_vertex)
        if self.save_normal != "":
            outfile.write(self.save_normal)
        # if self.save_uv != "":
            # outfile.write(self.save_uv)
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

    # Loop through each line of the import file
    for line_in in content:

        # Store the unedited line_in in the xml object
        xml.store_line(line_in)
        # print("xml.line(0): ", xml.line)

        # Find the input string "<unit": Substitute inches for millimeters.
        # Note: This substitution is global for wherever the unit tag is found.
        if find_string("<unit ", xml.line):
            xml.new_line = xml.pad_string() + '<unit name="inch" meter="0.0254"/>\n'
            outfile.write(xml.new_line)
            # print("xml.new_line(1): ", xml.new_line)
            continue

        # Find the input string "<translate>": convert values from metric (millimeters) to English (inches)
        # Note: This conversion is global for wherever the translate tag is found.
        if find_string("<translate>", xml.line):
            xml.new_line = xml.scale_metric()
            outfile.write(xml.new_line)  # Scale down translate values by a factor of 25.4
            continue

        # Find the input string "<asset>": Set xml.inside_asset to TRUE
        if find_string("<asset>", xml.line):
            outfile.write(xml.line)
            xml.inside_asset = True
            # print("xml.line(3): ", xml.line)
            continue

        # Find the input string "</asset>": Set xml.inside_asset to FALSE
        if find_string("</asset>", xml.line):
            outfile.write(xml.line)
            xml.inside_asset = False
            # print("xml.line(4): ", xml.line)
            continue

        # Find the input string "<library_visual_scenes>": Set xml.inside_library_visual_scenes to TRUE
        if find_string("<library_visual_scenes>", xml.line):
            xml.inside_library_visual_scenes = True
            outfile.write(xml.line)
            # print("xml.line(5): ", xml.line)
            continue

        # Print any unprocessed line inside library_visual_scenes to outfile.
        if xml.inside_library_visual_scenes:
            outfile.write(xml.line)

            # Close out tag when </library_visual_scenes> is found.
            if find_string("</library_visual_scenes>", xml.line):
                # print("xml.line(6A): ", xml.line)
                xml.inside_library_visual_scenes = False

            # print("xml.line(6): ", xml.line)
            continue

        # Find the input string "<library_nodes ": Set xml.inside_library_nodes to TRUE
        if find_string("<library_nodes ", xml.line):
            xml.inside_library_nodes = True
            outfile.write(line_in)
            # print("xml.line(8): ", xml.line)
            continue

        # Find any unprocessed line with in library_nodes: write to outfile.
        if xml.inside_library_nodes:
            outfile.write(xml.line)
            # print("xml.line(9): ", xml.line)
            # Find the input string "</library_nodes ": Set xml.inside_library_nodes to FALSE, exit tag.
            if find_string("</library_nodes>", xml.line):
                xml.inside_library_nodes = False
                # print("xml.line(9A): ", xml.line)
            continue

        # Find the input string "<library_geometries ": Save library attributes
        if find_string("<library_geometries ", xml.line):
            xml.extract_geometry_library_name()
            xml.inside_library_geometries = True
            outfile.write(xml.line)
            # print("xml.line(11): ", xml.line)
            continue

        # Boolean xml.inside_library_geometries is TRUE: Process contents of <library_geometries> tag.
        if xml.inside_library_geometries:

            # Find the input string "<geometry ": Set xml.inside_geometry to TRUE
            if find_string("<geometry ", xml.line):
                xml.inside_geometry = True
                outfile.write(xml.line)
                # print("xml.line(12): ", xml.line)
                continue

            if xml.inside_geometry:

                # Find the input string "<mesh>": Set xml.inside_mesh to TRUE
                if find_string("<mesh>", xml.line):
                    if xml.inside_geometry:
                        xml.inside_mesh = True
                        outfile.write(xml.line)
                        # print("xml.line(13): ", xml.line)
                        continue

                # Process tags inside mesh
                if xml.inside_mesh:

                    # Find the input string "<source ": Set xml.inside_source to TRUE, delete name attributes.
                    if find_string("<source ", xml.line):
                        if xml.inside_mesh:
                            xml.inside_source = True

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
                                continue

                    if xml.inside_source:

                        if not xml.is_uvparams:

                            # Find the input string "<float_array": delete "digits" and "magnitude" attributes,
                            # convert float array values from metric to English
                            if find_string("<float_array ", xml.line):
                                #  If count = 0 is found, then account for the missing </float_array> tag
                                if find_string(' count="0"', xml.line):
                                    xml.new_line = fixZeroCountParam(xml.line)
                                    outfile.write(xml.new_line)
                                else:
                                    xml.new_line = xml.reformat_float_array_tag()
                                    outfile.write(xml.new_line)

                            if find_string("<technique_common>", xml.line):
                                xml.inside_technique = True
                                outfile.write(xml.line)
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
                            # print("xml.line(15): ", xml.line)

                    # Find the input string "<vertices ": write the line to the output file.
                    if find_string("<vertices ", xml.line):
                        if xml.inside_mesh:
                            xml.inside_vertices = True
                            outfile.write(xml.line)
                            # print("xml.line(16): ", xml.line)
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

                        if xml.inside_mesh:
                            xml.inside_triangles = True
                            xml.save_triangle_tag()
                            # print("xml.line(17): ", xml.line)
                        continue

                    if xml.inside_triangles:

                        if find_string("<input ", xml.line):
                            if xml.inside_triangles:
                                xml.save_input_tag()

                            continue

                        if find_string("<p>", xml.line):
                            xml.save_points()
                            continue

                        if find_string("</triangles>", xml.line) \
                                or find_string("</tristrips>",  xml.line) \
                                or find_string("</trifans>", xml.line):
                            xml.inside_triangles = False
                            xml.is_triangle = False
                            xml.is_tristrip = False
                            xml.is_trifan = False
                            xml.triangle_texcoords = 0
                            continue

                    # Find the input string "</mesh>": Close out the mesh tag. Update the tristrips/trifans/triangles
                    # found in the current mesh, write to file.
                    if find_string("</mesh>", xml.line):
                        xml.inside_mesh = False
                        xml.inside_triangles = False
                        xml.modify_count()
                        xml.write_triangles(outfile)
                        xml.reset_all()
                        outfile.write(xml.line)
                        # print("xml.line(13A): ", xml.line)
                        continue

                if find_string("</geometry>", xml.line):
                    xml.inside_geometry = False
                    outfile.write(xml.line)
                    continue

            # Find the input string "</library_geometries>": Close out library_geometries tag.
            if find_string('</library_geometries>', xml.line):
                outfile.write(xml.line)
                xml.inside_library_geometries = False
                # print("xml.line: ", xml.line)
                continue

    # TEMPORARY: Send any line outside the library_geometries tag to outfile. REMOVE when required.
        if not xml.inside_library_geometries:
            print(xml.line)
            outfile.write(xml.line)
            continue

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
    return temp_out[0:temp_start] + 'count="0"/>\n'


""" 10/18/2018: This function is no longer being used. 
def remove_float_array_attributes(line_in):

    # print("remove_float_array_attributes:")
    tmpOut = line_in
    # Scale down float array values if magnitude is not 1
    # if line_in.find('magnitude="1"') == -1:
    # 10/10/18: Modify logic to accept all magnitudes
    if not find_string('magnitude="1"', line_in):
        #  if find_string("magnitude=", line_in):
        tmpOut = scale_down(line_in)
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
"""

# def process_mesh(line_texcoord1, line_texcoord2, line_out, line_orig_out, foundTriangles,
#                 foundTristrips, foundTrifans, line_vertex, line_normal, line_triangle, outfile):
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
"""

# def modify_semantic_TEXCOORD(strOut):
"""
    Function modify_semantic_TEXCOORD: modify the output string str_temp to the requisite
    Open COLLADA format and return the result.
    :param strOut:
    :return:
"""
"""
    str_temp = strOut.replace(' set="0"', "")
    str_temp = strOut.replace('<input offset="2" semantic="TEXCOORD"', '<input offset="3" semantic="TEXCOORD"')
    return str_temp.replace('<input offset="1" semantic="TEXCOORD"', '<input offset="2" semantic="TEXCOORD"')
"""

# def convertSingleTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in):
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


"""
    if (insideTriangles):
        return (triangleToTriangleSingleTEXCOORD(line_in))
    if (insideTristrips):
        return (tristripsToTriangleSingleTEXCOORD(line_in))
    if (insideTrifans):
        return (trifansToTriangleSingleTEXCOORD(line_in))
    return (line_in)
"""


#def triangleToTriangleSingleTEXCOORD(line_in):
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
"""
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(0, len(list(vertex)), 2):
        newVertex = str(vertex[i]) + " " + str(vertex[i]) + " " + str(vertex[i + 1])
        line_out = line_out + newVertex + " "
    return line_out.strip()
"""

# def trifansToTriangleSingleTEXCOORD(line_in):
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
"""

# def tristripsToTriangleSingleTEXCOORD(line_in):
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
        if (i + 8) <= len(list(vertex)):
            newVertex = str(vertex[i + 4]) + " " + str(vertex[i + 4]) + " " + str(vertex[i + 5]) + " " + str(
                vertex[i + 2]) + " " + str(vertex[i + 2]) + " " + str(vertex[i + 3]) + " " + str(
                vertex[i + 6]) + " " + str(vertex[i + 6]) + " " + str(vertex[i + 7])
            line_out = line_out + newVertex + " "
    return line_out.strip()
"""

# def scale_down(line_in):
"""
     The function takes an input string that extracts the numbers between > and </.
     Returns an output string with the numbers scaled down by 25.4 (convert millimeters to inches)
     along with its appropriate tags
     Parameters:
        line_in: the input string from one line of the file
     Returns:
         line_out: the output string
"""
"""
    begin_index = line_in.find('>') + 1
    end_index = line_in.find('</') - 1
    line_tmp = line_in[begin_index:end_index]
    # print("line_in: ", line_in[0:endNum)
    try:
        vertex = [float(x) for x in line_tmp.split()]
    except ValueError:
        # WARNING: the following code is a kluge to keep the creation of the vertex list from failing.
        # It deletes the last character found, which is a "-" when it should be a 1, then continues on and appends
        # a -1 to vertex.
        print("Non-numeric data found in file")
        t_line = line_tmp[0:len(line_tmp) - 1]
        vertex = [float(x) for x in t_line.split()]
        if find_string("-1</", line_in):
            vertex.append(-1)
        print("len(list(vertex)): ", len(list(vertex)))

    line_out = line_in[0:begin_index]
    for i in range(0, len(list(vertex))):
        vertex[i] /= 25.4
        str_vertex = str(vertex[i])
        line_out = line_out + str_vertex[:str_vertex.find(".") + 6] + " "
    if find_string(" -1</", line_in):
        line_out = line_out + "-1"
    line_out = line_out + line_in[end_index:]
    return line_out
"""

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

# def convertNoTEXCOORD(insideTriangles, insideTristrips, insideTrifans, line_in):
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
"""
    if (insideTriangles):
        return (triangleToTriangleNoTEXCOORD(line_in))
    if (insideTristrips):
        return (tristripsToTriangleNoTEXCOORD(line_in))
    if (insideTrifans):
        return (trifansToTriangleNoTEXCOORD(line_in))
    return (line_in)
"""

# def triangleToTriangleNoTEXCOORD(line_in):
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
"""
    line_tmp = setLineTemp(line_in, "<p>", "</p>")
    vertex = [int(x) for x in line_tmp.split()]
    line_out = ""
    for i in range(0, len(list(vertex))):
        newVertex = str(vertex[i]) + " " + str(vertex[i])
        line_out = line_out + newVertex + " "
    return line_out  # .strip()
"""

# def tristripsToTriangleNoTEXCOORD(line_in):
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
"""

# def concat_mod(vertex, max_index, i1, i2, i3):
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
"""
    return concat_vertices(vertex[max_index + i1], vertex[max_index + i1]) + " " + \
           concat_vertices(vertex[max_index + i2], vertex[max_index + i2]) + " " + \
           concat_vertices(vertex[max_index + i3], vertex[max_index + i3]) + " "
"""

# def concat_vertices(vertex1, vertex2):
"""
    Function concat_vertices: Concatenate two input vertices separated by a blank character
    and return the resulting string.
    :param vertex1:
    :param vertex2:
    :return:
"""
#    return str(vertex1) + " " + str(vertex2)


# def trifansToTriangleNoTEXCOORD(line_in):
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
"""

# def tristripsToTriangleDoubleTEXCOORD(line_in):
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
"""

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


"""
        
        # Find the input string "<tristrips ": process the tristrip object, convert it to triangle.
        if find_string("<tristrips ", xml.line):
            if xml.inside_mesh:
                xml.inside_tristrips = True
                xml.new_line = xml.line.replace("tristrips", "triangles")
                outfile.write(xml.new_line)
                xml.line_out = ""
                # print("xml.new_line(19): ", xml.new_line)
                continue

        if xml.inside_tristrips:
            if find_string(' semantic="TEXCOORD"', xml.line):
                xml.new_line = xml.line
                xml.tristrip_texcoords += 1
                xml.new_line = xml.update_texcoord()
                outfile.write(xml.new_line)
                # print("xml.line: ", xml.line, "xml.tristrip_texcoords: ", xml.tristrip_texcoords)

            if find_string("<p>", xml.line):
                if xml.tristrip_texcoords == 0:
                    # outfile.write(xml.tristrips_to_triangles_no_texcoord())
                    xml.line_out += xml.tristrips_to_triangles_no_texcoord()
                # elif xml.tristrip_texcoords == 1:
                #     outfile.write(xml.tristrips_to_triangles_single_texcoord())
                continue

            if find_string("</tristrips>", xml.line):
                # print("xml.line_out: ", xml.line_out)
                xml.new_line = xml.pad_string() + "    <p>" + xml.line_out + "</p>\n"
                outfile.write(xml.new_line)
                outfile.write(xml.pad_string() + "</triangles>\n")
                xml.inside_tristrips = False
                xml.tristrip_texcoords = 0
                xml.line_out = ""
                # outfile.write(xml.new_line)
                # print("xml.new_line(20): ", xml.new_line)
            else:
                outfile.write(xml.line)
            continue

        # Find the input string "<trifans ": process the trifan object, convert it to triangle
        if find_string("<trifans ", xml.line):
            if xml.inside_mesh:
                xml.inside_trifans = True
                xml.new_line = xml.line
                xml.new_line = xml.new_line.replace("trifans", "triangles")
                outfile.write(xml.new_line)
                # print("xml.new_line(21): ", xml.new_line)
                continue

        if xml.inside_trifans:
            if find_string(' semantic="TEXCOORD"', xml.line):
                xml.trifan_texcoords += 1
                xml.update_texcoord()
                outfile.write(xml.new_line)
                # print("xml.line: ", xml.line, "xml.trifan_texcoords: ", xml.trifan_texcoords)
                continue

            if find_string("<p>", xml.line):
                if xml.trifan_texcoords == 0:
                    # outfile.write(xml.tristrips_to_triangles_no_texcoord())
                    xml.line_out += xml.trifans_to_triangles_no_texcoord()
                elif xml.tristrip_texcoords == 1:
                     outfile.write(xml.trifans_to_triangles_single_texcoord())
                continue

            if find_string("</trifans>", xml.line):
                xml.new_line = xml.pad_string() + "    <p>" + xml.line_out + "</p>\n"
                outfile.write(xml.new_line)
                outfile.write(xml.pad_string() + "</triangles>\n")
                xml.inside_trifans = False
                xml.trifan_texcoords = 0
                xml.line_out = ""
            else:
                outfile.write(xml.line)
            continue

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

        # If line is outside the mesh tags, write as is
        # 10/15/2018: Comment out this test. Move, substitute test for xml.inside_library_geometries.
        # if not (insideMesh):
        #     outfile.write(line_in)
        #     continue


        # Find the input string "</library_visual_scenes?": Close out the library_visual_scenes tag.
        if find_string("</library_visual_scenes>", xml.line):
            xml.inside_library_visual_scenes = False
            outfile.write(xml.line)
            print("xml.line(15): ", xml.line)
            continue
        """
