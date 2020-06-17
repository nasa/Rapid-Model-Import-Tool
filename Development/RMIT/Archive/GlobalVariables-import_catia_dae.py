# Initialize variables
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
