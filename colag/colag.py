import argparse
import csv
import random
import numpy as np
from itertools import repeat
from collections import Counter
from scipy.spatial import distance

TRIGGER_VEC_ORDER = '01*~'

COLAG_TSV = '../data/COLAG_2011_ids.txt'
IRRELEVANCE_OUTPUT = '../data/irrelevance-output.txt'

parameters = ['sp',
              'hip',
              'hcp',
              'opt',
              'ns',
              'nt',
              'whm',
              'pi',
              'tm',
              'VtoI',
              'ItoC',
              'ah',
              'QInv']

def grammar_str(g):
    return '{:013b}'.format(g)

def mutate_grammar(rate, g):
    for i in range(13):
        if random.random() < rate:
            g = toggled(i, g)
    return g

def hamming_distance(g1, g2):
    distance = 0
    for i in range(13):
        if get_param_value(i, g1) != get_param_value(i, g2):
            distance += 1
    return distance

def get_param_value(index, grammar):
    """Return the status (0 or 1) of parameter number `index` in `grammar`,
    zero-indexed.

    >>> get_param_value(2, int('0100', 2))
    1

    >>> get_param_value(2, int('0100', 3))
    0

    """

    return int(bool((1 << index) & grammar))

def toggled(param, grammar):
    """ Returns grammar with parameter number `parameter` toggled

    >>> gram = int('0100', 2)
    >>> t = toggled(3, gram)
    >>> "{0:b}".format(t)
    '1100'
    """
    return grammar ^ (1 << param)

def jaccard_coef(a, b):
    a = list(a)
    b = list(b)
    return len(np.intersect1d(a, b)) / len(np.union1d(a, b))

def counter_to_block(counter):
    return [counter[x] for x in TRIGGER_VEC_ORDER]

def irrelevence_array(irrel_list):
    counts = [Counter(param_col)
                  for param_col in zip(*irrel_list)]
    return [count
                for counter in counts
                for count in counter_to_block(counter)]

class Colag:
    def __init__(self, grammars, sentences, grammar_irr, sentence_irr):
        self.sentences = sentences
        self.grammars = grammars
        self.grammar_irr = grammar_irr
        self.sentence_irr = sentence_irr

    @classmethod
    def from_tsvs(cls, colag_tsv, irrelevance_tsv):
        """Returns a dictionary with sentence ids as keys. Each value is a set of
        grammars IDs - the grammars that generate that sentence.

        """
        grammars = {}
        sentences = {}
        sentence_irr = {}
        grammar_irr = {}

        with open(irrelevance_tsv) as handle:
            for line in handle:
                sid, irr = line.split()
                sentence_irr[int(sid)] = irr

        with open(colag_tsv) as handle:
            reader = csv.reader(handle, delimiter='\t')
            for grammar, sentence, _ in reader:
                grammar = int(grammar)
                sentence = int(sentence)
                irr_str = sentence_irr[sentence]
                try:
                    sentences[sentence].add(grammar)
                    sentence_irr[irr_str].add(grammar)
                except KeyError:
                    sentences[sentence] = {grammar}
                    sentence_irr[irr_str] = {grammar}
                try:
                    grammars[grammar].add(sentence)
                    grammar_irr[grammar].append(irr_str)
                except KeyError:
                    grammars[grammar] = {sentence}
                    grammar_irr[grammar] = [irr_str]
        assert len(sentences) == 48077, 'expected 48077 sentences in colag tsv'
        assert len(grammars) == 3072, 'expected 3072 grammars in colag tsv'

        return Colag(grammars, sentences, grammar_irr, sentence_irr)

    def grammar_sent_distance(self, g1, g2):
        return 1 - jaccard_coef(self.grammars[g1], self.grammars[g2])

    def grammar_trig_distance(self, g1, g2):
        return distance.cosine(self.trigger_vector(g1), self.trigger_vector(g2))

    def trigger_vector(self, g1):
        return irrelevence_array(self.grammar_irr[g1])

def distance_simulation():
    colag = Colag.from_tsvs(COLAG_TSV, IRRELEVANCE_OUTPUT)
    while True:
        rate = random.random()
        g1 = random.randint(0, 2**13)
        g2 = mutate_grammar(rate, g1)
        if not (g1 in colag.grammars and g2 in colag.grammars):
            continue
        ham = hamming_distance(g1, g2)
        yield {'g1': g1,
               'g2': g2,
               'hamming_distance': ham,
               'sentence_distance': colag.grammar_sent_distance(g1, g2),
               'trigger_distance': colag.grammar_trig_distance(g1, g2)}

def distance_simulation_stdout(n=None):
    keys = ['g1', 'g2', 'hamming_distance', 'sentence_distance', 'trigger_distance']
    print(', '.join(keys))
    count = range(n) if n is not None else repeat(None)
    for _, item in zip(count, distance_simulation()):
        print(', '.join(str(item[key]) for key in keys))

def grammar_trigger_vectors():
    colag = Colag.from_tsvs(COLAG_TSV, IRRELEVANCE_OUTPUT)
    for g in colag.grammars:
        yield [g] + colag.trigger_vector(g)

def grammar_trigger_vectors_stdout():
    header = ['grammar'] + ['P{}={}'.format(n, c)
                                for irrstr, n in zip(repeat(TRIGGER_VEC_ORDER), range(1, 14))
                                for c in irrstr]
    print(', '.join(header))
    for row in grammar_trigger_vectors():
        print(', '.join(str(x) for x in row))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    distance = subparsers.add_parser('distance',
                                     help=""" Run a simulation that picks random grammars in pairs and computes hamming, jacard, and cosine distance between them. """)
    distance.add_argument('n', type=int, default=None, nargs='?')
    distance.set_defaults(func=distance_simulation_stdout)

    trigger = subparsers.add_parser('trigger',
                          help=""" Output the trigger vector for every grammar in colag. """)
    trigger.set_defaults(func=grammar_trigger_vectors_stdout)

    args = parser.parse_args()

    if 'func' not in args:
        parser.print_help()
        return

    args.func(**dict((key, val)
                     for key, val in args.__dict__.items()
                         if key != 'func'))

if __name__ == "__main__":
    main()
