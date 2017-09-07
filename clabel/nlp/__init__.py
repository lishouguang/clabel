# coding: utf-8

import os

from clabel.config import RESOURCE_DIR
from clabel.helper import utils

stop_words = utils.read_file(os.path.join(RESOURCE_DIR, 'stop.txt'))
