import sys       # to get command line args
import argparse  # to parse options for us and print a nice help message

class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, " ".join(values))

def argEval():
    """
    Get the args passed to blender after "--", all of which are ignored by
    blender so scripts may receive their own arguments

    Parameters
    ----------
    Parameters are provided via command line arguments:
    Input/Output str and decimate amount

    Returns
    -------
    Input and Output paths
        param1 (str): inputPath -i
        param2 (str): outputPath -e
        param3 (bool): decimate -d
        param4 (float): decimate amount -p
        param4 (bool): cleanup -c
        param5: (float): cleanup amount -l
        param6 (bool): delete hidden -h
        param7 (bool): flatten tree -r
        param8 (bool): merge -m
        param9 (bool): center -o
        param10 (bool): split -s

    """

    
    print(sys.argv)
    argv = sys.argv  # Gets command line arguments
    if "--" not in argv:
        argv = []    # As if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # Get all args after "--"

    # When --help or no args are given, print this help
    usage_text = \
        "Run blender in background mode with this script: D:/<User>/<blender path> \
        /blender.exe --background --python " + __file__ + " -- [options]" + str(sys.argv)
    parser = argparse.ArgumentParser(description=usage_text)

    # Get Import and Export Options
    parser.add_argument("-i", "--import", dest="import_path", metavar='FILE', action=CustomAction, nargs='+',
                        help="Import the file from a specified path")
    parser.add_argument("-e", "--export", dest="export_path", metavar='FILE', action=CustomAction, nargs='+',
                        help="Export the generated file to the specified path")
    parser.add_argument("-d", "--decimateperc", dest="decimation", metavar='N',
                        help="Decimation boolean")
    parser.add_argument("-p", "--decimate", dest="decimation_percent", metavar='N',
                        help="Percent to decimate")                        
    parser.add_argument("-c", "--clean", dest="clean", metavar='N',
                        help="CleanUp bool for small dense parts")
    parser.add_argument("-l", "--cleanperc", dest="clean_percentage", metavar='N',
                        help="Cleanup percentage")
    parser.add_argument("-x", "--hidden", dest="hidden", metavar='N',
                        help="delete hidden objects")
    parser.add_argument("-r", "--flatten", dest="flatten", metavar='N',
                        help="flattens the model tree")
    parser.add_argument("-m", "--merge", dest="merge", metavar='N',
                        help="merges into a single object")
    parser.add_argument("-o", "--center", dest="center", metavar='N',
                        help="Center object to origin")
    parser.add_argument("-s", "--split", dest="split", metavar='N',
                        help="Splits entire object")    
                                        

    args = parser.parse_args(argv)

    # These provide help and return when the command arguments aren't correct
    if not argv:
        parser.print_help()
        return

    if not args.import_path:
        print("Error: --import=\"input file path\" arg not given, aborting.")
        parser.print_help()
        return

    if not args.export_path:
        print("Error: --export=\"export file path\" arg not given, aborting.")
        parser.print_help()
        return

    print("Args parsed successfully")
    return(args.import_path, args.export_path,
            s2b(args.decimation),float(args.decimation_percent),
            s2b(args.clean),float(args.clean_percentage),s2b(args.hidden),
            s2b(args.flatten),s2b(args.merge),s2b(args.center),
            s2b(args.split))

def s2b(v):
  return v.lower() in ("true")

if __name__ == '<run_path>' or __name__ == '__main__':
    argEval()

