from setuptools import setup, Extension

module = Extension("markov_c", sources=["markov_c.c"], extra_compile_args=["-O3"])

setup(
    name="markov_c",
    version="1.0",
    description="Markov chain word generator",
    ext_modules=[module],
)
