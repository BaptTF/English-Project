# setup.py
from setuptools import setup, Extension

module = Extension(
    "markov_c",
    sources=["fake_word_generator_lib.c"],
    extra_compile_args=[
        "-O3",
        "-march=native",
        "-ffast-math",
        "-funroll-loops",
        "-flto",  # Link-time optimization
    ],
)

setup(
    name="markov_c",
    version="1.0",
    description="Highly optimized Markov chain word generator",
    ext_modules=[module],
)
