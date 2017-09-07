# coding: utf-8

import re
import logging

from clabel.helper import utils
from clabel.config import NLP_POS_SEPARATOR
from clabel.config import FREQUENT_FEATURE_POSES

from clabel.nlp import parser

logger = logging.getLogger(__file__)

RE_NORMAL_CHARS = ur'^[0-9a-zA-Z\u4e00-\u9fa5]+$'


def create(sentences, features, dest_file, field_sep=',', parsed=True):
    logger.info('to create transaction basket file...')

    if not parsed:
        sentences = [sentence for cmt in R for sentence in parser.parse(cmt)['sentences']]

    with open(dest_file, 'wb') as df:
        for sentence in sentences:
            itemset = []

            for relation, token1, token2 in parse_relation(sentence):
                if relation in ['compound:nn(NN, NN)', 'nmod:assmod(NN, NN)']:
                    f = '%s_%s' % (token2, token1)
                    if f in features:
                        itemset.append(f)

            for token in sentence['tokens']:
                word = token['word']
                if (token['pos'] in ['NN', 'JJ']) and (not is_token_exist(word, itemset)) and (word in features):
                    itemset.append(word)

            if itemset:
                df.write('%s\n' % field_sep.join(itemset))


def is_token_exist(s_np, tokens):
    is_exist = False
    for x in tokens:
        if x.find(s_np) != -1:
            is_exist = True
    return is_exist


def parse_relation(sentence):
    relations = []

    tokens = sentence['tokens']
    for dependency in sentence['basicDependencies']:
        relation, governor, dep = dependency['dep'], dependency['governorGloss'], dependency['dependentGloss']
        pgovernor = 'ROOT' if dependency['governor'] == 0 else tokens[dependency['governor'] - 1]['pos']
        pdep = tokens[dependency['dependent'] - 1]['pos']

        relation_format = '%s(%s, %s)' % (relation, pgovernor, pdep)
        relations.append((relation_format, governor, dep))

    return relations
