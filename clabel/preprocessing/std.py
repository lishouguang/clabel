# coding: utf-8

import re
import os

from lm.lm import LM
from lm.lm import HanziLM
from lm.config import LM_MODEL_DIR

from sbd.sbd import SBDModel
from sbd.config import APP_RESOURCE_DIR as SBD_DIR

from wed.wed2 import correct


hanzi_model_file = os.path.join(LM_MODEL_DIR, 'hanzi.arpa')
pnyin_model_file = os.path.join(LM_MODEL_DIR, 'pinyin.arpa')
# lmModel = LM(hanzi_model_file, pnyin_model_file)
hanziLM = HanziLM(hanzi_model_file)

sbdModel = SBDModel.load(keras_model_file=os.path.join(SBD_DIR, 'sbd.keras.model'))


def extract_txt(txt):
    words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', txt)
    return ''.join(words)


def sbd(txt):
    sbd_txt = sbdModel.predict_txt(txt)
    return sbd_txt


def prob(txt):
    return hanziLM.predict_prob(txt)


def wed(txt):
    txt = ''.join(re.findall(r'[\u4e00-\u9fa5，。？！?,]', txt))
    ctxt = correct(txt)
    return ctxt


