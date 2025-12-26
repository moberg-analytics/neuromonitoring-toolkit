# setup.py
from setuptools import setup, find_packages

setup(
    name="nmtk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "physio",
        "pandas",
        "numpy",
        "matplotlib",
        "scipy",
    ],
)