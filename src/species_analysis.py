'''
Analyse species itemsets
'''
import argparse
import joblib

import pandas as pd
import apriori

import apriori_sequential as asq
import helpers

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('minsup', help='Minimum support', nargs='?', type=float, default=0.8)
#parser.add_argument('minconf', help='Minimum confidence', nargs='?', type=float, default=0.8)
args = parser.parse_args()

itemsets = helpers.get_species_itemsets()
all_items = list(set([item for itemset in itemsets for item in itemset]))
print(len(itemsets))
print(len(all_items))

freq_items = apriori.apriori(itemsets, all_items, args.minsup, verbose=True)

print('\nSupport {:.3f} frequent itemsets:\n'.format(args.minsup))
print(len(freq_items))
print(freq_items[-1])

joblib.dump(freq_items, helpers.DATA_DIR + 'freq_species_itemsets_{:.3f}.pkl'.format(args.minsup))

