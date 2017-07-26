import csv
import pickle
import sys
from collections import defaultdict

NUM_PARAMS = 13

class Colag:
    """ Represents the COLAG domain database. """
    def __init__(self, database_fn):
        self.parses = defaultdict(lambda: defaultdict(set))
        self.sentence_licensors = defaultdict(set)
        self.sentences = set()

        with open(database_fn, 'r') as handle:
            reader = csv.reader(handle, delimiter='\t')
            for grammar, sentence, tree in reader:
                grammar, sentence, tree = [int(x) for x in (grammar, sentence, tree)]
                self.parses[grammar][sentence].add(tree)
                self.sentence_licensors[sentence].add((grammar, tree))
                self.sentences.add(sentence)

        self.parses = dict(self.parses)
        self.sentence_licensors = dict(self.sentence_licensors)
        grammars = self.parses.keys()
        self.illegal_grammars = {g for g in range(2**NUM_PARAMS)
                                 if g not in grammars}

        print(len(self.parses), len(self.illegal_grammars))

    def parse(self, grammar, sentence):
        """ Returns all parses (treeids) of `sentence` by `grammar` """
        return self.parses.get(grammar, {}).get(sentence, [])

    def licensors(self, sentence):
        """Returns a list of (grammar, tree) tuples for every possible parse of
        `sentence`."""
        return self.sentence_licensors[sentence]

def grammar_to_str(grammar):
    return format(grammar, '013b')

def sister_grammars(grammar):
    """ Returns a list of all the grammars that differ from `grammar` by a single bit.

    >>> grammar = 8128

    >>> grammar_to_str(8128)
    '1111111000000'

    >>> [grammar_to_str(x) for x in sister_grammars(grammar)]
    ['1111111000001', '1111111000010', '1111111000100', '1111111001000', '1111111010000',
     '1111111100000', '1111110000000', '1111101000000', '1111011000000', '1110111000000',
     '1101111000000', '1011111000000', '0111111000000']
    """

    return [grammar ^ (1 << index)
            for index in range(NUM_PARAMS)]

def param_status(index, grammar):
    """Return the status (0 or 1) of parameter number `index` in `grammar`,
    zero-indexed.

    >>> param_status(2, int('0100', 2))
    1

    >>> param_status(2, int('0100', 3))
    0

    """

    return int(bool((1 << index) & grammar))

def irrelevate(colag, sentence, grammar, tree):
    """Returns the irrelevance string (actually a list of strings) for a particular
    parse of a sentence in a grammar.

    """
    return ['~' if (tree in colag.parse(sister_grammar, sentence)
                    or sister_grammar in colag.illegal_grammars)
            else param_status(param_num, grammar)
            for param_num, sister_grammar in enumerate(sister_grammars(grammar))]

def ambiguate_param(vals):
    """Given all the observed values of a given parameter for a sentence (0, 1 or
    ~), return a single parameter, one of 0, 1, ~ or *. """
    if '~' in vals:
        return '~'
    if len(set(vals)) == 1:
        # unambiguous
        return str(vals[0])
    return '*'

def ambiguate_str(irrelevated_strs):
    """Given a list of irrelevated_strings, return a single string that includes
    ambiguous markers (*).

    """
    return ''.join([ambiguate_param(v)
                    for v in zip(*irrelevated_strs)])

def ambiguate(colag, sentence):
    """Returns an ambiguated string, containing 0, 1, ~ or *, for a given sentence."""
    return ambiguate_str(irrelevate(colag, sentence, grammar, tree)
                         for grammar, tree in colag.licensors(sentence))

def main(db_filename):
    """Writes per-sentence ambiguous/irrelevance strings to sdtout. caches Colag
    object to disk as a pickle on first run and reads from disk during
    subsequent runs.

    """
    cache_fn = 'cached/{}.pkl'.format(db_filename)
    try:
        with open(cache_fn, 'rb') as handle:
            print('loading pickled db')
            colag = pickle.load(handle)
    except FileNotFoundError:
        print('constructing db')
        colag = Colag(db_filename)
        print('pickling db')
        with open(cache_fn, 'wb') as handle:
            pickle.dump(colag, handle)

    return [(sent, ambiguate(colag, sent))
            for sent in colag.sentences]
