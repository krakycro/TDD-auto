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

    log.log_master("Parsing...")
    adapter.run(args)
    log.log_master("OK!")

    log.log_master("Linking...")
    linker.run(args.data)
    log.log_master("OK!")

    log.log_master("Generating...")
    generator.run(args)
    log.log_master("OK!")

    log.log_master("DONE!")

    return 0

##############################################################################

if __name__ == "__main__":
    exit(main())

##############################################################################
