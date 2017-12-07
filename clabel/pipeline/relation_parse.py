# coding: utf-8

import os
import logging

from fastavro import writer

from common.utils import iter_file
from nlp.parser import default_parser as parser

logger = logging.getLogger(__name__)


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

    with open(dest_avro_file, 'wb') as df:
        writer(df, _PARSE_DATA_SCHEMA, _iter_parse_file(pinglun_file))


def _iter_parse_file(pinglun_file):

    for i, pinglun in enumerate(iter_file(pinglun_file)):
        if i % 10000 == 0:
            logger.info('parse line %d' % i)

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
