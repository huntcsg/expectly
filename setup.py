from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst'), 'rb') as f:
        README = f.read().decode('utf-8')
    with open(os.path.join(here, 'CHANGES.rst'), 'rb') as f:
        CHANGES = f.read().decode('utf-8')
    with open(os.path.join(here, 'AUTHORS.rst'), 'rb') as f:
        AUTHORS = f.read().decode('utf-8')
except IOError:
    README = CHANGES = AUTHORS = ''

install_requires = [
    'jsonschema',
    'jmespath',
]

testing_requires = [
    'pytest',
    'pytest-cov',
    'pytest-html',
    'requests',
    'requests-mock'
]

docs_require = [
    'sphinx',
    'sphinx_rtd_theme',
]

dev_requires = testing_requires + docs_require + [
    'isort',
    'flake8',
    'ipython',
    'bumpversion',
]

setup(
    name='expectly',
    version='0.1.4',
    description='An HTTP API centric BDD style test framework',
    long_description="\n".join([README, CHANGES, AUTHORS]),
    author='Hunter Senft-Grupp',
    author_email='huntcsg@gmail.com',
    url='https://github.com/huntcsg/expectly',
    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },
    install_requires=install_requires,
    extras_require={
        'testing': testing_requires,
        'dev': dev_requires,
        'docs': docs_require,
    },
    keywords="testing bdd rest api expect rspec chakram chai",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries'
    ],
)
