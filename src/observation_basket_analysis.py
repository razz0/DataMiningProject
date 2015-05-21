'''
Analyse observation basket
'''
import argparse
import joblib

import pandas as pd

import apriori
import helpers
from rules import RuleGenerator

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('minsup', help='Minimum support', nargs='?', type=float, default=0.8)
args = parser.parse_args()

apriori.NUM_CORES = 1


MINSUP = args.minsup

itemsets = helpers.read_observation_basket(helpers.DATA_DIR + 'observation.basket')

all_items = list(set([item for itemset in itemsets for item in itemset]))

print(len(itemsets))
print(len(all_items))
#print(itemsets[:1])

print('\nSupport {:.3f} frequent itemsets:\n'.format(MINSUP))

freq_items = apriori.apriori(itemsets, all_items, MINSUP, verbose=True)

print(freq_items[-1])
print(len(freq_items))

joblib.dump(freq_items, helpers.DATA_DIR + 'freq_items_{:.3f}.pkl'.format(MINSUP))

ruler = RuleGenerator(itemsets, freq_items)

rules = ruler.rule_generation(0.5) #, fixed_consequents=[('varis',)])

print(len(rules))

joblib.dump(rules, helpers.DATA_DIR + 'freq_rules_{:.3f}.pkl'.format(MINSUP))

#for (rule, conf) in rules:
#    print(' -> %s \t conf: {:.2f} \t supp: {:.3f}'.format(conf, ruler.support(*rule)))