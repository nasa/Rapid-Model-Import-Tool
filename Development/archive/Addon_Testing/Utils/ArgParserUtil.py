import sys       # to get command line args
import argparse  # to parse options for us and print a nice help message


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
        param1 (str): inputPath
        param2 (str): outputPath
        param3 (float): decimateAmount
        param4 (bool):

    """
    argv = sys.argv  # Gets command line arguments
    if "--" not in argv:
        argv = []  # As if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # Get all args after "--"

    # When --help or no args are given, print this help
    usage_text = \
        "Run blender in background mode with this script: D:\Jose\\blender-2.80 \
        \\blender --background --python " + __file__ + " -- [options]"
    parser = argparse.ArgumentParser(description=usage_text)

    # Get Import and Export Options
    parser.add_argument("-i", "--import", dest="import_path", metavar='FILE',
                        help="Import the file from a specified path")
    parser.add_argument("-e", "--export", dest="export_path", metavar='FILE',
                        help="Export the generated file to the specified path")
    parser.add_argument("-d", "--decimate", dest="decimate_amount", metavar='N',
                        type=float, help="Decimation factor to apply per model")
    parser.add_argument("-c", "--clean", dest="clean_amount", metavar='N',
                        type=bool, help="CleanUp bool for small dense parts")
    args = parser.parse_args(argv)  # In this example we wont use the args

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

    if not args.decimate_amount:
        print("Error: --decimate=\"decimation factor\" arg not given, aborting.")
        parser.print_help()
        return

    if not args.decimate_amount:
        print("Error: --clean=\"clean bool\" arg not given, aborting.")
        parser.print_help()
        return

    print("Args parsed successfully")
    return(args.import_path, args.export_path,
           args.decimate_amount, args.clean_amount)
