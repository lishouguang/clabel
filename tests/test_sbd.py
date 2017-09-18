# coding: utf-8

import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.model.sbd import SBDModel


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_sbd_train(self):
        self.assertTrue(True)

        model = SBDModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'))
        model._build_ctable()
        model.train()
        model.save()

    def test_sbd(self):
        self.assertTrue(True)

        txt = '性价比很高但是容易碎屏等等在入手吧'

        model = SBDModel.load(keras_model_file=os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'sbd', 'sbd.keras.model'))
        sequence = model.predict_sequence(txt)
        print(sequence)

        ptxt = model.predict_txt(txt)
        print(ptxt)


if __name__ == '__main__':
    unittest.main()
