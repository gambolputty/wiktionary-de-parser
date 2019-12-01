from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    readme = fh.read()

setup(name='wiktionary_de_parser',
    version='0.7.9',
    author='Gregor Weichbrodt',
    author_email='gregorweichbrodt@gmail.com',
    description='Extracts data from German Wiktionary dump files. Allows you to add your own extraction methods 🚀',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: German',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    url='https://github.com/gambolputty/wiktionary_de_parser',
    keywords='wiktionary xml parser data-extraction german nlp',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=['lxml', 'pyphen'],
    project_urls={
        'Bug Reports': 'https://github.com/gambolputty/wiktionary_de_parser/issues',
        'Source': 'https://github.com/gambolputty/wiktionary_de_parser',
    })
