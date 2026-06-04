PYTHON = python3

.PHONY: all uninstall clean test demo build install dev-install upload

all:
	make uninstall
	make clean
	make test
	make demo
	make build
	make install

uninstall:
	$(PYTHON) -m pip uninstall -y phuker-music

clean:
	rm -rf *.egg-info dist

test: ./tests/
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(PYTHON) -m phuker_music albums -v -f ./tests/files/albums.test.json

demo: ./docs/
	$(PYTHON) -m phuker_music albums -v -f ./docs/albums.json

build dist/*.whl dist/*.tar.gz: pyproject.toml
	uvx --from build pyproject-build --installer uv
	rm -rf *.egg-info
	$(PYTHON) -m twine check dist/*.whl dist/*.tar.gz

install: dist/*.whl
	$(PYTHON) -m pip install dist/*.whl
	$(PYTHON) -m pip show phuker-music

dev-install:
	$(PYTHON) -m pip install -e .
	rm -rf *.egg-info

upload: dist/*.whl dist/*.tar.gz
	$(PYTHON) -m twine upload dist/*.whl dist/*.tar.gz
