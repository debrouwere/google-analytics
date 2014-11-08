from setuptools import setup, find_packages

setup(name='googleanalytics',
    description='A wrapper for the Google Analytics API.',
    long_description=open('README.rst').read(),
    author='Stijn Debrouwere',
    author_email='stijn@debrouwere.org',
    #url='http://stdbrouw.github.com/python-google-analytics/',
    download_url='http://www.github.com/debrouwere/google-analytics/tarball/master',
    version='0.7.2',
    license='ISC',
    packages=find_packages(),
    keywords='data analytics api wrapper google',
    scripts=[
        'bin/gash'
    ],
    install_requires=[
        'oauth2client==1.3', 
        'google-api-python-client==1.3', 
        'python-dateutil==1.5',
        'addressable==dev', 
        'inspector==dev', 
        'flask==0.10', 
        'keyring==4', 
    ], 
    test_suite='googleanalytics.tests', 
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        ],
    )