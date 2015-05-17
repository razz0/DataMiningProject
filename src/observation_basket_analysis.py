'''
Analyse observation basket
'''
import argparse
import csv

import pandas as pd

import apriori

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('cores', help='How many CPU cores to use', type=int)
args = parser.parse_args()

apriori.NUM_CORES = args.cores


DATA_DIR = '../data/'
RESULT_DIR = '../results/'

MINSUP = 0.8

itemsets = []

with open(DATA_DIR + 'observation.basket.1') as csvfile:
    transaction_reader = csv.reader(csvfile, delimiter=',')
    for row in transaction_reader:
        itemsets.append(tuple(row))
#inducer = Orange.associate.AssociationRulesSparseInducer(support=minsup, store_examples=False, max_item_sets=10**7)
#itemsets = inducer.get_itemsets(data)

all_items = list(set([item for itemset in itemsets for item in itemset]))

print(len(itemsets))
print(len(all_items))
#print(itemsets[:1])

print('\nSupport %1f frequent itemsets:\n' % MINSUP)

max_itemset = (0, [])

#for itemset in itemsets:
#    if len(itemset[0]) > max_itemset[0]:
#        max_itemset = (len(itemset[0]), [])
#    if len(itemset[0]) == max_itemset[0]:
#        itemset_string = ', '.join([data.domain[i].name for i in itemset[0]])
#        max_itemset[1].append(itemset_string)

freq_items = apriori.apriori(itemsets, all_items, MINSUP, verbose=True)
print(freq_items)
print(len(freq_items))

# print('Found length %s frequent itemset(s)' % max_itemset[0])
#
# for itemset in max_itemset[1]:
#     print(itemset)
# #    print ', '.join([data.domain[i].name for i in itemset[0]]).decode('utf8')
#
# with open(RESULT_DIR + 'frequent_sets_minsup_%s.txt' % MINSUP, 'w') as f:
#     for itemset in max_itemset[1]:
#         f.write(itemset + "\n")
#
# print('\nFrequent generated rules (pajulintu -> x:)\n')
#
# rules = Orange.associate.AssociationRulesSparseInducer(data, support=0.35, confidence=0.35, max_item_sets=10**7)
#
# print("%5s   %5s   %5s" % ("supp", "conf", 'lift'))
#
# for r in rules:
# #    if r.n_left == 1 and r.n_right >= 5:
#     if str(r.left) == 'pajulintu':
#         print("%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r))
#
# with open(RESULT_DIR + 'association_rules_pajulintu.txt', 'w') as f:
#     for r in rules:
#         rule = "%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r)
#         f.write(rule + "\n")
#
# print('\nFrequent generated rules (suosirri -> x:)\n')
#
# for r in rules:
# #    if r.n_left == 1 and r.n_right >= 5:
#     if str(r.left) == 'suosirri':
#         print("%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r))
#
# for r in rules:
# #    if r.n_left == 1 and r.n_right >= 5:
#     if str(r.left) == 'haahka':
#         print("%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r))
#
#
