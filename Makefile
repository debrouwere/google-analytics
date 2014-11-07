all:
	pandoc -o README.rst README.md

test:
	python setup.py test

upload:
	python setup.py sdist upload