# coding: utf-8

import os
import re
import unittest

from clabel.config import RESOURCE_DIR

from clabel.helper import utils


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_create(self):
        self.assertTrue(True)

        '''
        JJ=名词修饰符
        NN=普通名词
        DEG=的
        '''

        line = ' 都AD 是VC 回答VV 预售NN 的DEG 类NN 的DEG 商品NN 不AD 知道VV 快递NN 的DEG 速度NN 也AD 很AD 快VA'

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

        print '%s\n' % ','.join(tokens)

    def test_create2(self):
        self.assertTrue(True)

        from clabel.pipeline import transaction2 as tx

        sentences = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.R'))
        sentences = [sentence for _, parsed in sentences for sentence in parsed['sentences']]

        fcounter = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'feature.counter'))
        # features = [x for f in fcounter if fcounter[f] > 1 for x in f.split('_')]
        features = [f for f in fcounter if fcounter[f] > 1]
        dest_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')

        tx.create(sentences, features, dest_file)


def is_token_exist(s_np, tokens):
    is_exist = False
    for x in tokens:
        if x.find(s_np) != -1:
            is_exist = True
    return is_exist


if __name__ == '__main__':
    unittest.main()
