from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, "doxygen_parser/requirements.txt")) as f:
    deps = f.readlines()

test_deps = [
    'pytest',
    'mypy'
]

setup(
    name='doxygen-parser',
    version='0.1.0',
    description='Parse doxygen',
    url='https://github.com/paulgessinger/doxygen-parser',
    license='MIT',

    author='Paul Gessinger',

    author_email='hello@paulgessinger.com',

    packages=find_packages(exclude=[]),
    package_data={
        'doxygen_parser': ["requirements.txt"],
    },

    entry_points = {
        # 'console_scripts': ["codereport=codereport.cli:main"]
    },

    extras_require = {
        "lxml": ["lxml"],
        'test': test_deps,
    },
    install_requires=[deps],
    tests_require = test_deps
)
