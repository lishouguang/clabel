# coding: utf-8

import os
import logging
import numpy as np
from collections import defaultdict

from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_similarity

from clabel.config import RESOURCE_DIR
from clabel.model import word2vec as w2c

logger = logging.getLogger(__file__)


def create(features, model, preference=-30):

    features = filter_features(features, model)
    X = get_X(features, model)

    # preference是小于0的值。值越大，聚类数就越多。
    ap = AffinityPropagation(preference=preference)
    labels = ap.fit_predict(X)

    centers = dict()
    for label, index in enumerate(ap.cluster_centers_indices_):
        centers[label] = features[index]

    clusters = defaultdict(set)
    for label, feature in zip(labels, features):
        clusters[centers[label]].add(feature)

    # 去除只有一个词的类
    for cls in list(clusters.keys()):
        if len(clusters[cls]) == 1:
            del clusters[cls]

    return clusters


def create2(features, n_clusters=200):
    logger.info('cluster features...')

    model = w2c.get()

    features = filter_features(features, model)
    X = get_X(features, model)

    kmean = KMeans(n_clusters=n_clusters)
    labels = kmean.fit_predict(X)

    centers = kmean.cluster_centers_

    cluster_features = defaultdict(list)
    cluster_X = defaultdict(list)
    cluster_centers = dict()

    for f, l, x in zip(features, labels, X):
        cluster_features[l].append(f)
        cluster_X[l].append(x)

    for l, x in list(cluster_X.items()):
        i = np.argmax(cosine_similarity(centers[l], cluster_X[l]))
        cluster_centers[l] = cluster_features[l][i]

    with open(os.path.join(os.path.join(RESOURCE_DIR, 'cluster', 'cluster.txt')), 'wb') as f:
        for label in cluster_features:
            f.write('%s --- %s\n' % (cluster_centers[label], ' '.join(cluster_features[label])))

    return cluster_features


# def get_features_X(model):
#     # features = get_features()
#     features = filter_features(features, model)
#     X = get_X(features, model)
#     return features, X


# def get_features():
#     fcounter = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'feature.counter'))
#     return [f for f in fcounter if fcounter[f] > 1]


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
