from colag import Colag

NUM_PARAMS = 13

def get_param_value(param, grammar):
    """Return the status (0 or 1) of parameter number `param` in `grammar`,
    zero-paramed.

    param=12 -> the 0th bit
    param=0 -> the 12th bit

    """

    return int(bool((1 << (NUM_PARAMS - param -1)) & grammar))

def toggled(param, grammar):
    """ Returns grammar with parameter number `parameter` toggled

    >>> gram = int('0100', 2)
    >>> t = toggled(3, gram)
    >>> "{0:b}".format(t)
    '1100'
    """
    return grammar ^ (1 << (NUM_PARAMS - param - 1))

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

def mark_irrelevant_params_ignore_weakly_equiv(colag, sentence):
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
            supersets = colag.find_equivalent(generator)
            gens = [g for g in generators
                        if g not in supersets]
            if minimal_pair not in gens and colag.legal_grammar(minimal_pair):
                relstr[param] = '*'
                break
    return relstr


def mark_irrelevant_params_ignore_supersets(colag, sentence):
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
            supersets = colag.find_supersets(generator)
            gens = [g for g in generators
                        if g not in supersets]
            if minimal_pair not in gens and colag.legal_grammar(minimal_pair):
                relstr[param] = '*'
                break
    return relstr

def main():
    colag = Colag.default()

    for sentence in sorted(colag.sentences):
        irr_str = mark_irrelevant_params_ignore_weakly_equiv(colag, sentence)
        print(sentence, ''.join(irr_str))


if __name__ == '__main__':
    main()
