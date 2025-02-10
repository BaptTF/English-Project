from collections import defaultdict
from collections.abc import Callable
import ctypes
import random


class MarkovChain:
    def __init__(self, word_set: set, order: int = 2):
        """
        Initialize the Markov chain with a list of words and an order (default is 2).
        """
        self.order = order
        self.transitions = defaultdict(list)
        self.word_set = word_set
        # Load the C library
        self.markov_lib = ctypes.CDLL("./fake_word_generator_lib.so")
        # Set the argument types.
        self.markov_lib.load_transitions_from_python.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),  # states array
            ctypes.POINTER(ctypes.c_char_p),  # transitions array
            ctypes.c_int                      # number of entries
        ]
        self.markov_lib.load_wordset_from_python.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),  # word set array
            ctypes.c_int                      # number of words
        ]
        # Note: Use POINTER(ctypes.c_char) for a mutable buffer.
        self.markov_lib.generate_word.argtypes = [ctypes.POINTER(ctypes.c_char)]
        self.markov_lib.generate_word.restype = None
        self.build_transitions(word_set)
        self.load_markov_into_c()
        # Load the same real word set into C so that generated words not in this set are considered fake.
        self.load_wordset_into_c(word_set)

    def build_transitions(self, word_set: set):
        """
        Build the transition probabilities based on the input word list.
        """
        for word in word_set:
            # Pad the word with start and end markers
            padded_word = "^" * self.order + word + "$"
            for i in range(len(padded_word) - self.order):
                # Get the current state (sequence of characters) and the next character
                state = padded_word[i : i + self.order]
                next_char = padded_word[i + self.order]
                self.transitions[state].append(next_char)

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

    def generated_fake_word(self, generate_word_func: Callable[[int], str] = generate_word):
        """
        Generate a fake word that is not in the input word list.
        """
        fake_word_in_word_list = True
        while fake_word_in_word_list:
            fake_word = generate_word_func()
            if fake_word not in self.word_set:
                fake_word_in_word_list = False
        return fake_word

    def export_transitions(self):
        """
        Convert transitions into C-friendly format:
        - states: list of strings
        - transitions: list of concatenated possible next characters
        """
        states = list(self.transitions.keys())
        transitions = ["".join(chars) for chars in self.transitions.values()]
        return states, transitions

    def generate_word_from_c(self):
        buffer = ctypes.create_string_buffer(10 + 1)
        self.markov_lib.generate_word(buffer)
        return buffer.value.decode("utf-8")

    def load_markov_into_c(self):
        states, transitions = self.export_transitions()
        states_c = (ctypes.c_char_p * len(states))(*[s.encode("utf-8") for s in states])
        transitions_c = (ctypes.c_char_p * len(transitions))(
            *[t.encode("utf-8") for t in transitions]
        )
        self.markov_lib.load_transitions_from_python(states_c, transitions_c, len(states))

    def load_wordset_into_c(self, word_set: set):
        words = list(word_set)
        words_c = (ctypes.c_char_p * len(words))(*[w.encode("utf-8") for w in words])
        self.markov_lib.load_wordset_from_python(words_c, len(words))

def load_word_list(file_path: str):
    """
    Load a list of words from a file.
    """
    with open(file_path, "r") as file:
        return {line.strip().lower() for line in file}


def fake_and_real_word(
    markov_chain: MarkovChain, word_set: set, nb_word: int, nb_fake_word: int
):
    """
    Generate a list of fake and real words.
    """
    real_words = random.sample(sorted(word_set), nb_word)
    fake_words = [markov_chain.generated_fake_word() for _ in range(nb_fake_word)]
    return real_words, fake_words


if __name__ == "__main__":

    word_set = load_word_list("words_alpha.txt")
    mc = MarkovChain(word_set, order=3)

    for _ in range(5):
        print("C generated:", mc.generate_fake_word_from_c())
        print("Python generated:", mc.generated_fake_word())
