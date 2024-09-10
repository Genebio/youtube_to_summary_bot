# Variables
BOT_NAME = youtube-to-summary-bot
PROJECT_ID = telegram-bots-9471
REGION = europe-west10
VENV_DIR = venv
PYTHON = /usr/local/bin/python3.11


# Create a virtual environment and install dependencies
.PHONY: venv
venv: requirements.in
	$(PYTHON) -m pip install pip-tools
	$(PYTHON) -m piptools compile requirements.in
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

.PHONY: venv
lint:
	ruff check main.py apis/ config/ handlers/ utils/

.PHONY: venv
deploy:
	ruff check main.py apis/ config/ handlers/ utils/
	docker build -t gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest .
	docker push gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest
	gcloud run deploy $(BOT_NAME) \
	--image gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest \
	--platform managed \
	--region $(REGION) \
	--allow-unauthenticated
