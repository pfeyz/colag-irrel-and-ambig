""" This code was used to generate the data used in notebooks/VL Path Tracking.ipynb """

import random

from colag.colag import Colag
from learners.variational import RewardOnlyLearner, RewardOnlyRelevantLearner, learn_language

class HistoryReporter():
    " A mixin for a VL which will cause it to print out its weights every few steps "

    __id_counter = 0

    def __init__(self, *args, **kwargs):
        self.__name = HistoryReporter.__id_counter
        self.__counter = 0
        HistoryReporter.__id_counter += 1
        super().__init__(*args, **kwargs)

    def consume(self, *args, **kwargs):
        val = super().consume(*args, **kwargs)

        if not self.__counter % 20 == 0:
            self.__counter += 1
            return val

        row = [self.__name] + self.weights

        print('\t'.join(map(str, row)))

        self.__counter += 1
        return val

class LoudRewardOnlyLearner(HistoryReporter, RewardOnlyLearner):
    pass

class LoudRewardOnlyRelevantLearner(HistoryReporter, RewardOnlyRelevantLearner):
    pass

def track_path():
    domain = Colag.default()
    for trial in range(100):
        learner = LoudRewardOnlyRelevantLearner(domain)
        language = list(domain.language[611])
        learn_language(learner, language, 100000)

if __name__ == "__main__":
    track_path()
