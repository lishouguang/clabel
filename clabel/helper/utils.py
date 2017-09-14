# coding: utf-8

import codecs
import pickle


def save_obj(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)


def read_obj(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def read_file(file_path):
    lines = []
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def write_file(file_path, lines):
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write('%s\n' % line)


def iter_file(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line
