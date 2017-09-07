# coding: utf-8

import os
import unittest

import numpy as np

from collections import defaultdict

from sklearn import metrics

from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_similarity

from clabel.helper import utils
from clabel.config import RESOURCE_DIR
from clabel.model import word2vec as w2c


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_cluster_kmean(self):
        self.assertTrue(True)

        model = w2c.get()

        features, X = get_features_X(model)

        n_clusters = 200
        kmean = KMeans(n_clusters=n_clusters)
        labels = kmean.fit_predict(X)

        centers = kmean.cluster_centers_

        cluster_features = defaultdict(list)
        cluster_X = defaultdict(list)
        cluster_centers = dict()

        for f, l, x in zip(features, labels, X):
            cluster_features[l].append(f)
            cluster_X[l].append(x)

        for l, x in cluster_X.items():
            i = np.argmax(cosine_similarity(centers[l], cluster_X[l]))
            cluster_centers[l] = cluster_features[l][i]

        with open(os.path.join(os.path.join(RESOURCE_DIR, 'cluster', 'cluster.txt')), 'wb') as f:
            for label in cluster_features:
                f.write('%s --- %s\n' % (cluster_centers[label], ' '.join(cluster_features[label])))

    def test_cluster_h(self):
        self.assertTrue(True)

        model = w2c.get()

        features, X = get_features_X(model)
        for f in features:
            print f

    def test_ap_features(self):
        self.assertTrue(True)

        from collections import defaultdict

        model = w2c.get()

        features, X = get_features_X(model)

        # preference是小于0的值。值越大，聚类数就越多。
        ap = AffinityPropagation(preference=-30)
        labels = ap.fit_predict(X)

        centers = dict()
        for label, index in enumerate(ap.cluster_centers_indices_):
            centers[label] = features[index]

        clusters = defaultdict(set)
        for label, feature in zip(labels, features):
            clusters[label].add(feature)

        for label in centers:
            print '%s --- %s' % (centers[label], ' '.join(clusters[label]))

    def test_ap_features2(self):
        self.assertTrue(True)

        model = w2c.get()

        features, X = get_features_X(model)

        ap = AffinityPropagation(preference=-50)
        labels = ap.fit_predict(X)

        n_cluster = len(ap.cluster_centers_indices_)
        print 'n_cluster: ', n_cluster

        # for c in ap.cluster_centers_indices_:
        #     print c, features[c]

        # 绘制图表展示
        import matplotlib.pyplot as plt
        from itertools import cycle
        from sklearn.manifold import TSNE

        plt.close('all')  # 关闭所有的图形
        plt.figure(1)  # 产生一个新的图形
        plt.clf()  # 清空当前的图形

        colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
        colors = [c for _, c in zip(range(n_cluster), colors)]
        print len(colors)
        print colors

        tsne = TSNE(n_components=2)
        X_2d = tsne.fit_transform(X)

        for x, l in zip(X_2d, labels):
            plt.scatter(x[0], x[1], c=colors[l])

        '''
        for k, col in zip(range(n_cluster), colors):
            plt.scatter()

        for k, col in zip(range(n_cluster), colors):
            # labels == k 使用k与labels数组中的每个值进行比较
            # 如labels = [1,0],k=0,则‘labels==k’的结果为[False, True]

            class_members = labels == k
            cluster_center = X_2d[ap.cluster_centers_indices_[k]]  # 聚类中心的坐标

            plt.plot(X_2d[class_members, 0], X_2d[class_members, 1], col + '.')
            plt.plot(cluster_center[0], cluster_center[1], markerfacecolor=col,
                     markeredgecolor='k', markersize=14)
            for x in X_2d[class_members]:
                plt.plot([cluster_center[0], x[0]], [cluster_center[1], x[1]], col)
        '''

        plt.title('预测聚类中心个数：%d' % n_cluster)
        plt.show()

    def test_dbscan(self):
        self.assertTrue(True)

        features, X = get_features_X(w2c.get())

        X = cosine_similarity(X)

        eps = 0.5
        dbscan = DBSCAN(metric='precomputed', eps=eps)

        labels = dbscan.fit_predict(X)
        print labels
        print 'eps: %f, n_cluster: %d' % (eps, len(set(labels)))

    def test_my_cluster(self):
        self.assertTrue(True)

        from clabel.pipeline import cluster

        features = get_features()
        cluster.create(features)


def get_features_X(model):
    features = get_features()
    features = filter_features(features, model)
    X = get_X(features, model)
    return features, X


def get_features():
    # fcounter = utils.read_obj(os.path.join(RESOURCE_DIR, 'dp', 'feature.counter'))
    # return [f for f in fcounter if fcounter[f] > 1]

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
