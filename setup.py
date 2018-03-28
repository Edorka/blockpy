from setuptools import setup, find_packages

setup(
    name='blockpy',
    version='0.5.0',
    url='https://github.com/Edorka/blockpy.git',
    author='Eduardo Orive',
    author_email='edorka@gmail.com',
    description='Minimal implementation of a blockchain',
    # packages=find_packages(),
    py_modules=["block", "node"],
    install_requires=[],
)
