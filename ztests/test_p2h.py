# coding: utf-8

import unittest

import time

from p2h.pinyin2hanzi import p2h


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_p2h(self):
        self.assertTrue(True)

        stime1 = time.time()
        pnyins = 'xingjiabihengao'
        hanzis = p2h(pnyins)
        etime1 = time.time()
        print(hanzis, (etime1 - stime1))

        stime2 = time.time()
        pnyins = 'pingmutaidale'
        hanzis = p2h(pnyins)
        etime2 = time.time()
        print(hanzis, (etime2 - stime2))

        stime3 = time.time()
        pnyins = 'youdianfahuang'
        hanzis = p2h(pnyins)
        etime3 = time.time()
        print(hanzis, (etime3 - stime3))


if __name__ == '__main__':
    unittest.main()
