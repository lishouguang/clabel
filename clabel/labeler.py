# coding: utf-8

import logging
import os

from fastavro import reader as avro_reader

from clabel.config import RESOURCE_DIR
from clabel.helper import utils
from clabel.model import word2vec as w2c
from clabel.nlp.lexicon import RevisedTerm
from clabel.nlp.lexicon import degreeLexicon
from clabel.nlp.lexicon import fixedSentimentLexicon
from clabel.nlp.parser import Token
# from clabel.nlp.parser import default_ltp_parser as parser
from clabel.nlp.parser import default_parser as parser
from clabel.pipeline import cluster
from clabel.pipeline import double_propagation
from clabel.pipeline import prune
from clabel.pipeline import sentence_parser
from clabel.preprocessing import clean

logger = logging.getLogger(__file__)

from clabel.pipeline.relation_rule import foRule
from clabel.pipeline.relation_rule import mfRule
from clabel.pipeline.relation_rule import moRule


class LexiconExtractor(object):

    def __init__(self, workspace=os.path.join(RESOURCE_DIR, 'extractor'), threshold=0.00001):
        """
        :param workspace: 工作目录，临时文件保存在这里
        :param threshold: 阈值，0.00001 表示10W条评论中至少出现一次
        """

        self._workspace = workspace
        self._clean_file = os.path.join(self._workspace, 'clean', 'clean.txt')
        self._relation_file = os.path.join(self._workspace, 'relation', 'relation.avro')

        self._dp_f_file = os.path.join(self._workspace, 'dp', 'dp.F')
        self._dp_o_file = os.path.join(self._workspace, 'dp', 'dp.O')
        self._dp_f_counter = os.path.join(self._workspace, 'dp', 'dp.fcounter')
        self._dp_o_counter = os.path.join(self._workspace, 'dp', 'dp.ocounter')

        self._prune_f_file = os.path.join(self._workspace, 'prune', 'dp.F.pruned')
        self._prune_o_file = os.path.join(self._workspace, 'prune', 'dp.O.pruned')

        self._word2vec_file = os.path.join(self._workspace, 'word2vec', 'w2c.model')
        # self._word2vec_file = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'word2vec', 'w2c.model')

        self._feature_file = os.path.join(self._workspace, '_result', 'features.raw')
        self._opinion_file = os.path.join(self._workspace, '_result', 'opinions.raw')

        if not os.path.exists(self._workspace):
            os.mkdir(self._workspace)

        for f in [self._clean_file, self._relation_file,
                  self._dp_f_file, self._dp_o_file, self._dp_f_counter, self._dp_o_counter,
                  self._prune_f_file, self._prune_o_file,
                  self._feature_file]:
            if not os.path.exists(os.path.dirname(f)):
                os.mkdir(os.path.dirname(f))

        self._threshold = threshold

    def run(self, pinglun_file, O_seeds):
        """
        提取特征词/评价词
        :param pinglun_file: 评论文本
        :param O_seeds: 种子评价词
        :return:
        """
        logger.info('pipeline run...')

        clean.clean_file(pinglun_file, self._clean_file)

        sentence_parser.parse(self._clean_file, self._relation_file)

        S = self._iter_sentences_relations(self._relation_file)

        F, O, fcounter, ocounter, rcount = double_propagation.extract(O_seeds, S)

        utils.write_file(self._dp_f_file, F)
        utils.write_file(self._dp_o_file, O)
        utils.save_obj(fcounter, self._dp_f_counter)
        utils.save_obj(ocounter, self._dp_o_counter)

        F, O = prune.prune(F, O, fcounter, ocounter, rcount, self._threshold)

        utils.write_file(self._prune_f_file, F)
        utils.write_file(self._prune_o_file, O)

        # T = self._iter_sentences_tokens(self._relation_file)
        # model = w2c.train(T)

        model = w2c.get(self._word2vec_file)

        cf = cluster.create(F, model, preference=-30)
        features = ['%s %s' % (cls, ' '.join(cf[cls])) for cls in cf]
        utils.write_file(self._feature_file, features)

        O = utils.read_file(self._prune_o_file)
        of = cluster.create(O, model, preference=None)
        opinions = ['%s %s' % (cls, ' '.join(of[cls])) for cls in of]
        utils.write_file(self._opinion_file, opinions)

        logger.info('pipeline over.')

        return cf, of, F, O

    @staticmethod
    def _iter_sentences_relations(avro_file):
        """
        将评论文本进行句法分析，取得依赖关系
        :return: [[(format, token1, token2), (format, token1, token2), ...], ...]
        """
        i = 0

        with open(avro_file, 'rb') as df:
            for pinglun in avro_reader(df):
                # txt = pinglun['txt']
                for sent in pinglun['sents']:
                    i += 1
                    # if i < 1000:
                    yield sent['relations']

        '''
        R = []
        source_dir = os.path.join(RESOURCE_DIR, 'parsed')
        i = 0
        for d in os.listdir(source_dir):
            i += 1
            print i
    
            R += utils.read_obj(os.path.join(source_dir, d))
            if len(R) >= 50000:
                break
    
        utils.save_obj(R, os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
        '''
        # R = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
        # R = [sentence for _, parsed in R for sentence in parsed['sentences']]
        # return R

    @staticmethod
    def _iter_sentences_tokens(avro_file):
        """
        将评论文本进行句法分析，取得分词
        :return: [[token1, token2, token3, ...], ...]
        """

        i = 0
        with open(avro_file, 'rb') as df:
            for pinglun in avro_reader(df):
                # txt = pinglun['txt']
                for sent in pinglun['sents']:
                    i += 1
                    # if i < 1000:
                    yield [token['word'] for token in sent['tokens']]


class LabelExtractor(object):

    def __init__(self, feature_file, opinion_file, lexicon_dir=None):
        self._fTerm = RevisedTerm(feature_file)
        self._oTerm = RevisedTerm(opinion_file)
        pass

    def extract_from_file(self, txt_file):
        """
        提取标签，输入源是一个文本文件
        :param txt_file:
        :return: [Label, Label, ...]
        """
        labels = []

        for line in utils.iter_file(txt_file):
            labels += self.extract_from_txt(line)

        return labels

    def extract_from_txt(self, txt):
        """
        提取标签，输入源是一段文本
        :param txt:
        :return: [Label, Label, ...]
        """
        txts = clean.clean_txt2(txt)
        logger.debug('清洗后的文本是：\n%s' % ('\n'.join(txts)))

        labels = []
        for txt in txts:
            for sent in parser.parse2sents(txt):
                slabels, features, opinions = self._extract_labels_stem(sent)

                for label in slabels:
                    # 获取特征修饰符，名词
                    ftoken = features[id(label)]
                    label.fmodifier = self._extract_feature_modifier(sent, ftoken)

                    # 获取评价词修饰符，程度词/否定词
                    otoken = opinions[id(label)]
                    label.omodifier = self._extract_opinion_modifier(sent, otoken)
                    label.omodifier2 = label.omodifier

                labels += slabels

            # 标准化标签的特征
            for label in labels:
                label.nfeature = self.normalize_feature(label.feature_np)

            # 标准化标签的评价词
            for label in labels:
                label.nopinion = self.normalize_opinion(label.opinion)

            # 标准化标签的程度词修饰符
            for label in labels:
                label.omodifier2 = self.normalize_opinion_degree(label.omodifier)

            # 判断情感极性
            for label in labels:
                label.polar = self.get_polar(label.feature_np, label.opinion, label.nfeature, label.nopinion)

        return labels

    def normalize_feature(self, feature):
        """
        标准化标签的特征
        :param feature:
        :return:
        """
        nfeature = self._fTerm.get_head(feature)
        if nfeature is None:
            nfeature = feature

        return nfeature

    def normalize_opinion(self, opinion):
        """
        标准化标签的评价词
        :param opinion:
        :return:
        """
        self
        return opinion

    def normalize_opinion_degree(self, omodifier):
        """
        标准化评价词的程度修饰符
        :param omodifier:
        """
        self
        words = omodifier.split(Label.OPINION_MODIFIER_SEPARATOR)
        for index, word in enumerate(words):
            if degreeLexicon.is_degree(word):
                words[index] = degreeLexicon.get_head(word)
        return Label.OPINION_MODIFIER_SEPARATOR.join(words)

    def get_polar(self, feature, opinion, nfeature, nopinion):
        """
        判断标签的情感极性
        :param feature:
        :param opinion:
        :param nfeature:
        :param nopinion:
        """
        polar = fixedSentimentLexicon.get_polar(opinion)

        if polar == 'x' and nopinion is not None:
            polar = fixedSentimentLexicon.get_polar(nopinion)

        # TODO 确定情感极性时需要在集群impala上进行查询，而外部机器访问不了集群
        # if polar == 'x':
        #     pmi.get_polar('%s_%s' % (feature, opinion))

        return polar

    def _extract_labels_stem(self, sentence):
        """
        提取出标签主干
        :param sentence:
        :return:
        """
        labels = []

        opinions = {}
        features = {}

        # 有评价对象的提取方式
        for relation in sentence.relations:

            ftoken, otoken = foRule.match(relation.format, relation.token1, relation.token2)
            # TODO 加上判断逻辑：判断ftoken是否属于特征库
            if ftoken and otoken and self._fTerm.is_term(ftoken.word):
                self.save_labels(labels, features, opinions, ftoken, otoken)

        # 无评价对象的提取方式，HED(Root/None, a/不错)
        rrelation = sentence.get_root_relation()
        if rrelation.token2.pos == 'a':

            is_exist = False
            for label in labels:
                if label.opinion == rrelation.token2.word:
                    is_exist = True
                    break

            if not is_exist:
                self.save_labels(labels, features, opinions, Token('', '', ''), rrelation.token2)

            # 并列关系，比如“便宜实惠”
            for xrelation in sentence.relations:
                if xrelation.relation == 'COO' and xrelation.token1 == rrelation.token2:
                    self.save_labels(labels, features, opinions, Token('', '', ''), xrelation.token2)
                    break

        return labels, features, opinions

    def _extract_feature_modifier(self, sentence, ftoken):
        """
        填充标签的特征词修饰语，组成特征短语
        :param sentence:
        :param ftoken:
        """
        self
        for relation in sentence.relations:

            mtoken, xtoken = mfRule.match(relation.format, relation.token1, relation.token2)
            if mtoken and xtoken and xtoken.word == ftoken.word:
                return mtoken.word
        return None

    def _extract_opinion_modifier(self, sentence, otoken):
        """
        填充评价词的修饰语，程度词/否定词
        :param sentence:
        :param otoken:
        """
        self
        modifiers = []
        for relation in sentence.relations:

            mtoken, xtoken = moRule.match(relation.format, relation.token1, relation.token2)
            if mtoken and xtoken and xtoken.word == otoken.word:
                modifiers.append(mtoken)
            '''
            if relation.format == 'ADV(a, d)' and relation.token1 == otoken:
                modifiers.append(relation.token2)
            '''

        return Label.OPINION_MODIFIER_SEPARATOR.join([t.word for t in modifiers])

    def save_labels(self, labels, features, opinions, ftoken, otoken):
        self
        label = Label(ftoken.word, otoken.word)
        labels.append(label)

        features[id(label)] = ftoken
        opinions[id(label)] = otoken


class Label(object):

    OPINION_MODIFIER_SEPARATOR = ','

    def __init__(self, feature, opinion, fmodifier='', omidifier=''):
        self.fmodifier = fmodifier
        self.feature = feature

        self.omodifier = omidifier
        self.omodifier2 = omidifier
        self.opinion = opinion

        self.polar = '0'

        self.nfeature = self.feature
        self.nopinion = self.opinion

    @property
    def feature_np(self):
        if self.fmodifier:
            return '%s_%s' % (self.fmodifier, self.feature)
        return self.feature

    @property
    def raw(self):
        return '%s_%s__(%s)%s %s' % (self.fmodifier, self.feature, self.omodifier, self.opinion, self.polar)

    @property
    def normalized(self):
        # 1）特征标准化 2）程度词标准化 3）评价词标准化
        return '%s__(%s)%s %s' % (self.nfeature, self.omodifier2, self.nopinion, self.polar)

    def __str__(self):
        return '(%s)%s[%s]__(%s)%s[%s]' % (self.fmodifier, self.feature, self.nfeature, self.omodifier, self.opinion,
                                           self.nopinion)
