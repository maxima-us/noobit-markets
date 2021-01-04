# Always prefer setuptools over distutils
from os import path
from setuptools import setup, find_packages
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get exact dependencies
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='noobit-markets',  # Required
    version='0.0.0',  # Required
    description='',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/maxima-us/noobit-markets',  # Optional
    author='maximaus',  # Optional
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    package_dir={'': 'src'},  # Optional
    packages=find_packages(where='src'),  # Required
    python_requires='>=3.7, <4',
    install_requires=required,
    entry_points={  # Optional
        'console_scripts': [
            'noobit-cli=noobit_markets.ui.cli:launch'
        ],
    },
)