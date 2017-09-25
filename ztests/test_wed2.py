# coding: utf-8

import re
import unittest

from wed.wed2 import correct


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_correct(self):
        self.assertTrue(True)

        txt = '屏幕太大了，不好看。'
        txt = ''.join(re.findall(r'[\u4e00-\u9fa5，。？！?,]', txt))
        ctxt = correct(txt)
        print('txt:', txt)
        print('correct txt:', ctxt)


if __name__ == '__main__':
    unittest.main()
