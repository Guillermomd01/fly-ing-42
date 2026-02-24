VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

MAIN = main.py
CONFIG_FILE = maps/challenger/01_the_impossible_dream.txt
REQUIREMENTS = requirements.txt
FILES = drone.py parser.py simulation.py zone.py

all: banner install run

banner:
	@echo "**************************************"
	@echo "           	Fly-Ing                  "
	@echo "**************************************"

install: $(VENV)/bin/activate $(MLX)

$(VENV)/bin/activate: $(REQUIREMENTS)
	@echo "Initiallizing virtual environment and installing dependecies"
	python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
	touch $(VENV)/bin/activate

run: install
	@echo "Runnign..."
	$(PYTHON) $(MAIN) $(CONFIG_FILE)

debug: install
	@echo "debugging..."
	$(PYTHON) -m pdb $(MAIN_FILE) $(CONFIG_FILE)

lint:
	@echo "Linters"
	@echo "- Check flake8..."
	$(PYTHON) -m flake8 $(MAIN) $(FILES)
	@echo "- Check mypy..."
	$(PYTHON) -m mypy --follow-imports=skip $(MAIN) $(FILES) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	@echo "Linting strictly..."
	@echo "- Running flake8..."
	$(PYTHON) -m flake8 $(MAIN) $(FILES)
	@echo "- Running mypy..."
	$(PYTHON) -m mypy --follow-imports=skip $(MAIN) $(FILES) --strict

clean:
	@echo "Cleaning temporary files..."
	@rm -rf __pycache__ .mypy_cache
	@rm -rf $(VENV)
	

.PHONY: all lint clean run