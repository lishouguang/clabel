# coding: utf-8

import re
import logging

from clabel.helper import utils
from clabel.config import NLP_POS_SEPARATOR
from clabel.config import NLP_SENT_SEPARATORS

logger = logging.getLogger(__file__)

RE_SENT_SPLIT = re.compile(('[%s]%sPU' % (''.join(NLP_SENT_SEPARATORS), NLP_POS_SEPARATOR)).decode('utf-8'))


def create(pos_file, dest_file):
    logger.info('to split sentence...')

    with open(dest_file, 'wb') as f:
        for line in utils.iter_file(pos_file):
            for sent in re.split(RE_SENT_SPLIT, line.decode('utf-8')):
                sent = sent.strip().encode('utf-8')
                if sent:
                    f.write('%s\n' % sent)

            '''
            tokens = []

            for pair in line.split():
                try:
                    tokens.append(pair)

                    token, pos = pair.split(NLP_POS_SEPARATOR)
                    if token in NLP_SENT_SEPARATORS:
                        f.write('%s\n' % ' '.join(tokens))
                        tokens = []
                except Exception:
                    pass

            if tokens:
                f.write('%s\n' % ' '.join(tokens))
            '''
