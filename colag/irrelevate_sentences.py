import csv

NUM_PARAMS = 13

def read_colag_tsv(filename):
    """Returns a dictionary with sentence ids as keys. Each value is a set of
    grammars IDs - the grammars that generate that sentence.

    """
    colag = {}
    with open(filename) as handle:
        reader = csv.reader(handle, delimiter='\t')
        for grammar, sentence, _ in reader:
            grammar = int(grammar)
            sentence = int(sentence)
            try:
                colag[sentence].add(grammar)
            except KeyError:
                colag[sentence] = {grammar}
    return colag

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

def mark_unambiguous_params(colag, sentence):
    """Returns a 13-item list of strings, each item either 0, 1 or ~.

    For a parameter Pi, if every grammar in colag that generates `sentence` has
    Pi set to the same value v (0 or 1), then the returned list will have its
    i-th element set to v. Otherwise, it will be ~.

    """

    param_list = [None for _ in range(13)]
    generators = colag[sentence]
    for i in range(13):
        values = set(get_param_value(i, gram) for gram in generators)
        assert len(values) > 0
        if len(values) == 1:
            param_list[i] = str(values.pop())
        else:
            param_list[i] = '~'

    return param_list


def mark_irrelevant_params(colag, disallowed, sentence):
    """Returns 13-item list containing 0, 1, ~ or *"""
    relstr = mark_unambiguous_params(colag, sentence)
    for param, val in enumerate(relstr):
        assert val in ['~', '0', '1'], val
        if val != '~':
            continue
        generators = colag[sentence]
        for generator in colag[sentence]:
            minimal_pair = toggled(param, generator)
            # TODO: is this "and" correct?
            if minimal_pair not in generators and minimal_pair not in disallowed:
                relstr[param] = '*'
                break
    return relstr

def main():
    colag = read_colag_tsv('../data/COLAG_2011_ids.txt')
    grammars = set([g
                    for grams in colag.values()
                    for g in grams])

    assert len(colag) == 48077, 'expected 48077 sentences in colag tsv'
    assert len(grammars) == 3072, 'expected 3072 grammars in colag tsv'

    # the grammars that are not included in colag.
    disallowed = {g for g in range(2**NUM_PARAMS)
                  if g not in grammars}

    for sentence in sorted(colag):
        print(sentence,
              ''.join(mark_irrelevant_params(colag, disallowed, sentence)))


if __name__ == '__main__':
    main()
