import random

from colag.colag import Colag, get_param_value, toggled
from datetime import datetime

def param_list_to_grammar(params):
    """Given a list of 0s and 1s `params`, treat it as a bitstring and
    return its integer value."""
    grammar = 0
    total_bits = len(params)
    for bit, value in enumerate(params):
        grammar += value * (2 ** (total_bits - bit - 1))
    return grammar

def weighted_coin_flip(weight):
    " Returns 1 with a probability of `weight`, otherwise 0. "
    return int(random.random() < weight)

class VariationalLearner:
    """An abstract base class for a variational learner.

    To create a usable variational learner, make a class that subclasses this
    one and defines `reward` and `punish` methods which update the parameter
    weights.
    """
    def __init__(self, domain, num_params=13, learning_rate=.0005):
        """Args:

        - domain: an object representing the Colag domain. it should
        have the following defined:

          1. a .legal_grammar method, which accepts an integer grammar id
             and returns true if that grammar exists in Colag.

          2. a .language attribute, which is a dictionary which maps from
             grammar ids to sets of sentence ids.

        - num_params: the # of params in the language.
        TODO: make this an attribute of the domain object.

        - learning_rate: a float that controls how much the weights are updated
        with every sentence.

    """

        self.domain = domain
        self.learning_rate = learning_rate
        self.num_params = num_params
        self.weights = [0.5] * num_params

    def consume(self, sentence):
        """ Update the parameter weights based on the knowledge that `sentence`
        (an integer sentence id) exists in the target language.
        """
        hypothesis_grammar = self.choose_grammar()
        if self.parses(hypothesis_grammar, sentence):
            self.reward(hypothesis_grammar, sentence)
        else:
            self.punish(hypothesis_grammar, sentence)

    def parses(self, grammar, sentence):
        """ Returns True if `sentence` parses in `grammar`. """
        return sentence in self.domain.language[grammar]

    def choose_grammar(self):
        """Returns a random grammar valid in the language domain.

        Each param is picked independently at random weighted by the
        corresponding weight in self.weights. If self.weights[0] is 0.2,
        then parameter 1 has a 20% chance of being set to 1.
        """
        grammar = None
        while not self.domain.legal_grammar(grammar):
            grammar = 0
            for index, w in enumerate(self.weights):
                if random.random() < w:
                    grammar = toggled(12 - index, grammar)
        return grammar

    def converged(self, threshold):
        """Returns true if all values in `weights` list are less than
        `threshold` away from 0 or 1.
        """
        for w in self.weights:
            if not (1 - w < threshold) or (w < threshold):
                return False
        return True

    def reward(self, hypothesis_grammar, sentence):
        """ Updates the param weights based on the knowledge that `sentence`
        parses in `hypothesis_grammar`.
        """
        raise NotImplementedError()

    def punish(self, hypothesis_grammar, sentence):
        """ Updates the param weights based on the knowledge that `sentence`
        does not parse in `hypothesis_grammar`.
        """
        raise NotImplementedError()

    def best_guess(self):
        return param_list_to_grammar([round(p) for p in self.weights])

class RewardOnlyLearner(VariationalLearner):
    """ Variational learner that only updates weights if sentence parses in grammar. """
    def reward(self, hypothesis_grammar, sentence):
        for index in range(13):
            val = get_param_value(12-index, hypothesis_grammar)
            weight = self.weights[index]
            if val == 0:
                self.weights[index] -= self.learning_rate * weight
            elif val == 1:
                self.weights[index] += self.learning_rate * (1-weight)

    def punish(*args):
        pass

class RelevantRewardOnlyLearner(VariationalLearner):
    """Reward-only learner that ignores irrelevant parameter evidence.
    """
    def reward(self, hypothesis_grammar, sentence):
        """ If `sentence` is known to be irrelevant to the parameter setting of Pi, do
        not update the weights of Pi. The other parameters might still be updated.
        The irrelevance is a per-sentence/per-parameter consideration.
        """

        trigger_str = self.domain.sentence_irr[sentence]
        for index in range(13):
            if trigger_str[index] == '~':
                continue
            val = get_param_value(12-index, hypothesis_grammar)
            weight = self.weights[index]
            if val == 0:
                self.weights[index] -= self.learning_rate * weight
            elif val == 1:
                self.weights[index] += self.learning_rate * (1-weight)

    def punish(*args):
        pass

class SkepticalRewardOnlyLearner(VariationalLearner):
    """ Relevant-reward-only learner that uses knowledge of ambiguity to temper
    weight adjustments.
    """
    def reward(self, hypothesis_grammar, sentence):
        """ If `sentence` is known to be ambiguous evidence wrt Pi, be
        conservative in adjusting Pi. """
        trigger_str = self.domain.sentence_irr[sentence]
        for index in range(13):
            if trigger_str[index] == '~':
                continue
            learning_rate = self.learning_rate
            if trigger_str[index] == '*':
                learning_rate = learning_rate / 2
            val = get_param_value(12-index, hypothesis_grammar)
            weight = self.weights[index]
            if val == 0:
                self.weights[index] -= learning_rate * weight
            elif val == 1:
                self.weights[index] += learning_rate * (1-weight)

    def punish(*args):
        pass

class PunishOnlyLearner(RewardOnlyLearner):
    def reward(self, hypothesis_grammar, sentence):
        pass

    def punish(self, hypothesis_grammar, sentence):
        ones = (2 ** self.num_params) - 1
        return super().reward(hypothesis_grammar ^ ones, sentence)


#### Simulation Code

def choose_sentence(language):
    return random.choice(language)

def learn_language(learner, target_language, iterations):
    weights = [0.5] * 13
    threshold = 0.02
    counter = 0

    while not learner.converged(threshold):
        sentence = choose_sentence(target_language)
        learner.consume(sentence)
        if counter >= iterations:
            break
        counter += 1

    return counter

def timed_apply(fun, *args, **kwargs):
    start = datetime.now()
    result = fun(*args, **kwargs)
    end = datetime.now()
    return (end - start).total_seconds(), result

def weights_to_params(weights):
    return ''.join(str(round(x)) for x in weights)

if __name__ == "__main__":
    domain = Colag.default()
    for grammar in [611, 3856, 2253, 584]:
        language = tuple(domain.language[grammar])
        for i in range(100):
            learner = RelevantRewardOnlyLearner(domain)
            runtime, iterations = timed_apply(learn_language, learner, language, iterations=600000)
            gcurr = learner.choose_grammar()
            col = [grammar, i, iterations, learner.choose_grammar(), ''] + learner.weights
            col = col + ['', runtime]
            print('\t'.join(map(str, col)))
