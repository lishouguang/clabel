# coding: utf-8

import os
import unittest
from collections import defaultdict

import openpyxl

from clabel.config import RESOURCE_DIR


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_read(self):
        self.assertTrue(True)

        excel_file = os.path.join(RESOURCE_DIR, 'general', '情感词汇本体.xlsx')
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active

        polar_map = {
            0: 'neu',
            1: 'pos',
            2: 'neg',
            3: 'two'
        }

        words = defaultdict(set)

        i = 0
        for row in list(sheet.rows)[1:]:
            i += 1

            main_polar = row[6].value
            aux_polar = row[9].value

            if aux_polar is None or main_polar == aux_polar:
                words[polar_map.get(main_polar, 3)].add(row[0].value)

        for word in words['neg']:
            print(word)


if __name__ == '__main__':
    unittest.main()
