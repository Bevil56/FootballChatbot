import nltk
import numpy as np
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()


def tokenize(sentence):
    return nltk.word_tokenize(sentence)


def stemming(word):
    return stemmer.stem(word.lower())


def bag_of_words(tokenize_sentence, all_words):
    tokenize_sentence = [stemming(word) for word in tokenize_sentence]
    list_of_words = np.zeros(len(all_words), dtype=np.float32)
    for index, word in enumerate(all_words):
        if word in tokenize_sentence:
            list_of_words[index] = 1.0
    return list_of_words



