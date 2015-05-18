'''
Analyse observation basket
'''
import argparse
import joblib

import pandas as pd

import apriori_sequential as asq
import helpers

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('minsup', help='Minimum support', nargs='?', type=float, default=0.8)
parser.add_argument('minconf', help='Minimum confidence', nargs='?', type=float, default=0.8)
args = parser.parse_args()

NUM_CORES = 1

MINSUP = args.minsup
MINCON = args.minsup


year_seqs = helpers.get_yearly_sequences(prune_common_species=True)

print(year_seqs[5][0])
print(year_seqs[0][0])
print(year_seqs[-5][180])

freq_seqs = asq.apriori_sequential(year_seqs, MINSUP, verbose=True)

joblib.dump(freq_seqs, helpers.DATA_DIR + 'freq_seqs_{:.3f}.pkl'.format(MINSUP))

