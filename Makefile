test:
	uv run pylint --rcfile=.pylintrc cornell tests
	uv run pytest --cov=cornell tests

configure:
	uv sync --extra dev

docker_build_push:
	docker build . -t hiredscorelabs/cornell:latest
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
	docker push hiredscorelabs/cornell:latest

publish:
	rm -rf dist/
	uv build
	uv publish

docker_tag_push:
	REPO="hiredscorelabs/cornell"
	TAG="${REPO}:$(python cornell/_version.py)"
	docker pull ${REPO}:latest
	docker tag ${REPO}:latest ${TAG}
	echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
	docker push ${TAG}
