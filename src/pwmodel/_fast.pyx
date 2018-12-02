#!/usr/bin/env cython
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: embedsignature=True
# coding: utf-8

from cpython cimport array

cpdef compute_ngrams(unicode word, unsigned int min_n, unsigned int max_n=0):
    """Get the list of all possible ngrams for a given word.
    Parameters
    ----------
    word : str
        The word whose ngrams need to be computed.
    min_n : unsigned int
        Minimum character length of the ngrams.
    max_n : unsigned int
        Maximum character length of the ngrams.
    Returns
    -------
    list of str
        Sequence of character ngrams.
    """
    cdef unicode extended_word = f'\x02{word}\x03'
    # cdef ngrams = array.array('u')
    cdef ngrams = []
    max_n = max(max_n, min_n)
    cdef unsigned int ngram_length = 0
    cdef unsigned int i = 0
    for ngram_length in range(min_n, min(len(extended_word), max_n) + 1):
        for i in range(0, len(extended_word) - ngram_length + 1):
            ngrams.append(extended_word[i:i + ngram_length])
    return ngrams
