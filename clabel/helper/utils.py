# coding: utf-8

import pickle


def save_obj(obj, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)


def read_obj(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def read_file(file_path):
    lines = []
    with open(file_path, 'rb') as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def write_file(file_path, lines):
    with open(file_path, 'wb') as f:
        for line in lines:
            if line:
                f.write('%s\n' % line)


def iter_file(file_path):
    with open(file_path, 'rb') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def convert2unicode(s):
    if isinstance(s, unicode):
        return s

    elif isinstance(s, str):
        return s.decode('utf-8')

    return str(s).decode('utf-8')


def str2unicode(txt):
    if isinstance(txt, str):
        return txt.decode('utf-8')
    elif isinstance(txt, unicode):
        return txt
    else:
        return str(txt).decode('utf-8')


def unicode2str(txt):
    if isinstance(txt, str):
        return txt
    elif isinstance(txt, unicode):
        return txt.encode('utf-8')
    else:
        return str(txt)