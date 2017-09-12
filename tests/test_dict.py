# coding: utf-8

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_dict(self):
        self.assertTrue(True)

        a = {'a': 'b'}
        b = {}

        if b:
            print('b is blank')
        else:
            print('b is not blank')


if __name__ == '__main__':
    unittest.main()
