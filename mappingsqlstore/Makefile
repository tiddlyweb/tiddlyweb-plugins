
sql:
	rm test.db || true
	sqlite3 test.db < table.sql

test: sql
	py.test -svx test
