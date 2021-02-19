VENV := pyenv-scripts
VERSION := 3.9.2
FAMILY := python3.9

test:
	python -m pytest

coverage:
	coverage run -m pytest
	coverage report -m

check_types:
	mypy .

install_dev_env:
	pyenv uninstall -f $(VENV)
	pyenv install -s $(VERSION)
	pyenv virtualenv -p $(FAMILY) $(VERSION) $(VENV)
	pyenv local $(VENV)
	pip install -r requirements.txt
