===========================
 Irrelevance and Ambiguity
===========================

Right now the code just spits out sentence ids and strings separated by tabs, to
stdout. I joined it to the original data table in pandas, which isn't included
in this repo yet.

Usage
=====

.. code::

   $ python irrelevate_sentences.py COLAG_2011_ids.txt

    loading pickled db
    0        ~~*~0~~~1~*0*
    1        ~~*~0~~~1~*0*
    2        ~~*~0~~~1~*0*
    3        ~~*~0~~~1~*0*
    4        ~~*~0~~~~~*01
    5        ~~*~0~~~~~*01
    6        ~~*~0~~~1~*0*
    7        ~~*~0~~~~~*01
    8        ~~*~0~~~~~*01
    9        ~~*~0~~~1~*0*
    10       ~~*~0~~~~~*01
    11       ~~*~0~~~~~*01
    12       ~~*~0~~~1~*0*
    13       ~~*~0~~~1~*0*
    14       ~~*~0~~~1~*0*
    15       ~~*~0~~~1~*0*
    16       ~~*~0~~~~~*01
    17       ~~*~0~~~~~*01
    18       ~~*~0~~~1~*0*
    19       ~~*~0~~~~~*01
    20       ~~*~0~~~~~*01
    21       ~~*~0~~~1~*0*
    22       ~~*~0~~~~~*01
    ...
