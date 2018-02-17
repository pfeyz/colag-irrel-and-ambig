from colag.colag import Colag, get_param_value, toggled
import random

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
    def __init__(self, domain, num_params=13, learning_rate=.0005):
        self.domain = domain
        self.learning_rate = learning_rate
        self.weights = [0.5] * num_params

    def converged(self, threshold):
        """Returns true if all values in `weights` list are less than
        `threshold` away from 0 or 1.
        """
        for w in self.weights:
            if not (1 - w < threshold) or (w < threshold):
                return False
        return True

    def parses(self, grammar, sentence):
        """ Returns True if `sentence` parses in `grammar`. """
        return sentence in self.domain.language[grammar]

    def choose_grammar(self):
        """ Returns a random grammar valid in the language domain. Each
        param is picked independently at random (0 or 1) weighted by the
        corresponding weight in self.weights.
        """
        grammar = None
        while not self.domain.legal_grammar(grammar):
            grammar = 0
            for index, w in enumerate(self.weights):
                if random.random() < w:
                    grammar = toggled(12 - index, grammar)
        return grammar

    def consume(self, sentence):
        hypothesis_grammar = self.choose_grammar()
        if self.parses(hypothesis_grammar, sentence):
            self.reward(hypothesis_grammar)
        else:
            self.punish(hypothesis_grammar)

    def reward(self, hypothesis_grammar):
        for index in range(13):
            val = get_param_value(12-index, hypothesis_grammar)
            weight = self.weights[index]
            if val == 0:
                self.weights[index] -= self.learning_rate * weight
            elif val == 1:
                self.weights[index] += self.learning_rate * (1-weight)
            else:
                raise Exception()

    def punish(self, hypothesis_grammar):
        pass

class RewardOnlyLearner(VariationalLearner):
    def punish(self):
        pass

def choose_sentence(language):
    return random.choice(language)

def simulate_learning(domain, target_grammar):
    weights = [0.5] * 13
    target_language = list(domain.language[target_grammar])
    learner = VariationalLearner(domain, num_params=13)
    threshold = 0.02
    counter = 0
    while not learner.converged(threshold):
        sentence = choose_sentence(target_language)
        learner.consume(sentence)
        if counter >= 50000:
            break
        counter += 1
    print(counter,
          param_list_to_grammar([round(x) for x in learner.weights]),
          round(100 *
            sum(abs(0.5 - x) * 2 for x in learner.weights) / 13))

if __name__ == "__main__":
    domain = Colag.default()
    for i in range(100):
        simulate_learning(domain, 611)
