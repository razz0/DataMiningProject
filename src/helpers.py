'''
Helpers for data mining tasks.
'''

import csv, json

DATA_DIR = '../data/'


def read_observation_basket(filename):
    """
    Read observation itemsets from file.

    :param filename:
    """
    itemsets = []

    with open(filename) as csvfile:
        transaction_reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        for row in transaction_reader:
            itemsets.append(tuple(sorted(row)))

    return itemsets


def read_observation_sequences(filename):
    """
    Read observation sequences from file.

    :param filename:
    """
    with open(filename) as f:
        sequences = json.load(f)

    return sequences
