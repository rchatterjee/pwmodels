init:
	pip install -r requirements.txt

upload:
	python setup.py sdist bdist bdist_egg
	twine upload dist/*

test:
	tox

