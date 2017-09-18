# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR

from clabel.model.wed import CharModel
from clabel.model.wed import HomoModel
from clabel.model.wed import PinyinModel


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_wed_char_model_train(self):
        self.assertTrue(True)

        model = CharModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'),
                          workspace=os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'char'))
        model.train()
        model.save()
        
    def test_wed_pinyin_model_train(self):
        self.assertTrue(True)

        model = PinyinModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'),
                            workspace=os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'pinyin'))
        model.train()
        model.save()

    def test_homonym(self):
        self.assertTrue(True)

        m = HomoModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'))
        print(m.pinyin2chars('hen'))
        print(m.dictx)
        
    def test_correct(self):
        self.assertTrue(True)

        model_file = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'char', 'wed.model')
        keras_model_file = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'char', 'wed.keras.model')
        cmodel = CharModel.load(model_file=model_file, keras_model_file=keras_model_file)

        model_file = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'pinyin', 'wed.model')
        keras_model_file = os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'wed', 'pinyin', 'wed.keras.model')
        pmodel = PinyinModel.load(model_file=model_file, keras_model_file=keras_model_file)

        m = HomoModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'))

        txt = '象素不行'
        print(pmodel.correct(txt, cmodel, m))
        
        
if __name__ == '__main__':
    unittest.main()
