from setuptools import setup, find_packages

setup(name='googleanalytics',
    description='A wrapper for the Google Analytics API.',
    long_description=open('README.md').read(),
    author='Stijn Debrouwere',
    author_email='stijn@stdout.be',
    url='http://stdbrouw.github.com/python-google-analytics/',
    download_url='http://www.github.com/stdbrouw/python-google-analytics/tarball/master',
    version='0.2.1',
    license='MIT',
    packages=find_packages(),
    keywords='data analytics api wrapper google',
    scripts=[
        'bin/gash'
    ],
    install_requires=[
        'oauth2client', 
        'google-api-python-client', 
        'python-dateutil',
        'addressable', 
        'flask', 
        'keyring', 
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        ],
    )