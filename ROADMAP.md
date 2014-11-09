# Roadmap

Priorities: 

* [x] in-depth reference documentation of all major functionality (`authenticate`, `Account`, `CoreQuery`, `Report`) in docstrings
* [ ] expose reference documentation by turning it into HTML with [python-inspector](https://github.com/debrouwere/python-inspector/) and pandoc.
* [ ] query subcommand in the CLI

Can wait: 

* [ ] nicer and more powerful `CoreQuery#segment` interface
* [ ] nicer filtering interface
* [ ] drop into a Python shell, automatically log in and expose `accounts`
* [ ] support for Live Analytics
* [ ] wrap errors into ones that are easier to understand and test against in try/except blocks.
* [ ] example report-to-html template
* [ ] unit tests for the authentication functionality
