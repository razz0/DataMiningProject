# coding=utf-8
import math

import apriori as a


class RuleGenerator(object):

    def __init__(self, transactions, frequent_itemsets):
        self.transactions = transactions
        self.frequent_itemsets = frequent_itemsets
        self.N = len(transactions)

    def _ap_genrules(self, k_itemset, consequents):
        """
        :param frequent_k_itemsets:
        :param consequents:
        """
        k = len(k_itemset)
        m = len(consequents[0])

        if k > m + 1:
            new_consequents = a._apriori_gen(consequents)
            # TODO: Prune for better speed
            #for new_con in new_consequents:
            #    pass

    def confidence(self, antecedent, consequent):
        ant_sup = a.support_count(antecedent, self.transactions)
        if ant_sup == 0:
            return 0

        return a.support_count(list(set(antecedent) | set(consequent)), self.transactions) / float(ant_sup)

    def support(self, antecedent, consequent):
        N = len(self.transactions)
        if N == 0:
            return 0

        return a.support_count(list(set(antecedent) | set(consequent)), self.transactions) / float(N)

    def lift(self, antecedent, consequent):
        sup = a.support_count(antecedent, self.transactions) * a.support_count(consequent, self.transactions)
        if sup == 0:
            return 0

        # return self.confidence(antecedent, consequent) / float(sup)
        return self.N * a.support_count(list(set(antecedent) | set(consequent)), self.transactions) / float(sup)

    def IS_measure(self, antecedent, consequent):
        denominator = math.sqrt(a.get_support(antecedent, self.transactions) * a.get_support(consequent, self.transactions))
        if denominator == 0:
            return 0

        return a.get_support(list(set(antecedent) | set(consequent)), self.transactions) / denominator

    def rule_generation(self, minconf, itemsets=None, maxconf=None, fixed_consequents=(), verbose=False):
        """
        Generate rules ({A, B} -> {C}) from frequent itemsets
        """
        rules = []

        sets = itemsets or self.frequent_itemsets

        for i, itemset in enumerate(sets):
            candidates = [(item,) for item in itemset]
            if verbose:
                print('%s initial candidates for itemset %i of %i' % (len(candidates), i, len(sets)))

            while candidates:
                good_candidates = []
                for x in candidates:
                    consequent = list(set(itemset) - set(x))
                    conf = self.confidence(x, consequent)

                    # TODO: Refactor structure (is minconf working?)

                    if consequent and conf >= minconf and (not maxconf or conf <= maxconf):
                        if (fixed_consequents and set(consequent) & set(fixed_consequents)) \
                                or not fixed_consequents:
                            rules.append({(x, tuple(consequent)): (conf,
                                                                   self.support(x, consequent),
                                                                   self.lift(x, consequent),
                                                                   self.IS_measure(x, consequent))})
                            if verbose:
                                print('found rule %s -> %s' % (x, tuple(consequent)))
                        good_candidates.append(x)

                candidates = a._apriori_gen(good_candidates)

        if verbose:
            print('Found %i frequent rules' % (len(rules)))

        return rules
