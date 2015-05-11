'''
Analyse observation basket
'''

DATA_DIR = '../data/'

import Orange

data = Orange.data.Table(DATA_DIR + 'observation.basket')
inducer = Orange.associate.AssociationRulesSparseInducer(support=0.4, store_examples=True)
itemsets = inducer.get_itemsets(data)

for itemset in itemsets:
    print ', '.join([data.domain[i].name for i in itemset[0]]).decode('utf8')
