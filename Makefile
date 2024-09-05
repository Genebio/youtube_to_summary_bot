# Variables
FUNCTION_NAME = youtube_to_summary_bot
REGION = europe-west10
ENTRY_POINT = telegram_bot
RUNTIME = python311
VENV_DIR = venv

# Deploy the Google Cloud Function
.PHONY: deploy
deploy:
	gcloud functions deploy $(FUNCTION_NAME) \
		--region $(REGION) \
		--runtime $(RUNTIME) \
		--gen2 \
		--entry-point $(ENTRY_POINT) \
		--allow-unauthenticated

# Read logs from Google Cloud Function
.PHONY: logs
logs:
	gcloud functions logs read $(FUNCTION_NAME) --region $(REGION)
	# gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=youtube-to-summary-bot" --limit=100

lo.PHONY: venv
logs-local:
	functions-framework --target=telegram_bot

# Explicitly use the full path to Python 3.11
PYTHON_VERSION = /usr/local/bin/python3.11

# Create a virtual environment and install dependencies
.PHONY: venv
venv: requirements.txt
	$(PYTHON_VERSION) -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Compile the requirements.txt file from requirements.in using pip-compile
.PHONY: requirements.txt
requirements.txt: requirements.in
	$(PYTHON_VERSION) -m pip install pip-tools
	$(PYTHON_VERSION) -m piptools compile requirements.in