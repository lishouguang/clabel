# coding: utf-8

import sys
import os
import unittest

from clabel.config import RESOURCE_DIR


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_jnius(self):
        self.assertTrue(True)

        import jnius_config

        jnius_config.add_options('-Xrs', '-Xmx1024m')
        jnius_config.add_options('-Dfile.encoding=UTF-8')
        jnius_config.add_classpath('.')
        jnius_config.add_classpath(os.path.join(RESOURCE_DIR, 'java', 'hanlp-1.3.4-release'))
        jnius_config.add_classpath(os.path.join(RESOURCE_DIR, 'java', 'hanlp-1.3.4-release', 'hanlp-1.3.4.jar'))

        from jnius import autoclass

        txt = '手机很漂亮。'

        HanLP = autoclass('com.hankcs.hanlp.HanLP')

        print('-' * 10 + 'segment' + '-' * 10)
        words = HanLP.segment(txt)
        for i in range(words.size()):
            word = words.get(i)
            print('{}/{}'.format(word.word, word.nature.toString()))

        print('-' * 10 + 'relation' + '-' * 10)

        relations = HanLP.parseDependency(txt)
        iterator = relations.iterator()
        while iterator.hasNext():
            relation = iterator.next()
            print('{} <{}> {}'.format(relation.LEMMA, relation.DEPREL, relation.HEAD.LEMMA))

    def test_jpype(self):
        self.assertTrue(True)

        import jpype

        hanlp_dir = os.path.join(RESOURCE_DIR, 'java', 'hanlp-1.3.4-release')
        jar_file_path = os.path.join(hanlp_dir, 'hanlp-1.3.4.jar')

        separator = ';' if sys.platform.startswith('win') else ':'
        classpath_option = '-Djava.class.path={}{}{}'.format(hanlp_dir, separator, jar_file_path)
        jpype.startJVM(jpype.getDefaultJVMPath(), classpath_option, '-Xrs', '-Xmx1024m')

        txt = '手机很漂亮。'

        HanLP = jpype.JClass('com.hankcs.hanlp.HanLP')
        words = HanLP.segment(txt)
        print('standard segment:', words, type(words))

        NLPTokenizer = jpype.JClass('com.hankcs.hanlp.tokenizer.NLPTokenizer')
        words = NLPTokenizer.segment(txt)
        print('nlp segment:', words, type(words))

        sentence = HanLP.parseDependency(txt)
        print(sentence, type(sentence))

        jpype.shutdownJVM()


if __name__ == '__main__':
    unittest.main()
