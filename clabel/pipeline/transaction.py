# coding: utf-8

import re
import logging

from clabel.helper import utils
from clabel.config import NLP_POS_SEPARATOR
from clabel.config import FREQUENT_FEATURE_POSES

logger = logging.getLogger(__file__)

RE_NORMAL_CHARS = ur'^[0-9a-zA-Z\u4e00-\u9fa5]+$'


def create(pos_file, dest_file, field_sep=','):
    logger.info('to create transaction basket file...')

    with open(dest_file, 'wb') as f:
        for line in utils.iter_file(pos_file):
            '''
            JJ=名词修饰符
            NN=普通名词
            DEG=的
            '''

            tokens = []

            line = line.decode('utf-8')

            # 规则：三名词：NN(+DEG)+NN(+DEG)+NN
            # line = ' 都AD 是VC 回答VV 预售NN 的DEG 类NN 的DEG 商品NN 不AD 知道VV'
            nps = re.findall(ur'(\S+)\001NN(?:\s\S+\001DEG)?\s(\S+)\001NN(?:\s\S+\001DEG)?\s(\S+)\001NN', line)
            for np in nps:
                tokens.append('%s_%s_%s' % np)

            # 规则：两名词： NN(+DEG)+NN
            # line = u'快递NN 速度NN 也AD 很AD 快VA'
            nps = re.findall(ur'(\S+)\001NN(?:\s\S+\001DEG)?\s(\S+)\001NN', line)
            for np in nps:
                s_np = '%s_%s' % np
                if not is_token_exist(s_np, tokens):
                    tokens.append(s_np)

            # 规则：一名词：NN
            # line = u'快递NN 也AD 很AD 快VA'
            nps = re.findall(ur'(\S+)\001NN', line)
            for np in nps:
                s_np = '%s' % np
                if not is_token_exist(s_np, tokens):
                    tokens.append(s_np)

            '''
            # 规则： JJ+NN
            line = u'客服JJ 态度NN 差VA'
            nps = re.findall(ur'(\S+)\001JJ\s(\S+)\001NN', line)
            for np in nps:
                print '%s_%s' % np
            '''

            if tokens:
                f.write('%s\n' % field_sep.join(tokens))


def is_token_exist(s_np, tokens):
    is_exist = False
    for x in tokens:
        if x.find(s_np) != -1:
            is_exist = True
    return is_exist


def create2(pos_file, dest_file, field_sep=','):
    logger.info('to create transaction basket file...')

    with open(dest_file, 'wb') as f:
        for line in utils.iter_file(pos_file):
            nouns = []

            for pair in line.split():
                try:
                    token, pos = pair.split(NLP_POS_SEPARATOR)

                    is_noun = pos in FREQUENT_FEATURE_POSES
                    not_exist = token not in nouns
                    is_normal_chars = re.match(RE_NORMAL_CHARS, token.decode('utf-8'))

                    if is_noun and not_exist and is_normal_chars:
                        nouns.append(token)
                except Exception:
                    pass

            if nouns:
                f.write('%s\n' % field_sep.join(nouns))
