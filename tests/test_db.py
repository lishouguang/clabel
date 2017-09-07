# coding: utf-8

import unittest

from clabel.pipeline import db


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_insert(self):
        self.assertTrue(True)

        db.insertOrUpdate('屏幕', '花屏', '-')

        print db.query('屏幕', '花屏2')

    def test_all(self):
        self.assertTrue(True)

        for context, opinion, polar in db.queryAll():
            print context, opinion, polar

    def test_delete(self):
        self.assertTrue(True)

        db.delete('屏幕', '漂亮')


if __name__ == '__main__':
    unittest.main()
