from collections import defaultdict
from collections.abc import Callable
import random
from threading import Thread, Lock
from queue import Queue, Full
import time


class MarkovChain:

    def __init__(self, word_set: set, whole_word_set: set, order: int = 2):
        self.order = order
        self.transitions = defaultdict(list)
        self.word_set = word_set
        self.whole_word_set = whole_word_set

        # Build transitions first
        self.build_transitions(word_set)

    def build_transitions(self, word_set: set):
        """
        Build the transition probabilities based on the input word list.
        """
        for word in word_set:
            padded_word = "^" * self.order + word + "$"
            for i in range(len(padded_word) - self.order):
                state = padded_word[i : i + self.order]
                next_char = padded_word[i + self.order]
                self.transitions[state].append(next_char)

        # Convert transitions to format expected by C module
        states = list(self.transitions.keys())
        trans = ["".join(chars) for chars in self.transitions.values()]

    def generate_word(self, max_length: int = 10):
        """
        Generate a fake word using the Markov chain.
        """
        word = "^" * self.order  # Start with the initial state
        while True:
            # Get the last 'order' characters of the current word
            state = word[-self.order :]
            # Choose the next character based on the transition probabilities
            next_char = random.choice(self.transitions[state])
            if next_char == "$" or len(word) >= max_length:
                break  # Stop if we reach the end marker or max length
            word += next_char
        # Remove the start markers and return the generated word
        return word[self.order :]

    def generate_fake_word(self):
        """
        Generate a fake word that is not in the input word list.
        """
        fake_word_in_word_list = True
        while fake_word_in_word_list:
            fake_word = self.generate_word()
            if fake_word not in self.whole_word_set:
                fake_word_in_word_list = False
        return fake_word


def load_word_list(file_path: str):
    """
    Load a list of words from a file.
    """
    with open(file_path, "r") as file:
        return {line.strip().lower() for line in file}


def fake_and_real_word(
    markov_chain: MarkovChain, word_list: list, nb_word: int, nb_fake_word: int
):
    """
    Generate a list of fake and real words.
    """
    real_words = random.sample(word_list, nb_word)
    fake_words = [markov_chain.generate_word() for _ in range(nb_fake_word)]
    return real_words, fake_words


if __name__ == "__main__":

    word_set = load_word_list("words_hard.txt")
    mc3 = MarkovChain(word_set, order=3)
    mc2 = MarkovChain(word_set, order=2)
    mc1 = MarkovChain(word_set, order=1)

    for _ in range(5):
        # Print generated words
        print("Queue generated:", mc2.generate_word())
        print("Python generated:", mc2.generate_fake_word())
