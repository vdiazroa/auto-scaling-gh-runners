run:
	python app.py

build-run:
	./start.sh

publish-patch:
	python scripts/publish.py patch

publish-minor:
	python scripts/publish.py minor

publish-major:
	python scripts/publish.py major
