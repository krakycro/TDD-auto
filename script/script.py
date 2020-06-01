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

    log.log_info("Parsing...")
    adapter.run(args)
    log.log_info("OK!")

    log.log_info("Linking...")
    linker.run(args.data)
    log.log_info("OK!")

    log.log_info("Generating...")
    generator.run(args)
    log.log_info("OK!")

    return 0

##############################################################################

if __name__ == "__main__":
    exit(main())

##############################################################################
