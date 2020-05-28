import adapter.adapter as adapter
import adapter.linker as linker

import general.logger as log
import general.utils as utils

import generator.generator as generator

from general.model import *

##############################################################################

def main():

    # args.data is root database
    args = utils.arg_parser()

    print("Parsing...")
    adapter.run(args)
    print("OK!")

    print("Linking...")
    linker.run(args)
    print("OK!")

    print("Generating...")
    generator.run(args)
    print("OK!")

    return 0

##############################################################################

if __name__ == "__main__":
    exit(main())

##############################################################################
