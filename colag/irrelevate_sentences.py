from colag import Colag

NUM_PARAMS = 13

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
    generators = colag.sentences[sentence]
    for i in range(13):
        values = set(get_param_value(i, gram) for gram in generators)
        assert len(values) > 0
        if len(values) == 1:
            param_list[i] = str(values.pop())
        else:
            param_list[i] = '~'

    return param_list


def mark_irrelevant_params(colag, sentence):
    """Returns 13-item list containing 0, 1, ~ or *"""
    relstr = mark_unambiguous_params(colag, sentence)
    for param, val in enumerate(relstr):
        assert val in ['~', '0', '1'], val
        if val != '~':
            continue
        generators = colag.sentences[sentence]
        for generator in generators:
            minimal_pair = toggled(param, generator)
            # TODO: is this "and" correct?
            if minimal_pair not in generators and colag.legal_grammar(minimal_pair):
                relstr[param] = '*'
                break
    return relstr

def main():
    colag = Colag.default()

    for sentence in sorted(colag.sentences):
        irr_str = mark_irrelevant_params(colag, sentence)
        # reverse the order of the str. the first parameter should be the first
        # *bit* in the number, not the first char in the str.
        irr_str = irr_str[::-1]
        print sentence, ''.join(irr_str)


if __name__ == '__main__':
    main()
