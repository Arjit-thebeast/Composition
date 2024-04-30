.PHONY: clean-build
clean-build:
	
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/

	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +
	find . -type d -name __pycache__ -exec rm -rv {} +

	for dir in plugins/*; do \
		if [ -d "$$dir" ]; then \
			rm -rf "$$dir"/dist; \
		fi \
	done

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.DS_Store' -exec rm -fr {} +

.PHONY: clean-test
clean-test: clean-cache
	rm -fr htmlcov/
	rm -f .coverage
	rm -fr coverage.xml

	find . -name ".coverage*" -not -name ".coveragerc" -exec rm -fr "{}" \;

.PHONY: clean-cache
clean-cache:
	rm -fr .tox/
	rm -fr .pytest_cache/
	rm -fr .mypy_cache/

.PHONY: clean
clean: clean-test clean-build clean-pyc

.PHONY: dist
dist:
	rm -rf dist/
	python setup.py sdist

.PHONY: build
build:
	python -m build && \
	for dir in plugins/*; do \
		if [ -d "$$dir" ]; then \
			python -m build "$$dir" --outdir="$$dir"/dist; \
		fi \
	done

.PHONY: publish
publish: dist
	twine upload dist/* && \
	for dir in plugins/*; do \
		if [ -d "$$dir" ]; then \
			twine upload "$$dir"/dist/*; \
		fi \
	done

.PHONY: test-publish
test-publish: dist
	twine upload --repository testpypi dist/* && \
	for dir in plugins/*; do \
		if [ -d "$$dir" ]; then \
			twine upload --repository testpypi "$$dir"/dist/*; \
		fi \
	done

.PHONY: format-code
format-code:
	tox -e isort
	tox -e black

.PHONY: check-code
check-code:
	tox -p -e isort-check -e black-check -e flake8 -e mypy -e pylint


.PHONY: env
env: clean
	if [[ "$$VIRTUAL_ENV" == "" ]];\
	then\
		pipenv --rm;\
		pipenv --clear;\
		pipenv --python 3.10;\
		pipenv install --skip-lock;\
		pipenv install --dev --skip-lock;\
		pipenv run pip install -e .;\
		pipenv run pip install -e plugins/lyzr;\
		pipenv run pip install -e plugins/crew_ai;\
		pipenv run pip install -e plugins/autogen;\
		pipenv run pip install -e plugins/langchain;\
		echo "Enter virtual environment with all development dependencies now: 'pipenv shell'.";\
	else\
		echo "In a virtual environment! Exit first: 'exit'.";\
	fi
