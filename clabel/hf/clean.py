# coding: utf-8

import os
import re
import sys

from clabel.helper import utils

from clabel.nlp import parser_local as parser


def clean(txt):
    if txt == u'此用户没有填写评论!':
        return None

    txt = re.sub(ur'&[a-zA-Z]+;', '', txt)

    # 删除省略号
    txt = txt.replace(u'...........', '')

    # 消除连续字符
    txt = re.sub(ur'(.)(\1+)', r'\1', utils.str2unicode(txt))

    tokens = [t[0] for tokens in parser.pos(txt) for t in tokens]
    if len(txt) < 3 or len(tokens) < 2 or len(set(tokens)) < 2:
        return None

    return re.split(ur'[\s,，.。:：!！?？、]', utils.str2unicode(txt))
