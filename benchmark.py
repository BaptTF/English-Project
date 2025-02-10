import time
import statistics
import fake_word_generator

def benchmark_generation(markov_chain : fake_word_generator.MarkovChain, iterations=10000):
    """
    Benchmark the word generation from the Python and C implementations.

    Parameters:
        markov_chain (MarkovChain): An instance of your MarkovChain class.
        iterations (int): The number of iterations to run for each implementation.

    Prints:
        The average generation time (in seconds) for Python and C.
    """
    python_times = []
    c_times = []

    for _ in range(iterations):
        # Benchmark Python generation.
        start = time.perf_counter()
        markov_chain.generated_fake_word(markov_chain.generate_word)
        end = time.perf_counter()
        python_times.append(end - start)

        # Benchmark C generation.
        start = time.perf_counter()
        markov_chain.generated_fake_word(markov_chain.generate_word_from_c)
        end = time.perf_counter()
        c_times.append(end - start)

    avg_python = statistics.mean(python_times)
    avg_c = statistics.mean(c_times)

    print(f"After {iterations} iterations:")
    print(f"Python generated average time: {avg_python:.8f} seconds")
    print(f"C generated average time: {avg_c:.8f} seconds")


# Example usage:
if __name__ == "__main__":
    # Assume your library is loaded and the MarkovChain is defined as shown in previous code.
    word_set = fake_word_generator.load_word_list("words_alpha.txt")
    mc = fake_word_generator.MarkovChain(word_set, order=3)

    # Run the benchmark.
    benchmark_generation(mc, iterations=100000)
