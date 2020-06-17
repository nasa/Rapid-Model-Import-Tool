# parse objs into many smaller files for easier decimation

def parser(filepath):
    with open(filepath, 'r') as file:
        for i, line in enumerate(file):
            #print ('#' + str(i) + ' ' + line)
            pass

        print ("eof")


if __name__ == "__main__":
    parser("test\\CM EXT.obj")