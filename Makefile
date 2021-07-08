test:
	pylint --rcfile=.pylintrc cornell tests

configure:
	pip install -e .'[dev]'
