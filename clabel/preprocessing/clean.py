# coding: utf-8

import re
import codecs
import logging
import html.parser

from clabel.helper.utils import iter_file

logger = logging.getLogger(__file__)


html_parser = html.parser.HTMLParser()


def clean_file(source_file, dest_file):
    logger.info('clean pinglun run...')

    with codecs.open(dest_file, 'w', encoding='utf-8') as f:
        for line in iter_file(source_file):
            for sent in clean_txt(line):
                f.write('%s\n' % sent)


def clean_txt(txt):

    txt = txt.strip()

    # 还原html转义字符，&hellip; => ……
    txt = html_parser.unescape(txt)

    # Todo HTMLParser不能讲&#039;转换，而单独测试时是可以的，不知为何。。
    txt = txt.replace('&#039;', '\'')

    # 忽略用空格分割的评论
    if txt.find(' ') != -1:
        logger.debug('评论中包含空格，这条评论将被忽略。')
        return set()

    sents = extract_standard_sentences(txt)

    '''过滤单句'''
    return [sent for sent in sents if is_meaningful(sent)]


def clean_txt2(txt):

    txt = txt.strip()

    # 还原html转义字符，&hellip; => ……
    txt = html_parser.unescape(txt)

    # Todo HTMLParser不能讲&#039;转换，而单独测试时是可以的，不知为何。。
    txt = txt.replace('&#039;', '\'')

    # 空格换成逗号
    txt.replace(' ', '，')

    sents = extract_standard_sentences(txt)

    '''过滤单句'''
    return [sent for sent in sents if is_meaningful(sent)]


_SENT_CHAR_SET = '[0-9a-zA-Z\u4e00-\u9fa5_-]'
_rule1 = re.compile('((?:%s+，)*%s+[。！；？?])' % (_SENT_CHAR_SET, _SENT_CHAR_SET))
_rule2 = re.compile('((?:%s+，)*%s+)' % (_SENT_CHAR_SET, _SENT_CHAR_SET))


def extract_standard_sentences(line):
    """
    提取规范句，规范句的形式如下：
    1. xxx，xxx，xxx。 => 完整提取
    2. xxx, xxx =>提取后加'。'
    :param line:
    :return: 规范句集合
    """
    sents = set()

    # 1. xxx，xxx，xxx。 => 完整提取
    groups = re.findall(_rule1, line)
    for sent in groups:
        sents.add(sent)

    # 2. xxx, xxx =>提取后加'。
    if not groups:
        groups = re.findall(_rule2, line)
        for sent in groups:
            sents.add('%s。' % sent)

    return sents


def is_meaningful(sent):
    """
    判断句子是否有意义
    1. 必须至少包含两个连续的中文（一个词）
    2. 必须包含至少两个不同的字
    3. 不是无意义的评论
    :param sent:
    :return:
    """

    # 必须至少包含两个连续的中文（一个词）
    if not re.match(r'.*[\u4e00-\u9fa5]{2,999}.*', sent):
        return False

    words = re.findall(r'[\u4e00-\u9fa5]', sent)

    # 必须包含至少两个不同的字
    if len(set(words)) < 2:
        return False

    # 不是无意义的评论
    if ''.join(words) in SYS_COMMENTS:
        return False

    return True


SYS_COMMENTS = ['此用户没有填写评论', '好评']