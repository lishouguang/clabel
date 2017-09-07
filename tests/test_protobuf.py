# coding: utf-8

import unittest

from clabel.model import sentence_pb2 as sp


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_proto_buf(self):
        self.assertTrue(True)

        psentence = sp.PSentence()
        psentence.sent = u'手机的屏幕不错'
        psentence.token.extend([u'手机', u'的', u'屏幕', u'不错'])

        relation = psentence.relation.add()
        relation.format = u'ff'
        relation.token1 = u'手机'
        relation.token2 = u'屏幕'

        relation2 = psentence.relation.add()
        relation2.format = u'ff2'
        relation2.token1 = u'手机'
        relation2.token2 = u'性能'

        print psentence.IsInitialized()


if __name__ == '__main__':
    unittest.main()
