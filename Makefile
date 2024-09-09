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
	ruff check handlers.py main.py

.PHONY: venv
deploy:
	ruff check handlers.py main.py
	docker build -t gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest .
	docker push gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest
	gcloud run deploy $(BOT_NAME) \
	--image gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest \
	--platform managed \
	--region $(REGION) \
	--allow-unauthenticated

.PHONY: logs-err
logs-err:
	gcloud logging read \
		'resource.type="cloud_run_revision" AND logName="projects/telegram-bots-9471/logs/run.googleapis.com/stderr"' \
		--limit=50 \
		--freshness=1h

.PHONY: logs-out
logs-out:
	gcloud logging read \
		'resource.type="cloud_run_revision" AND logName="projects/telegram-bots-9471/logs/run.googleapis.com/stdout"' \
		--limit=50 \
		--freshness=1h