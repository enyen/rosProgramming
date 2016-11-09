from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import random
from tensorflow.contrib.learn.python.learn.datasets import base
random.seed()


class DataSet(object):

    def __init__(self,
                 data,
                 label,
                 len_back,
                 len_front):
        self._data = data
        self._label = label
        self._back = len_back
        self._front = len_front
        self._epochs_completed = 0
        self._index_in_epoch = 0
        self._num_examples = data.shape[0]

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        if self._index_in_epoch > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._data = self._data[perm]
            self._label = self._label[perm]
            # Start next epoch
            start = 0
            self._index_in_epoch = batch_size
            assert batch_size <= self._num_examples
        end = self._index_in_epoch
        return self._data[start:end], self._label[start:end]


def read_data_sets(len_back, len_front, test_size=1000):
    data_file = 'traj_data.npy'
    label_file = 'traj_label.npy'
    data = np.load(data_file)
    label = np.load(label_file)

    train_data = data[:(data.shape[0] - test_size)]
    test_data = data[(data.shape[0] - test_size):]
    train_label = label[:(label.shape[0] - test_size)]
    test_label = label[(label.shape[0] - test_size):]

    train = DataSet(train_data, train_label, len_back, len_front)
    test = DataSet(test_data, test_label, len_back, len_front)
    validate = DataSet(test_data, test_label, len_back, len_front)

    return base.Datasets(train=train, test=test, validation=validate)


def produce_data(len_back, len_front, order):
    local_file = 'trajactory2.txt'
    with open(local_file, 'rb') as f:
        raw_data = []
        for line in f:
            raw_data.append(line.split())

    train_data = []
    train_label = []
    for idx in range(len_back, (len(raw_data)-len_front)):
        data = np.asarray(np.asarray(raw_data[(idx - len_back):(idx + len_front)], dtype=np.float32))
        # for x
        data[:len_back] = data[:len_back] - np.mean(data[:len_back], axis=0)
        data[:len_back] = data[:len_back] / np.std(data[:len_back], axis=0)
        # for y
        data[len_back:] = data[len_back:] - np.mean(data[len_back:], axis=0)
        data[len_back:] = data[len_back:] / np.std(data[len_back:], axis=0)

        train_data.append(np.reshape(data[:len_back], -1))

        X = np.zeros([len_front, order + 1])
        Y = np.zeros([len_front, 2])
        for i in range(0, len_front):
            for j in range(0, order + 1):
                X[i, j] = np.power(data[(len_back + i), 0], j)
            Y[i, 0] = data[(len_back + i), 1]
            Y[i, 1] = data[(len_back + i), 2]
        temp = np.linalg.solve(X.transpose().dot(X), X.transpose())
        train_label.append(np.reshape(temp.dot(Y), -1))

    data_file = 'traj_data'
    label_file = 'traj_label'
    np.save(data_file, np.asarray(train_data))
    np.save(label_file, np.asarray(train_label))


# def produce_data(len_back, len_front, order):
#     local_file = 'trajactory2.txt'
#     with open(local_file, 'rb') as f:
#         raw_data = []
#         for line in f:
#             raw_data.append(line.split())
#
#     train_data = []
#     train_label = []
#     for idx in range(len_back, (len(raw_data)-len_front)):
#         data = np.asarray(np.asarray(raw_data[(idx - len_back):(idx + len_front)], dtype=np.float32))
#         # for x
#         data[:len_back] = data[:len_back] - np.mean(data[:len_back], axis=0)
#         data[:len_back] = data[:len_back] / np.std(data[:len_back], axis=0)
#         # for y
#         data[len_back:] = data[len_back:] - np.mean(data[len_back:], axis=0)
#         data[len_back:] = data[len_back:] / np.std(data[len_back:], axis=0)
#
#         train_data.append(np.reshape(data[:len_back], -1))
#         train_label.append(np.reshape(data[len_back:], -1))
#
#     data_file = 'traj_data'
#     label_file = 'traj_label'
#     np.save(data_file, np.asarray(train_data))
#     np.save(label_file, np.asarray(train_label))

