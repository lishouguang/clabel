# coding: utf-8

import os
import logging

from clabel.config import RESOURCE_DIR
from clabel.helper.utils import iter_file

logger = logging.getLogger(__file__)


def create(cat, source_file, dest_file):
    logger.info('to sample %s comments...' % cat)

    i = 0
    with open(dest_file, 'wb') as df:
        for line in iter_file(source_file):
            i += 1
            if i % 100000 == 0:
                logger.info('Handled %d lines' % i)

            cat1, cat2, cmt = line.split('\001')
            if '%s/%s' % (cat1, cat2) == cat:
                df.write('%s\n' % cmt)
