# coding: utf-8

import os
import re
import time
import logging

from fastavro import writer

from clabel.config import NLP_POS_SEPARATOR
from clabel.config import NLP_SENT_SEPARATORS

from clabel.nlp import parser
from clabel.helper.utils import iter_file

from clabel.nlp.lexicon import irrelevantLexicon

logger = logging.getLogger(__file__)

__brands = irrelevantLexicon.get_words('brand')
__models = irrelevantLexicon.get_words('model')
__personals = irrelevantLexicon.get_words('personal')


def pos(source_file, dest_file):
    """
    词性标注，标注之后进行修正
    :param source_file: 原始评论
    :param dest_file: 标注后的评论
    """
    logger.info('to pos comment text...')

    tmp = dest_file + '.tmp'
    with open(tmp, 'wb') as f:
        for line in iter_file(source_file):
            sents = parser.pos(line)
            for sent in sents:
                f.write('%s\n' % ' '.join(['%s%s%s' % (token, NLP_POS_SEPARATOR, pos) for token, pos in sent]))

    correct_pos(tmp, dest_file)


def parse(pinglun_file, dest_avro_file):
    """
    句法解析，结果保存为avro文件
    :param pinglun_file:
    :param dest_avro_file:
    """
    logger.info('parse pinglun run...')

    pdir = os.path.dirname(dest_avro_file)
    if not os.path.exists(pdir):
        os.mkdir(pdir)

    def pingluns():

        for pinglun in iter_file(pinglun_file):

            if pinglun:

                pinglun_obj = {
                    'txt': pinglun,
                    'sents': []
                }

                for sentence in parser.parse2sents(pinglun):
                    tokens = set()

                    for relation in sentence.relations:
                        if relation.token1.word != 'Root':
                            tokens.add(relation.token1)
                        tokens.add(relation.token2)

                    tokens = sorted(tokens, key=lambda t: t.id)

                    pinglun_obj['sents'].append({
                        'sent': ''.join([t.word for t in tokens]),
                        'tokens': [{'word': t.word, 'pos': t.pos} for t in tokens],
                        'relations': [{'format': r.format, 'token1': r.token1.word, 'token2': r.token2.word} for r
                                      in sentence.relations]
                    })

                yield pinglun_obj

    with open(dest_avro_file, 'wb') as df:
        writer(df, _PARSE_DATA_SCHEMA, pingluns())


def correct_pos(source_file, dest_file):
    """
    修正词性
    :param source_file:
    :param dest_file:
    """
    logging.info('to correct pos...')

    correct_map = {'BR': __brands, 'MO': __models, 'PE': __personals}

    with open(dest_file, 'wb') as f:
        for line in iter_file(source_file):
            new_tps = list()
            for tp in re.findall(ur'(\S+)%s(\S+)' % NLP_POS_SEPARATOR, line.decode('utf-8')):
                new_tp = tp

                for k, v in correct_map.items():
                    if tp[0] in v:
                        new_tp = (tp[0], k)

                new_tps.append(new_tp)
            f.write('%s\n' % ' '.join(['%s%s%s' % (tp[0], NLP_POS_SEPARATOR, tp[1]) for tp in new_tps]))


_PARSE_DATA_SCHEMA = {
    'namespace': 'clabel.bi.meizu.com',
    'name': 'PSentence',
    'type': 'record',
    'fields': [{
        'name': 'txt',
        'type': 'string'
    }, {
        'name': 'sents',
        'type': {
            'type': 'array',
            'items': {
                'name': 'Sent',
                'type': 'record',
                'fields': [{
                    'name': 'sent',
                    'type': 'string'
                }, {
                    'name': 'tokens',
                    'type': {
                        'type': 'array',
                        'items': {
                            'name': 'Token',
                            'type': 'record',
                            'fields': [{
                                'name': 'word',
                                'type': 'string'
                            }, {
                                'name': 'pos',
                                'type': 'string'
                            }]
                        }
                    }
                }, {
                    'name': 'relations',
                    'type': {
                        'type': 'array',
                        'items': {
                            'name': 'Relation',
                            'type': 'record',
                            'fields': [{
                                'name': 'format',
                                'type': 'string'
                            }, {
                                'name': 'token1',
                                'type': 'string'
                            }, {
                                'name': 'token2',
                                'type': 'string'
                            }]
                        }
                    }
                }]
            }
        }
    }]
}
