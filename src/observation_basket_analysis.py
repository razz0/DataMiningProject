'''
Analyse observation basket
'''

DATA_DIR = '../data/'
RESULT_DIR = '../results/'

import Orange

minsup = 0.5

data = Orange.data.Table(DATA_DIR + 'observation.basket')
inducer = Orange.associate.AssociationRulesSparseInducer(support=minsup, store_examples=False, max_item_sets=10**7)
itemsets = inducer.get_itemsets(data)

print('\nSupport %1f frequent itemsets:\n' % minsup)

max_itemset = (0, [])

for itemset in itemsets:
    if len(itemset[0]) > max_itemset[0]:
        max_itemset = (len(itemset[0]), [])
    if len(itemset[0]) == max_itemset[0]:
        itemset_string = ', '.join([data.domain[i].name for i in itemset[0]])
        max_itemset[1].append(itemset_string)

print 'Found length %s frequent itemset(s)' % max_itemset[0]

for itemset in max_itemset[1]:
    print itemset
#    print ', '.join([data.domain[i].name for i in itemset[0]]).decode('utf8')

with open(RESULT_DIR + 'frequent_sets_minsup_%s.txt' % minsup, 'w') as f:
    for itemset in max_itemset[1]:
        f.write(itemset + "\n")

print('\nFrequent generated rules (pajulintu -> x:)\n')

rules = Orange.associate.AssociationRulesSparseInducer(data, support=0.35, confidence=0.35, max_item_sets=10**7)

print "%5s   %5s   %5s" % ("supp", "conf", 'lift')

for r in rules:
#    if r.n_left == 1 and r.n_right >= 5:
    if str(r.left) == 'pajulintu':
        print "%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r)

with open(RESULT_DIR + 'association_rules_pajulintu.txt', 'w') as f:
    for r in rules:
        rule = "%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r)
        f.write(rule + "\n")

print('\nFrequent generated rules (suosirri -> x:)\n')

for r in rules:
#    if r.n_left == 1 and r.n_right >= 5:
    if str(r.left) == 'suosirri':
        print "%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r)

for r in rules:
#    if r.n_left == 1 and r.n_right >= 5:
    if str(r.left) == 'haahka':
        print "%5.3f   %5.3f   %5.3f   %s" % (r.support, r.confidence, r.lift, r)


