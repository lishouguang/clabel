# coding: utf-8

import os
import re
import unittest

from clabel.config import RESOURCE_DIR
from clabel.pipeline.relation_rule import foRule
from clabel.pipeline.relation_rule import ffRule
from clabel.pipeline.relation_rule import ooRule
from clabel.pipeline.relation_rule import mfRule
from clabel.pipeline.relation_rule import moRule


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_relation_rule(self):
        self.assertTrue(True)

        templates = ['SBV(a_o, v_f)']

        pattern = r'^(.+)\((.+)_(.+), (.+)_(.+)\)$'
        print(re.match(pattern, templates[0]))
        xx = re.findall(pattern, templates[0])
        print(xx)

    def test_1(self):
        self.assertTrue(True)

        fmt = 'ATT(n, n)'
        token1 = '外形'
        token2 = '手机'

        # rt = FORuleTemplate(os.path.join(RESOURCE_DIR, 'relation_rule', 'fo.rule'))
        # feature, opinion = rt.match(fmt, token1, token2)
        # print feature, opinion

        # ft = FFRule(os.path.join(RESOURCE_DIR, 'relation_rule', 'ff.rule'))
        # feature1, feature2 = ft.match(fmt, token1, token2)
        # print feature1, feature2

        # oo = OORule(os.path.join(RESOURCE_DIR, 'relation_rule', 'oo.rule'))
        # opinion1, opinion2 = oo.match(fmt, token1, token2)
        # print opinion1, opinion2

        # feature1, feature2 = mfRule.match(fmt, token1, token2)
        # print feature1, feature2

        modifier, opinion = moRule.match(fmt, token1, token2)
        print(modifier, opinion)

if __name__ == '__main__':
    unittest.main()
