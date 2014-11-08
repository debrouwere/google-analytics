all:
	pandoc -o README.rst README.md

# experimental!
autodoc:
	inspect googleanalytics/query.py --markdown 3 > docs/query.md
	pandoc docs/query.md -o docs/query.html
	open docs/query.html

test:
	python setup.py test

upload:
	python setup.py sdist upload
