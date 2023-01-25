import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='twitch_bot',
    version='20.0.0',
    author='amorphousWaste',
    description='Plugin-based, asynchronous Python 3.9+ Twitch Bot.',
    license='Unlicense',
    author='amorphousWaste',
    description='Plugin-based, asynchronous Python 3.9+ Twitch Bot.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/amorphousWaste/twitch_bot',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    packages=['twitch_bot'],
    package_dir={'': 'twitch_bot'},
    packages=setuptools.find_packages(where='nori_ui'),
    python_requires='>=3.9',
)
