.PHONY: test dist upload clean pypi sql

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r *.egg-info || true

dist: test
	python setup.py sdist

release: clean pypi

pypi: test
	python setup.py sdist upload

sql:
	rm test.db || true
	sqlite3 test.db < table.sql

test: clean sql
	py.test -svx test
