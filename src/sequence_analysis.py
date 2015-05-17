'''
Analyse observation basket
'''
import argparse
import joblib

import pandas as pd

import apriori_sequential
import helpers

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('minsup', help='Minimum support', nargs='?', type=float, default=0.8)
parser.add_argument('minconf', help='Minimum confidence', nargs='?', type=float, default=0.8)
args = parser.parse_args()

NUM_CORES = 1

MINSUP = args.minsup
MINCON = args.minsup

sequences = helpers.read_observation_sequences(helpers.DATA_DIR + 'observation.sequence')

#all_items = list(set([item for itemset in itemsets for item in itemset]))

print(len(sequences))
print(list(sequences.items())[0])

year_seqs = []
for year in range(1979, 2009):
    good_keys, good_seqs = zip(*[(date, obs) for date, obs in sequences.items() if date.startswith(str(year))])

    year_seqs.append([species for seq in good_seqs for species, _, _ in seq])
    print(len(good_keys))

print(year_seqs[5])

#joblib.dump(freq_items, DATA_DIR + 'freq_items_{:.3f}.pkl'.format(MINSUP))

