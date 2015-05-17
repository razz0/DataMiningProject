"""Implementation of the Apriori algorithm for sequential patterns, F(k-1) x F(k-1) variant.

Model sequences like ((1, 2, 3), (4, 5), (4, 6)).

To get course sequences with empty elements as (0,):
course_seqs = [x.course_sequence for x in s.students]
course_seqs2 = [tuple([seq or (0,) for seq in x.course_sequence]) for x in s.students]
"""

from collections import defaultdict
from pprint import pprint
import copy


def flatten(sequence):
    """Flatten events in sequence elements to list of events"""
    return [event for element in sequence for event in element]


def is_subsequence(seq1, seq2):
    """Check if seq1 is a subsequence of seq2

    >>> is_subsequence(((2,), (3, 5)), ((2, 4), (3, 5, 6), (8,)))
    True
    >>> is_subsequence(((1,), (2,)), ((1, 2), (3, 4)))
    False
    >>> is_subsequence(((2,), (4,)), ((2, 4), (2, 4), (2, 5)))
    True
    """
    seq = copy.deepcopy(seq1)
    for element in seq2:
        if seq and set(seq[0]) <= set(element):
            seq = seq[1:]

    return True if not seq else False


def support_count(sequence, seq_list):
    """
    Count support count for sequence

    :param itemset: items to measure support count for
    :param transactions: list of sets (all transactions)

    >>> simple_seqs = [((1,), (2, 3)), ((2,), (3,)), ((2, 4,),), ((4,),)]
    >>> [support_count(((item,),), simple_seqs) for item in range(1, 5)]
    [1, 3, 2, 2]
    """
    return len([seq for seq in seq_list if is_subsequence(sequence, seq)])


def _sequential_candidate_generation(sequences, k):
    """
    Generate candidate sequences of length k.

    :param sequences: list of sequences containing elements containing events
    :param k: > 1

    >>> pprint(_sequential_candidate_generation([(('A',),), (('B',),), (('C',),)], 2))
    [(('A',), ('A',)),
     (('A',), ('B',)),
     (('A', 'B'),),
     (('A',), ('C',)),
     (('A', 'C'),),
     (('B',), ('A',)),
     (('B',), ('B',)),
     (('B',), ('C',)),
     (('B', 'C'),),
     (('C',), ('A',)),
     (('C',), ('B',)),
     (('C',), ('C',))]
    >>> _sequential_candidate_generation([(('A', 'B'),), (('A', 'C'),), (('B',), ('C',))], 3)
    [(('A', 'B'), ('C',))]
    >>> _sequential_candidate_generation([(('A',), ('B',)), (('A', 'C'),), (('B', 'C'),), (('C', 'C'),)], 3)
    [(('A',), ('B', 'C')), (('A', 'C', 'C'),), (('B', 'C', 'C'),)]
    >>> pprint(_sequential_candidate_generation([((1,),), ((2,),), ((3,),)], 2))
    [((1,), (1,)),
     ((1,), (2,)),
     ((1, 2),),
     ((1,), (3,)),
     ((1, 3),),
     ((2,), (1,)),
     ((2,), (2,)),
     ((2,), (3,)),
     ((2, 3),),
     ((3,), (1,)),
     ((3,), (2,)),
     ((3,), (3,))]
    >>> _sequential_candidate_generation([((1,), (2,)), ((2,), (3,))], 3)
    [((1,), (2,), (3,))]
    """

    new_candidates = []
    for index1, seq1 in enumerate(sequences):
        for index2, seq2 in enumerate(sequences):
            if k == 2:
                # Assume we get 1-sequences like we should
                new_candidates.append((seq1[0], seq2[0],))
                if seq1[0] < seq2[0]:
                    new_candidates.append(((seq1[0] + seq2[0]),))
            elif k > 2:
                seq1_flattened = flatten(seq1)
                seq2_flattened = flatten(seq2)
                if index1 == index2:
                    continue
                if seq1_flattened[1:] == seq2_flattened[:-1]:
                    new_sequence = copy.deepcopy(seq1)
                    if len(seq2[-1]) > 1:
                        new_sequence = new_sequence[:-1] + (new_sequence[-1] + (seq2_flattened[-1],),)
                    else:
                        new_sequence += (seq2[-1],)
                    new_candidates.append(new_sequence)

    return new_candidates


def get_subsequences(sequence):
    """
    Get length k-1 subsequences of length k sequence

    >>> get_subsequences((('A', 'B'), ('C',)))
    [(('A', 'B'),), (('A',), ('C',)), (('B',), ('C',))]
    >>> get_subsequences((('A', 'B'), ('C',), ('D', 'E')))
    [(('A', 'B'), ('C',), ('D',)), (('A', 'B'), ('C',), ('E',)), (('A', 'B'), ('D', 'E')), (('A',), ('C',), ('D', 'E')), (('B',), ('C',), ('D', 'E'))]

    :rtype : tuple
    :return:
    """
    subseqs = []

    for i in reversed(range(0, len(sequence))):
        element = sequence[i]
        for j in reversed(range(0, len(element))):
            event = element[j]
            if len(element) == 1:
                subseq = sequence[:i] + sequence[(i + 1):]
            else:
                subseq = list(sequence)
                subseq[i] = subseq[i][:j] + subseq[i][(j + 1):]

            subseqs.append(tuple(subseq))

    return subseqs


def apriori_sequential(sequences, minsup, fixed_k=None, verbose=False):
    """
    Apriori method for sequential patterns

    :param transactions: list of iterables (list of transactions containing items)
    :param all_items: list distinct items
    :param minsup: minimum support

    >>> seqs = [((1, 2, 4), (2, 3), (5,)), \
                ((1, 2), (2, 3, 4)), \
                ((1, 2), (2, 3, 4), (2, 4, 5)), \
                ((2,), (3, 4), (4, 5)), \
                ((1, 3), (2, 4, 5))]
    >>> pprint(apriori_sequential(seqs, 0.8))
    [{((1,),): 0.80000000000000004},
     {((2,),): 1.0},
     {((3,),): 1.0},
     {((4,),): 1.0},
     {((5,),): 0.80000000000000004},
     {((1,), (2,)): 0.80000000000000004},
     {((2,), (3,)): 0.80000000000000004},
     {((2, 4),): 0.80000000000000004},
     {((3,), (5,)): 0.80000000000000004}]
    >>> seqs = [((1,), (), (), (2,), (), (), (3,)), \
                ((1, 2,), (), (2,3 ), (2,), (), (3,), ()), \
                ((1,), (2,), (), (2,), (3,), (3,), (2, 3, 4))]
    """

    k = 1
    N = len(sequences)

    frequent_sequences = [[], []]  # k index, zero always empty
    support = defaultdict(int)

    if verbose:
        print 'Initializing length 1 frequent sequences...'

    for seq in sequences:
        events = sorted(set(flatten(seq)))
        for event in events:
            event_seq = ((event,),)
            if event_seq not in support:
                support[event_seq] = support_count(event_seq, sequences)

                #print "k==1, event seq: %s - support: %s" % (event_seq, support[event_seq])

                if support[event_seq] >= N * minsup and event_seq not in frequent_sequences[1]:
                    frequent_sequences[1].append(event_seq)

    if verbose:
        print 'Initialized %s 1-sequences' % len(frequent_sequences[1])
        print 'Generating longer frequent sequences...'

    pruned_candidates = ['dummy', 'dummy']

    while pruned_candidates and len(pruned_candidates) > 1 and (not fixed_k or k < fixed_k):
        k += 1
        candidate_seqs = _sequential_candidate_generation(frequent_sequences[k - 1], k)
        if verbose:
            print 'k=%s - candidate sequence count %s' % (k, len(candidate_seqs),)
        if not candidate_seqs:
            break

        pruned_candidates = []

        for can_seq in candidate_seqs:
            subseqs = get_subsequences(can_seq)
            if all([subseq in frequent_sequences[k - 1] for subseq in subseqs]) and can_seq not in pruned_candidates:
                pruned_candidates.append(can_seq)

        for pruned_index, pruned_seq in enumerate(pruned_candidates):
            if verbose and k > 3 and len(pruned_candidates) > 50 \
                    and pruned_index % (1 + len(pruned_candidates) / 5) == 0:
                print 'Candidate %s / %s' % (pruned_index, len(pruned_candidates))
            for seq in sequences:
                if is_subsequence(pruned_seq, seq):
                    support[pruned_seq] += 1

        frequent_sequences.append([seq for seq in pruned_candidates if support[seq] >= N * minsup])

    if fixed_k:
        try:
            freq_items = [{freqseq: support[freqseq] / float(N)} for freqseq in frequent_sequences[fixed_k]]
        except IndexError:
            return []
    else:
        freq_items = [{freqseq: support[freqseq] / float(N)} for freq_k in frequent_sequences for freqseq in freq_k]

    return freq_items


if __name__ == "__main__":
    print 'Running doctests'
    import doctest
    res = doctest.testmod()
    if not res[0]:
        print 'OK!'
