# coding: utf-8

import unittest

from w2c import word2vec as w2v


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_word2vec_model_train(self):
        self.assertTrue(True)

        w2v.train()

    def test_word2vec_model(self):
        self.assertTrue(True)

        model = w2v.get()
        for token, similarity in model.most_similar(positive=['屏幕']):
            print(token, similarity)

    def test_word2vec_vec(self):
        self.assertTrue(True)

        model = w2v.get()
        print(model['屏幕'])


if __name__ == '__main__':
    unittest.main()
