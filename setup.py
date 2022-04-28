from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    l_d = f.read()

setup(
    name='dawacotools',
    version='0.0.1',
    description='Dawaco tools by PWN',
    long_description=l_d,
    long_description_content_type="text/markdown",
    url='https://github.com/bdestombe/python-dawaco-tools',
    author='Bas des Tombe',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['geopandas', 'matplotlib', 'pyodbc'],
)
