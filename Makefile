test:
	pylint --rcfile=.pylintrc cornell tests
	pytest --cov=cornell tests

configure:
	pip install -e .'[dev]'

docker_build_push:
	docker build . -t hiredscorelabs/cornell:latest
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
	docker push hiredscorelabs/cornell:latest

publish:
	python setup.py sdist
	pip install twine
	twine upload dist/*
