# -*- coding: utf-8 -*-
""" Created by Cenk Bircanoğlu on 19/11/2016 """
import numpy as np
import operator
import os

import pandas as pd
from sklearn import cross_validation, neighbors
from sklearn import svm
from sklearn.neural_network.multilayer_perceptron import MLPClassifier

from confusion_matrix import create_confusion_matrix

__author__ = 'cenk'


def classify(data_path, path=None, counter=None, alg='svm'):
    print data_path
    fname = "{}/labels.csv".format(data_path)
    paths = pd.read_csv(fname, header=None).as_matrix()[:, 1]
    paths = map(os.path.basename, paths)  # Get the filename.
    # Remove the extension.
    paths = map(lambda x: x.split(".")[0], paths)
    paths = np.array(map(lambda path: os.path.splitext(path)[0], paths))

    fname = "{}/reps.csv".format(data_path)
    rawEmbeddings = pd.read_csv(fname, header=None).as_matrix()

    folds = cross_validation.KFold(n=len(rawEmbeddings), random_state=1, n_folds=10, shuffle=True)
    scores = []
    for idx, (train, test) in enumerate(folds):
        print idx
        if alg == 'knn':
            clf = neighbors.KNeighborsClassifier(1)
        elif alg == 'svm':
            clf = svm.SVC(kernel='linear', C=1)
        elif alg == 'nn':
            clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(18,), random_state=1)
        clf.fit(rawEmbeddings[train], paths[train])
        scores.append(clf.score(rawEmbeddings[test], paths[test]))
    accuracy_dir = os.path.abspath(os.path.join(data_path, 'accuracies_%s.txt' %alg))

    with open(accuracy_dir, "wb") as file:
        for i in scores:
            file.writelines("%s,%s\n" % (str(i), str(counter)))
    # print "KNN Avg. score %s" % (reduce(operator.add, scores) / len(folds))
    # print "MLP Avg. score %s" % (reduce(operator.add, scores3) / len(folds))
    print "Avg. score %s" % (reduce(operator.add, scores) / len(folds))
    result_path = "{}/{}_{}.log".format(os.path.abspath(os.path.join(os.path.join(data_path, os.pardir), os.pardir)),
                                        path, alg)
    with open(result_path, "a") as file:
        file.write("%s,\t%s\t%s\n" % (str((reduce(operator.add, scores) / len(folds))), str(counter), alg))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--trainDir', type=str)
    parser.add_argument('--testDir', type=str)
    parser.add_argument('--pathName', type=str)
    parser.add_argument('--train', type=int, default=0)
    parser.add_argument('--counter', type=int, default=0)
    parser.add_argument('--alg', type=str, default='svm')
    args = parser.parse_args()
    if not args.train:
        classify(args.testDir, path='%s_%s' % (args.pathName, 'test_score'), counter=args.counter, alg=args.alg)
    if args.train:
        classify(args.trainDir, path='%s_%s' % (args.pathName, 'train_score'), counter=args.counter, alg=args.alg)
        create_confusion_matrix(args.trainDir, args.testDir,
                                out_dir=os.path.abspath(os.path.join(args.trainDir)), path_name=args.pathName,
                                counter=args.counter, alg=args.alg)
