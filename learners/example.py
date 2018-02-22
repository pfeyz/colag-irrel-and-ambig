""" A simple example to demonstrate using the colag domain object and a learner """

import random

from colag.colag import Colag
from learners.variational import RewardOnlyLearner

# load the colag domain. this takes a moment.
colag = Colag.default()  # This should change, but right now this classmethod
                         # is how you get the module to read in the colag DB
                         # and the irrelevance strings. I plan to refactor the
                         # Colag class so it makes more sense.

learner = RewardOnlyLearner(colag)
print('pre learning VL weights', learner.weights)

# get the set of sentences in english
english = colag.language[611]  # we know that 611 is the grammar id for english

# make it into a list so we can use random.choice on it.
english = list(english)

for _ in range(100):
    sentence_id = random.choice(english)
    learner.consume(sentence_id)

print('weights after consuming sentence', learner.weights)
