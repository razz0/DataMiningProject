"""Implementation of The Apriori algorithm, F(k-1) x F(k-1) variant."""

from collections import defaultdict
import itertools

from joblib import Parallel, delayed


NUM_CORES = 1

# TODO:
#   - use Numpy arrays where possible
#   - after that, another try at multiprocessing


def support_count(itemset, transactions):
    """
    Count support count for itemset

    :param itemset: items to measure support count for
    :param transactions: list of sets (all transactions)

    >>> simple_transactions = ['ABC', 'BC', 'BD', 'D']
    >>> [support_count(item, simple_transactions) for item in 'ABCDE']
    [1, 3, 2, 2, 0]
    >>> some_transactions = [set(['beer', 'bread', 'milk']), set(['beer']), set(['milk'])]
    >>> support_count(set(['beer']), some_transactions)
    2
    """
    return len([row for row in transactions if set(itemset) <= set(row)])


def get_support(itemset, transactions):
    return support_count(itemset, transactions) / float(len(transactions))


def _apriori_gen(frequent_sets):
    """
    Generate candidate itemsets

    :param frequent_sets: list of tuples, containing frequent itemsets [ORDERED]

    >>> _apriori_gen([('A',), ('B',), ('C',)])
    [('A', 'B'), ('A', 'C'), ('B', 'C')]
    >>> _apriori_gen([('A', 'B'), ('A', 'C'), ('B', 'C')])
    [('A', 'B', 'C')]
    >>> _apriori_gen([tuple(item) for item in ['ABC', 'ABD', 'ABE', 'ACD', 'BCD', 'BCE', 'CDE']])
    [('A', 'B', 'C', 'D'), ('A', 'B', 'C', 'E'), ('A', 'B', 'D', 'E'), ('B', 'C', 'D', 'E')]
    >>> cc = [('55015', '55314'), ('55015', '55315'), ('55314', '55315'), ('57016', '57017'), ('57043', '57047'), ('581325', '582103')]
    >>> _apriori_gen(cc)
    [('55015', '55314', '55315')]
    """

    # Sanity check for the input
    errors = [freq for freq in frequent_sets if sorted(list(set(freq))) != sorted(list(freq))]
    assert not errors, errors

    assert sorted(list(set(frequent_sets))) == sorted(frequent_sets), \
        set([(x, frequent_sets.count(x)) for x in frequent_sets if frequent_sets.count(x) > 1])

    new_candidates = []
    for index, frequent_item in enumerate(frequent_sets):
        for next_item in frequent_sets[index + 1:]:
            if len(frequent_item) == 1:
                new_candidates.append(tuple(frequent_item) + tuple(next_item))
            elif frequent_item[:-1] == next_item[:-1]:
                new_candidates.append(tuple(frequent_item) + (next_item[-1],))
            else:
                break

    return new_candidates


def _apriori_prune(candidates, transactions, k, frequent_itemsets, minsup):
    """
    Prune candidate itemsets

    :param candidates: candidate itemsets
    :param transactions:
    :param k:
    :param frequent_itemsets: list of lists of frequent itemsets grouped by k
    :param minsup: minimum support
    """

    # Validate some inputs
    assert not [cand for cand in candidates if len(cand) != k]

    # Check that items are unique
    errors = [cand for cand in candidates if sorted(list(set(cand))) != sorted(list(cand))]
    assert not errors, errors

    N = len(transactions)

    pruned_candidates = candidates
    support = defaultdict(int)

    for t in transactions:
        candidate_sets = pruned_candidates  # Remove the already pruned ones
        for candset in candidate_sets:
            subsets = generate_transaction_subsets(candset, k - 1)
            for subset in subsets:
                if subset not in frequent_itemsets[len(subset)]:
                    # This candidate is not frequent
                    pruned_candidates.remove(candset)
                    break
            else:
                if all(candidate in t for candidate in candset):
                    support[candset] += 1

    pruned_candidates = [item for item in pruned_candidates if support[item] >= N * minsup]

    return pruned_candidates


def generate_transaction_subsets(transaction, k):
    """
    Get subsets of transactions of length k

    >>> generate_transaction_subsets(['A', 'B', 'C', 'D', 'E'], 4)
    [('A', 'B', 'C', 'D'), ('A', 'B', 'C', 'E'), ('A', 'B', 'D', 'E'), ('A', 'C', 'D', 'E'), ('B', 'C', 'D', 'E')]

    :param transaction: list
    :param k: int
    :return:
    """
    subsets = []

    if k == 1:
        return [(t,) for t in transaction]

#    elif k > len(transaction):
#        return []

#    elif k == len(transaction):
#        return [tuple(transaction)]

    elif k == len(transaction) - 1:
        for i in reversed(list(range(0, len(transaction)))):
            subset = tuple(transaction[:i] + transaction[i + 1:])
            subsets.append(subset)

    else:
        raise Exception('Trying to generate length %s subset of %s' % (k, transaction))
#        for i in range(0, len(transaction) - (k - 1)):
#            for t in generate_transaction_subsets(transaction[i + 1:], k - 1):
#                subset = (transaction[i],) + t
#                subsets.append(subset)

    return subsets


def apriori(transactions, all_items, minsup, fixed_k=None, verbose=False):
    """
    Apriori method

    :param transactions: list of iterables (list of transactions containing items)
    :param all_items: list distinct items
    :param minsup: minimum support

    >>> simple_transactions = [('007', '666', '777'), ('007', 'BC',), ('007', '666'), ('777',)]
    >>> alphabet = ['007', '666', '777', 'BC']
    >>> apriori(simple_transactions, alphabet, 0.3)
    [('007',), ('666',), ('777',), ('007', '666')]
    >>> apriori(simple_transactions, alphabet, 0.6)
    [('007',)]
    >>> apriori(simple_transactions, alphabet, 0.5, fixed_k=2)
    [('007', '666')]
    >>> apriori(simple_transactions, alphabet, 0.75)
    [('007',)]
    >>> apriori(simple_transactions, alphabet, 0.9)
    []
    """

    all_items = sorted(list(all_items))

    k = 1
    N = len(transactions)

    frequent_itemsets = [[], []]  # k index, zero always empty
    support = defaultdict(int)
    transaction_subsets = dict()

    for item in all_items:
        new_item = (item,)
        support[new_item] = support_count(new_item, transactions)

        if support[new_item] >= N * minsup:
            frequent_itemsets[1].append(new_item)

    pruned_candidates = [True, 'dummy']

    while pruned_candidates and len(pruned_candidates) > 1 and (not fixed_k or k < fixed_k):
        k += 1
        candidates = _apriori_gen(frequent_itemsets[k - 1])
        pruned_candidates = _apriori_prune(candidates, transactions, k, frequent_itemsets, minsup)
        if verbose:
            print('k=%s - candidate itemsets: %s - pruned itemsets: %s' % (k, len(candidates), len(pruned_candidates)))
        if not pruned_candidates:
            break

        frequent_itemsets.append(pruned_candidates)

    if fixed_k:
        try:
            return frequent_itemsets[fixed_k]
        except IndexError:
            return []

    return list(itertools.chain(*frequent_itemsets))


if __name__ == "__main__":
    print('Running doctests')
    import doctest
    res = doctest.testmod()
    if not res[0]:
        print('OK!')
