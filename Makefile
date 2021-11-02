test:
	pylint --rcfile=.pylintrc cornell tests
	pytest --cov=cornell tests

configure:
	pip install -e .'[dev]'

docker_build:
	docker build . -t hiredscorelabs/cornell:latest

docker_push
	echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
	docker push hiredscorelabs/cornell:latest

publish:
	python setup.py sdist
	pip install twine
	twine upload dist/*
