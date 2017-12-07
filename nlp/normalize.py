# coding: utf-8

import os
import re
import copy
import logging

import numpy as np
import html.parser
from collections import Counter

from itertools import product

from nltk.model import build_vocabulary
from nltk.model import count_ngrams
from nltk.model.ngram import MLENgramModel
from nltk.model.ngram import LidstoneNgramModel

from collections import defaultdict

from clabel.config import RESOURCE_DIR
from common.utils import iter_file


logger = logging.getLogger(__name__)


def _init_normalize_map(pos_norm_file):
    return {line.split()[0]: line.split()[1] for line in iter_file(pos_norm_file)}


class PosNormalizer(object):
    """
    词性统一器，将多个词性标注集统一成LTP的标注集
    """

    pos_norm_file = os.path.join(RESOURCE_DIR, 'nlp', 'normalize', 'pos.normalize')
    pos_map = _init_normalize_map(pos_norm_file)

    @staticmethod
    def normalize(raw_pos):
        return PosNormalizer.pos_map.get(raw_pos, raw_pos)


def _init_pos_lm(corpus_file):

    def get_tokens(cf):
        for line in iter_file(cf):
            for w in line.split(' '):
                yield w

    def get_sentences(cf):
        for line in iter_file(cf):
            yield line.split(' ')

    '''构建词表'''
    # 词频低于这个值将被认为不是词汇
    # 逻辑删除，还保留着这个词的词频
    cutoff = 1
    tokens = get_tokens(corpus_file)
    vocab = build_vocabulary(cutoff, tokens)

    '''统计ngram'''
    order = 3
    sentences = get_sentences(corpus_file)
    ngram_counter = count_ngrams(order, vocab, sentences)

    '''ngram转换成score'''
    ngram_model = MLENgramModel(ngram_counter)

    return ngram_model


class PosLM(object):

    corpus_file = os.path.join(RESOURCE_DIR, 'nlp', 'normalize', 'ctb.pos.seq')
    _wordPredictModel = _init_pos_lm(corpus_file)

    @classmethod
    def next_token_prob(cls, contexts, token):
        return PosLM._wordPredictModel.score(token, contexts)

    @classmethod
    def sentence_prob(cls, sentence, order=3):
        probs = []

        sentence = [None] * (order-1) + sentence + [None] * (order-1)
        for i in range(len(sentence) - 2):
            contexts = sentence[i: i+2]
            token = sentence[i+2]

            p = PosLM.next_token_prob(contexts, token)
            probs.append(p)

        return 1

    @classmethod
    def sentence_entropy(cls, sentence):
        return PosLM._wordPredictModel.entropy(sentence)


class ReviseRule(object):

    SEPARATOR = '+'

    def __init__(self, rule_format):
        self._poses = rule_format.split(ReviseRule.SEPARATOR)

    def match(self, tokens):
        if len(self._poses) != len(tokens):
            return False

        for pos, token in zip(self._poses, tokens):
            wps = PosReviser.getPosSet(token.word)
            if pos not in wps:
                return False

        return True

    def matchAndRevise(self, tokens):
        if len(self._poses) != len(tokens):
            return tokens, 0

        tokens = copy.deepcopy(tokens)

        # a=0.111/b=0.222,c=0.3/d=0.4,d=1

        ok = True
        probs = []
        for pos, token in zip(self._poses, tokens):
            wps = PosReviser.getPosSet(token.word)
            if pos not in wps:
                ok = False
                break
            else:
                probs.append(wps[pos])

        if ok:
            for pos, token in zip(self._poses, tokens):
                token.pos = pos

            p = 1
            for p_ in probs:
                p *= p_
            return tokens, p

        return tokens, 0

    def __str__(self):
        return ReviseRule.SEPARATOR.join(self._poses)


def _init_revise_map(pos_revise_file):
    revise_map = dict()

    for line in iter_file(pos_revise_file):
        word = line.split(' ')[0]

        # 过滤掉出现次数过低的词性
        pcs = {p: int(c) for p, c in re.findall(r'([a-zA-Z]+)=(\d+)', line) if int(c) > 1}
        total = sum(pcs.values())
        revise_map[word] = {p: 1.0*c / total for p, c in pcs.items()}
        revise_map = {w: s for w, s in revise_map.items() if len(s) > 1}

    return revise_map


class PosReviser1(object):
    """
    词性修正器，使用特定逻辑对标注的词性进行修正
    """
    pos_revise_file = os.path.join(RESOURCE_DIR, 'nlp', 'normalize', 'pos.revise')
    revise_map = _init_revise_map(pos_revise_file)

    revise_rules = [ReviseRule(rf) for rf in iter_file(os.path.join(RESOURCE_DIR, 'nlp', 'normalize', 'rule.revise'))]

    @classmethod
    def revise(cls, tokens):
        """
        :param tokens: list(Token)
        """
        for i, token in enumerate(tokens):
            if i == len(tokens) - 1:
                break

            token2 = tokens[i+1]

            matches = []
            for rule in PosReviser.revise_rules:
                xtokens, p = rule.matchAndRevise([token, token2])
                if p > 0:
                    matches.append((p, rule, xtokens))

            if matches:
                p, rule, xtokens = max(matches, key=lambda tp: tp[0])

                xtoken1, xtoken2 = xtokens[0], xtokens[1]

                if token.pos != xtoken1.pos or token2.pos != xtoken2.pos:
                    logger.debug('【%s】match revise rules: %s, select rule: %s, prob: %f  -> 【%s】' %
                                 ('%s/%s %s/%s' % (token.word, token.pos, token2.word, token2.pos),
                                  ', '.join(['%s/%f' % (str(m[1]), m[0]) for m in matches]),
                                  str(rule),
                                  p,
                                  '%s/%s %s/%s' % (xtoken1.word, xtoken1.pos, xtoken2.word, xtoken2.pos)))

                token.pos, token2.pos = xtokens[0].pos, xtokens[1].pos

            '''
            # 相邻的两个词有d+a的可能就改成d+a
            if 'd' in gps(token.word) and 'a' in gps(token2.word):
                if 'd' != token.pos or 'a' != token2.pos:
                    logger.debug('相邻的两个词有d+a的可能就改成d+a, %s/%s_%s/%s -> %s/%s_%s/%s' % (
                        token.word, token.pos, token2.word, token2.pos, token.word, 'd', token2.word, 'a'
                    ))
                token.pos = 'd'
                tokens[i+1].pos = 'a'

            # 相邻的两个词有n+a的可能就改成n+a
            if 'n' in gps(token.word) and 'a' in gps(token2.word):
                if 'n' != token.pos or 'a' != token2.pos:
                    logger.debug('相邻的两个词有n+a的可能就改成n+a, %s/%s_%s/%s -> %s/%s_%s/%s' % (
                        token.word, token.pos, token2.word, token2.pos, token.word, 'n', token2.word, 'a'
                    ))
                token.pos = 'n'
                tokens[i+1].pos = 'a'
            '''

    @classmethod
    def getPosSet(cls, word):
        return PosReviser.revise_map.get(word, {})


class PosReviser(object):
    """
    词性修正器，使用特定逻辑对标注的词性进行修正
    """
    pos_revise_file = os.path.join(RESOURCE_DIR, 'nlp', 'normalize', 'pos.multiple')
    revise_map = _init_revise_map(pos_revise_file)

    @classmethod
    def revise(cls, tokens):
        """
        :param tokens: list(Token)
        """

        tokens = copy.deepcopy(tokens)

        entropys = []

        poses = []
        for t in tokens:
            ps = list(PosReviser.getPosSet(t.word).keys())
            if not ps:
                ps = [t.pos]

            poses.append(ps)

        for cand in product(*poses):
            e = PosLM.sentence_entropy(list(cand))
            entropys.append((cand, e))

            # p = PosLM.sentence_prob(list(cand))
            # print(p)

        cand, entropy = min(entropys, key=lambda tp: tp[1])

        for p, token in zip(cand, tokens):
            token.pos = p

        return tokens

    @classmethod
    def getPosSet(cls, word):
        return PosReviser.revise_map.get(word, {})


def build_multiple_pos_vocab(pinglun_corpus_file):
    """
    从CTB语料中获取多词性规则，从评论语料中获取领域内高词频词语，人工修正
    """

    from nlp.parser import combParser

    # 词性列表
    posDict = _analysis_ctb_pos()

    # 词性类别
    typeCountDict = {w: len(set([x[0] for x in pd.keys()])) for w, pd in posDict.items()}

    # 词性方差
    stdDict = dict()

    '''
    去除一部分词汇
    '''
    words = posDict.keys()
    retains = []
    for word in words:
        if typeCountDict[word] <= 1:
            continue

        poses = posDict[word]

        total = sum(poses.values())
        if total < 10:
            continue

        pos_probs = {p: 1.0 * c / total for p, c in poses.items()}

        # 如果某个词性概率超过90%，怎认为这个词的词性是固定的
        if len([p for p in pos_probs.values() if p > 0.9]) > 0:
            continue

        for p, prob in pos_probs.items():
            if prob < 0.05:
                del posDict[word][p]

        stdDict[word] = np.std([pos_probs[p] for p in posDict[word].keys()])

        retains.append(word)

    '''
    统计评论语料词频
    '''
    html_parser = html.parser.HTMLParser()

    counter = Counter()
    for i, line in enumerate(iter_file(pinglun_corpus_file)):
        # 还原html转义字符，&hellip; => ……
        line = html_parser.unescape(line)
        # Todo HTMLParser不能讲&#039;转换，而单独测试时是可以的，不知为何。。
        line = line.replace('&#039;', '\'')
        counter.update(combParser.segment(line))

    '''
    查看词频前列的词的多词性情况
    '''
    for w, c in counter.most_common():
        if c < 100:
            continue

        if w in posDict and w in stdDict:
            print(w, c, ' '.join(['%s=%s' % (p, c) for p, c in posDict.get(w, {}).items()]), stdDict.get(w))


def _analysis_ctb_pos():
    """
    从CTB语料中统计各词的词性，获得有多个词性的词
    """

    posDict = defaultdict(lambda: defaultdict(int))

    base_dir = os.path.join(RESOURCE_DIR, 'nlp', 'corpus', 'ctb8.0', 'data', 'postagged')
    pattern = r'([\u4e00-\u9fa5]+)_([a-zA-Z]+)'

    def iter_corpus(pdict, base_dir_):
        for f in os.listdir(base_dir_):
            f = os.path.join(base_dir_, f)

            if os.path.isdir(f):
                iter_corpus(pdict, f)
            else:
                for line in iter_file(f):
                    for w, p in re.findall(pattern, line):
                        p = PosNormalizer.normalize(p)
                        pdict[w][p] += 1

    iter_corpus(posDict, base_dir)

    return posDict
