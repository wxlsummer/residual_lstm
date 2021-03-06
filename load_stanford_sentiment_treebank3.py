import csv
import os
import pickle
import gensim
# from gensim.models import Doc2Vec
import re
# from save_data import dump_picle
import numpy as np


def load_sst(path=None, level=None):
    filename = 'sst.p'
    if os.path.isfile(filename):
        print('Load OK.')
        return load_pickle(filename)

    def cleanStr(string):
        string = re.sub(r'^A-Za-z0-9(),!?\'\`', ' ', string)
        string = re.sub(r'\s{2,}', ' ', string)
        string = string.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã±', 'ñ').replace('Â', '').replace('Ã¯', 'ï')
        string = string.replace('Ã¼', 'ü').replace('Ã¢', 'â').replace('Ã¨', 'è').replace('Ã¶', 'ö').replace('Ã¦', 'æ')
        string = string.replace('Ã³', 'ó').replace('Ã»', 'û').replace('Ã´', 'ô').replace('Ã£', 'ã').replace('Ã§', 'ç')
        string = string.replace('Ã ', 'à ').replace('Ã', 'í').replace('í­', 'í')
        return string

    # sentiment label
    sentiment_file = open(path + 'sentiment_labels.txt', 'r')
    sentiment_label = {}
    n = 0
    for line in sentiment_file:
        lines = line.strip().split('|')
        if n > 0:
            sentiment_label[int(lines[0])] = float(lines[1])
        n += 1
    sentiment_file.close()

    # phrase dict
    dict_file = open(path + 'dictionary.txt', 'r')
    phrase_dict = {}
    for line in dict_file:
        # line = line.decode('utf-8')
        lines = line.strip().split('|')
        phrase_dict[lines[0]] = int(lines[1])
    dict_file.close()

    # sentence dict
    sentence_file = open(path + 'datasetSentences.txt', 'r')
    sentence_dict = {}
    n = 0
    for line in sentence_file:
        # line = line.decode('utf-8')
        line = line.replace('-LRB-', '(')
        line = line.replace('-RRB-', ')')
        lines = line.strip().split('\t')
        if n > 0:
            sentence_dict[int(lines[0])] = lines[1]
        n += 1
    sentence_file.close()

    # datasplit
    datasplit_file = open(path + 'datasetSplit.txt', 'r')
    split_dict = {}
    n = 0
    for line in datasplit_file:
        lines = line.strip().split(',')
        if n > 0:
            split_dict[int(lines[0])] = int(lines[1])
        n += 1
    datasplit_file.close()

    size = len(sentence_dict)  # size = 11855
    # for i in range(1000):
    #     senti = sentiment_label[phrase_dict[cleanStr(sentence_dict[i + 1])]]
    #     print(i, senti, cleanStr(sentence_dict[i + 1]))
    # exit()
    x_train, y_train_valence, y_train_labels = [], [], []
    x_test, y_test_valence, y_test_labels = [], [], []
    x_valid, y_valid_valence, y_valid_labels = [], [], []

    x_train_polarity, y_train_polarity = [], []
    x_test_polarity, y_test_polarity = [], []
    x_valid_polarity, y_valid_polarity = [], []

    for i in range(size):
        # print sentence_dict[i+1].encode('utf-8')
        sentence = cleanStr(sentence_dict[i + 1])
        senti = sentiment_label[phrase_dict[sentence]]

        # print(senti, sentence)
        labels, polarity = None, None
        if 0 <= senti <= 0.2:
            labels = 1
            polarity = 0
        if 0.2 < senti <= 0.4:
            labels = 2
            polarity = 0
        if 0.4 < senti <= 0.6:
            labels = 3
        if 0.6 < senti <= 0.8:
            labels = 4
            polarity = 1
        if 0.8 < senti <= 1:
            labels = 5
            polarity = 1
        if labels is None:
            raise Exception('Sentiment Error !')

        if split_dict[i + 1] == 1:
            x_train.append(sentence)
            y_train_valence.append(senti)
            y_train_labels.append(labels)
            if polarity is not None:
                x_train_polarity.append(sentence)
                y_train_polarity.append(polarity)
        elif split_dict[i + 1] == 2:
            x_test.append(sentence)
            y_test_valence.append(senti)
            y_test_labels.append(labels)
            if polarity is not None:
                x_test_polarity.append(sentence)
                y_test_polarity.append(polarity)
        else:
            x_valid.append(sentence)
            y_valid_valence.append(senti)
            y_valid_labels.append(labels)
            if polarity is not None:
                x_valid_polarity.append(sentence)
                y_valid_polarity.append(polarity)

    print("Fine-grained: #training: %s, #valid: %s, #test: %s" % (len(x_train), len(x_valid), len(x_test)))
    print("Binary classification: #train: %s, #valid: %s, #test: %s" % (
        len(x_train_polarity), len(x_valid_polarity), len(x_test_polarity)))

    # t = zip(x_train, y_train)
    # random.shuffle(t)
    # x_train, y_train = zip(*t)
    output = (x_train, y_train_valence, y_train_labels,
              x_test, y_test_valence, y_test_labels,
              x_valid, y_valid_valence, y_valid_labels,
              x_train_polarity, y_train_polarity,
              x_test_polarity, y_test_polarity,
              x_valid_polarity, y_valid_polarity)
    pickle.dump(output, filename)
    print('Data saved and load successfully.')
    return output

load_sst(path=os.path.join('corpus', 'stanford_sentiment_treebank') + '\\')