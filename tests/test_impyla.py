# coding: utf-8

import unittest

from impala.dbapi import connect


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_impyla(self):
        self.assertTrue(True)

        conn = connect(host='meizu-bi-hd-client-01', database='jingtian', auth_mechanism='GSSAPI')

        import flask

        app = flask.Flask(__file__)
        app.run()

if __name__ == '__main__':
    unittest.main()
