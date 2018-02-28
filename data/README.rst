============
 Data Files
============

COLAG_2011_ids.txt
==================

A 3-column tsv - Grammar Id, Sentence Id, Structure Id

COLAG_2011_sents.txt
====================

A 3-column tsv - Sentence Id, Illocutionary Force, Sentence String

grammar-trigger-vectors.txt
===========================

A 53 column csv. First column is grammar id, the rest of the 52 (4 * 13) columns
specify the distribution of trigger types observed for that grammar.

The headers look like this::

  grammar, P1=0, P1=1, P1=*, P1=~, P2=0, P2=1, P2=*, ...

These columns should be interpreted as follows.

- P1=0 - There were N sentences observed that were globally valid triggers for
  P1=0 for this grammar.
- P1=1 - There were N sentences observed that were globally valid triggers for
  P1=1 for this grammar.
- P1=* - There were N sentences observed that were relevant but ambiguous as to
  the value of P1 in this grammar.
- P1=~ - There were N sentences observed that were irrelevant as to the value of
  P1 in this grammar.

hamming-jacard-cosine-comparison.txt
====================================

A 5-col tsv.

g1, g2, hamming_distance(g1 g2), jaccard_distance(g1 g2), cosine_distance(t(g1), t(g2))

where

- g1 and g2 are grammar ids
- t(gx) is the distribution of trigger types observed for grammar gx

irrelevance-output.txt
======================

A 2-col tsv: sentence id, irrelevance string

NG_GrammIDs.txt
===============

A single column csv with the grammar ids of all the grammars which DO NOT exist
in the Colag domain.

trees-for-nltk.tsv
==================

A two-column tsv file: structure id, bracketed tree string

the bracketed tree string was rewritten from the original format in colag so
that it could be fed and graphed by nltk.Tree.fromstring.

vl_comparison/
==============

yang_rewrite/
=============
