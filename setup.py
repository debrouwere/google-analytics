from setuptools import setup, find_packages

setup(name='googleanalytics',
    description='A wrapper for the Google Analytics API.',
    long_description=open('README.rst').read(),
    author='Stijn Debrouwere',
    author_email='stijn@debrouwere.org',
    url='https://github.com/debrouwere/google-analytics/',
    download_url='http://www.github.com/debrouwere/google-analytics/tarball/master',
    version='0.14.2',
    license='ISC',
    packages=find_packages(),
    keywords='data analytics api wrapper google',
    scripts=[
        'bin/googleanalytics'
    ],
    install_requires=[
        'oauth2client==1.3', 
        'google-api-python-client==1.3', 
        'python-dateutil==1.5',
        'addressable>=1.3', 
        'inspect-it>=0.2', 
        'flask==0.10', 
        'keyring==4', 
        'click==3.3', 
        'pyyaml>=3', 
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