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

docker_tag_push:
	REPO="hiredscorelabs/cornell"
	TAG="${REPO}:$(python cornell/_version.py)"
	docker pull ${REPO}:latest
	docker tag ${REPO}:latest ${TAG}
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
	docker push ${TAG}
