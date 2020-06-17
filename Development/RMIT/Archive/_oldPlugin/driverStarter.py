import bpy
import os
import sys

sys.path.append(os.getcwd() + '\\Utils')
from ArgParserUtil import argEval

if __name__ == '__main__' or __name__ == '<run_path>':
    #print(os.getcwd() + '\\Utils')
    importPath, exportPath, decRatio, cleanUpBool = argEval()
    bpy.ops.rmit.run(importPath=importPath, exportPath=exportPath decRatio=decRatio, cleanUp=cleanUpBool)