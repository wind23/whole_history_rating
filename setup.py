from distutils.core import setup

setup(
    name='whr',
    packages=['whr'],
    version='0.0.1',
    license='MIT',
    description=
    'A Python implementation of the Whole History Rating algorithm proposed by Rémi Coulom. '
    'The implementation is based on the Ruby code of GoShrine.',
    author='Tianyi Hao',
    author_email='haotianyi0@126.com',
    url='https://github.com/wind23/whole_history_rating',
    download_url=
    'https://github.com/wind23/whole_history_rating/archive/0.0.1.tar.gz',
    keywords=['WHR', 'whole history rating', 'Elo rating'],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)