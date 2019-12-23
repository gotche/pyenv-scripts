VENV := pyenv-scripts
VERSION := 3.7.6

test:
	python -m pytest

coverage:
	coverage run --source update -m pytest
	coverage report -m

check_types:
	mypy .

install_dev_env:
	pyenv uninstall -f $(VENV)
	pyenv install -s $(VERSION)
	pyenv virtualenv -p python3.7 $(VERSION) $(VENV)
	pyenv local $(VENV)
	pip install -r requirements.txt
