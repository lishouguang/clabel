# coding: utf-8

import os
import unittest

from matplotlib import pyplot as plot
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from clabel.helper import utils
from clabel.config import RESOURCE_DIR


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_scatter_features(self):
        self.assertTrue(True)

        from clabel.model import word2vec as w2c

        model = w2c.get()
        features, X = get_features_X(model)

        tsne = TSNE(n_components=2)
        X_2d = tsne.fit_transform(X)

        plot.scatter(X_2d[:, 0], X_2d[:, 1])
        plot.show()


def get_features_X(model):
    features = get_features()
    features = filter_features(features, model)
    X = get_X(features, model)
    return features, X


def get_features():
    F = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'dp.F'))
    return list(F)


def filter_features(features, model):
    filtered_features = []

    for f in features:
        if f.find('_') != -1:
            word1, word2 = f.split('_')
            if word1 in model.vocab and word2 in model.vocab:
                filtered_features.append(f)

        elif f in model.vocab:
            filtered_features.append(f)

    return filtered_features


def get_X(features, model):
    X = []
    for f in features:
        if f.find('_') == -1:
            X.append(model[f])
        else:
            word1, word2 = f.split('_')
            X.append((model[word1] + model[word2]) / 2)

    return X


if __name__ == '__main__':
    unittest.main()
