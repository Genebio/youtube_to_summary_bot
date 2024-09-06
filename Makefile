# Variables
BOT_NAME = youtube_to_summary_bot
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

.PHONY: build
build:
	docker build -t gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest .

.PHONY: push
push:
	docker push gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest

.PHONY: deploy
deploy:
	gcloud run deploy $(BOT_NAME) \
	--image gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest \
	--platform managed \
	--region $(REGION) \
	--allow-unauthenticated
