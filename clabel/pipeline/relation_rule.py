# coding: utf-8

import os
import re

from clabel.config import RESOURCE_DIR
from common.utils import iter_file

''''
解析关系规则
'''


class FORule(object):
    def __init__(self, template_file):
        self._rules = []

        for line in iter_file(template_file):
            if not line:
                continue

            template = line.split('#')[0].strip()

            if not template:
                continue

            groups = re.findall(r'^(.+)\((.+)_(.+), (.+)_(.+)\)$', template)

            if groups:
                rule, token1_pos, token1_type, token2_pos, token2_type = groups[0]

                if token1_type == 'f':
                    feature_order = 1
                    opinion_order = 2
                else:
                    feature_order = 2
                    opinion_order = 1

                rule_format = '%s(%s, %s)' % (rule, token1_pos, token2_pos)
                self._rules.append((rule_format, feature_order, opinion_order))

    def match(self, relation_format, token1, token2):
        """
        :param relation_format: SBV(a, n)
        :param token1: 第一个词
        :param token2: 第二个词
        :return:(特征词, 评价词)
        :rtype: (str, str)
        """
        for rule_format, feature_order, opinion_order in self._rules:
            if relation_format == rule_format:

                if feature_order == 1:
                    return token1, token2
                else:
                    return token2, token1

        return None, None


class FFRule(object):

    def __init__(self, template_file):
        self._rules = []

        for line in iter_file(template_file):
            if not line:
                continue

            template = line.split('#')[0].strip()
            self._rules.append(template)

    def match(self, relation_format, token1, token2):
        """
        :param relation_format: ATT(n, n)
        :param token1: 第一个词
        :param token2: 第二个词
        :return:
        :rtype: (str, str)
        """
        for rule_format in self._rules:
            if relation_format == rule_format:
                return token1, token2

        return None, None


class OORule(FFRule):
    pass


class MFRule(object):
    def __init__(self, template_file):
        self._rules = []

        for line in iter_file(template_file):
            if not line:
                continue

            template = line.split('#')[0].strip()

            if not template:
                continue

            groups = re.findall(r'^(.+)\((.+)_(.+), (.+)_(.+)\)$', template)

            if groups:
                rule, token1_pos, token1_type, token2_pos, token2_type = groups[0]

                if token1_type == 'm':
                    modifier_order = 1
                    token_order = 2
                else:
                    modifier_order = 2
                    token_order = 1

                rule_format = '%s(%s, %s)' % (rule, token1_pos, token2_pos)
                self._rules.append((rule_format, modifier_order, token_order))

    def match(self, relation_format, token1, token2):
        """
        :param relation_format: SBV(a, n)
        :param token1: 修饰词
        :param token2:
        :return:(特征词, 评价词)
        :rtype: (str, str)
        """
        for rule_format, modifier_order, token_order in self._rules:
            if relation_format == rule_format:
                if modifier_order == 1:
                    return token1, token2
                else:
                    return token2, token1

        return None, None


class MORule(MFRule):
    pass


parser_type = 'hanlp'
# parser_type = 'ltp'

foRule = FORule(os.path.join(RESOURCE_DIR, 'relation_rule', parser_type, 'fo.rule'))
ffRule = FFRule(os.path.join(RESOURCE_DIR, 'relation_rule', parser_type, 'ff.rule'))
ooRule = FFRule(os.path.join(RESOURCE_DIR, 'relation_rule', parser_type, 'oo.rule'))
mfRule = MFRule(os.path.join(RESOURCE_DIR, 'relation_rule', parser_type, 'mf.rule'))
moRule = MORule(os.path.join(RESOURCE_DIR, 'relation_rule', parser_type, 'mo.rule'))
