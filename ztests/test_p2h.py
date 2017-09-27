# coding: utf-8

import unittest

import time

from p2h.pinyin2hanzi import p2h


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_p2h(self):
        self.assertTrue(True)

        while True:

            pnyins = input('请输入拼音: ')

            stime1 = time.time()

            hanzis = p2h(pnyins)

            etime1 = time.time()
            print(hanzis, '耗时:', (etime1 - stime1))


if __name__ == '__main__':
    unittest.main()
