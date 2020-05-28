import re

from pathlib import Path

import general.logger as log

from general.model import *

##############################################################################

def _generate_folder(args, folder: Path):
    print(folder)


##############################################################################

def run(args):

    _generate_folder(args, args.output_folder)

    return True

##############################################################################
