"""
Data loading.
Note:
Nine key pinyin keyboard layout sample:

`      ABC   DEF
GHI    JKL   MNO
POQRS  TUV   WXYZ

"""
import re
import json
import pickle
import codecs
import logging

import numpy as np

import tensorflow as tf

from p2h.parameters import Parameters as P

logger = logging.getLogger(__file__)


def load_vocab():
    with open(P.vocab_data_file, 'rb') as f:

        if P.vocab_data_file.endswith('.pkl'):
            return pickle.load(f)

        elif P.vocab_data_file.endswith('.json'):
            pnyn2idx, idx2pnyn, hanzi2idx, idx2hanzi = json.load(f)

            idxs = [_ for _ in idx2hanzi.keys()]
            for idx in idxs:
                idx2hanzi[int(idx)] = idx2hanzi[idx]

            idxs = [_ for _ in idx2pnyn.keys()]
            for idx in idxs:
                idx2pnyn[int(idx)] = idx2pnyn[idx]

            return pnyn2idx, idx2pnyn, hanzi2idx, idx2hanzi


def load_train_data():
    """Loads vectorized input training data"""
    pnyn2idx, idx2pnyn, hanzi2idx, idx2hanzi = load_vocab()

    logger.info("pnyn vocabulary size is", len(pnyn2idx))
    logger.info("hanzi vocabulary size is", len(hanzi2idx))

    xs, ys = [], []
    with codecs.open(P.train_data_file, 'r', 'utf-8') as fin, codecs.open('t', 'w', 'utf-8') as fout:
        for l, line in enumerate(fin):

            if l % 10000 == 0:
                logger.info(l)

            try:
                pnyn_sent, hanzi_sent = line.strip().split("\t")
            except ValueError:
                continue

            pnyn_sents = re.sub(u"(?<=([。，！？]))", r"|", pnyn_sent).split("|")
            hanzi_sents = re.sub(u"(?<=([。，！？]))", r"|", hanzi_sent).split("|")

            fout.write(pnyn_sent + "===" + "|".join(pnyn_sents) + "\n")

            for pnyn_sent, hanzi_sent in zip(pnyn_sents+[pnyn_sent], hanzi_sents+[hanzi_sent]):

                assert len(pnyn_sent) == len(hanzi_sent)

                if P.minlen < len(pnyn_sent) <= P.maxlen:
                    x = [pnyn2idx.get(pnyn, 1) for pnyn in pnyn_sent] # 1: OOV
                    y = [hanzi2idx.get(hanzi, 1) for hanzi in hanzi_sent] # 1: OOV

                    xs.append(np.array(x, np.int32).tostring())
                    ys.append(np.array(y, np.int32).tostring())
    return xs, ys


def load_test_data():
    '''Embeds and vectorize words in input corpus'''
    try:
        lines = [line for line in codecs.open('eval/input.csv', 'r', 'utf-8').read().splitlines()[1:]]
    except IOError:
        raise IOError("Write the sentences you want to test line by line in `data/input.csv` file.")

    pnyn2idx, _, hanzi2idx, _ = load_vocab()

    nums, xs, ys = [], [], [] # ys: ground truth (list of string)
    for line in lines:
        num, pnyn_sent, y = line.split(",")

        nums.append(num)
        x = [pnyn2idx.get(pnyn, 1) for pnyn in pnyn_sent]  # 1: OOV
        x += [0] * (P.maxlen - len(x))
        xs.append(x)
        ys.append(y)

    X = np.array(xs, np.int32)
    return nums, X, ys

def load_test_string(pnyn2idx, test_string):
    '''Embeds and vectorize words in user input string'''
    pnyn_sent= test_string
    xs = []
    x = [pnyn2idx.get(pnyn, 1) for pnyn in pnyn_sent]
    x += [0] * (P.maxlen - len(x))
    xs.append(x)
    X = np.array(xs, np.int32)
    return X


def get_batch():
    """Makes batch queues from the training data.
    Returns:
      A Tuple of x (Tensor), y (Tensor).
      x and y have the shape [batch_size, maxlen].
    """

    # Load data
    X, Y = load_train_data()

    # Create Queues
    x, y = tf.train.slice_input_producer([tf.convert_to_tensor(X),
                                          tf.convert_to_tensor(Y)])

    x = tf.decode_raw(x, tf.int32)
    y = tf.decode_raw(y, tf.int32)

    x, y = tf.train.batch([x, y],
                          shapes=[(None,), (None,)],
                          num_threads=8,
                          batch_size=P.batch_size,
                          capacity=P.batch_size * 64,
                          allow_smaller_final_batch=False,
                          dynamic_pad=True)
    num_batch = len(X) // P.batch_size

    return x, y, num_batch  # (N, None) int32, (N, None) int32, ()