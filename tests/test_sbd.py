# coding: utf-8

import re
import os
import unittest

from clabel.config import RESOURCE_DIR
from clabel.model.sbd import SBDModel

from clabel.helper.utils import iter_file
from clabel.helper.utils import write_file


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

        model = SBDModel.load(keras_model_file=os.path.join(RESOURCE_DIR, 'model', 'internal_model', 'sbd', 'sbd.keras.model'))

        lines = []
        for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'comment.mobile.txt')):
            words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', line)
            sent = ''.join(words)
            # sequence = model.predict_sequence(sent)
            pline = model.predict_txt(sent)
            lines.append('{} -> {}'.format(line, pline))

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbd.result.txt'), lines)


if __name__ == '__main__':
    unittest.main()
