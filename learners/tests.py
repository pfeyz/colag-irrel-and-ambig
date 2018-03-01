"""
Tests that would be good to have for the VL

# testing the grammar-choosing code

make a learner whose weights are
0000000000001
and assert that the next grammar they guess is
0b0000000000001 (aka 1)

make a learner whose weights are
1000000000000
and assert that the next grammar they guess is
0b1000000000000 (aka 4096)


# testing the grammar-rewarding code

reward the grammar 0 and assert that all weights are less than 0.5

reward the grammar 8192 (all params = 1) and assert that all the weights are greather than 0.5

reward a grammar like 0b0000000000111

and asert that the first 10 weights are < 0.5 and the last 3 are > 0.5.


# testing both together

pick like 6 different grammars and for each grammar G:

create a learner and reward it like 10000 times with G

assert that when you then ask it to pick a grammar at random, it picks G.

"""
