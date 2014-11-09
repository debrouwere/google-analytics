all:
	pandoc -o README.rst README.md

# experimental!
autodoc:
	inspect googleanalytics/auth/__init__.py --include documented --markdown 3 > docs/auth.md
	inspect googleanalytics/account.py --include documented --markdown 3 > docs/account.md
	inspect googleanalytics/query.py --include documented --markdown 3 > docs/query.md
	pandoc docs/auth.md -o docs/auth.html
	pandoc docs/account.md -o docs/account.html
	pandoc docs/query.md -o docs/query.html
	open docs/auth.html
	open docs/account.html
	open docs/query.html

test:
	python setup.py test

upload:
	python setup.py sdist upload
