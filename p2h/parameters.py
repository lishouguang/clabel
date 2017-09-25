# coding: utf-8

import os

from p2h.config import APP_RESOURCE_DIR


class Parameters:
    """App parameters"""
    # raw_corpus_file = os.path.join(APP_RESOURCE_DIR, 'corpus', 'raw.tiny.txt')
    # train_data_file = os.path.join(APP_RESOURCE_DIR, 'data', 'train.tiny.tsv')
    # vocab_data_file = os.path.join(APP_RESOURCE_DIR, 'data', 'vocab.tiny.pkl')

    raw_corpus_file = os.path.join(APP_RESOURCE_DIR, 'corpus', 'raw.txt')
    train_data_file = os.path.join(APP_RESOURCE_DIR, 'data', 'train.tsv')
    # vocab_data_file = os.path.join(APP_RESOURCE_DIR, 'data', 'vocab.pkl')
    vocab_data_file = os.path.join(APP_RESOURCE_DIR, 'data', 'vocab.json')

    logdir = os.path.join(APP_RESOURCE_DIR, "log")

    min_hanzi_count = 5

    """Hyper parameters"""
    # model
    embed_size = 300  # alias = E
    encoder_num_banks = 16
    num_highwaynet_blocks = 4
    maxlen = 50  # maximum number of a pinyin sentence
    minlen = 10  # minimum number of a pinyin sentence
    norm_type = "bn"  # Either "bn", "ln", "ins", or None
    dropout_rate = 0.5

    # training scheme
    lr = 0.0001
    batch_size = 200
    num_epochs = 20
    # batch_size = 1000
    # num_epochs = 30
