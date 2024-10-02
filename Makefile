# Variables
BOT_NAME = youtube-to-summary-bot
PROJECT_ID = telegram-bots-9471
REGION = europe-west10


# Create a virtual environment and install dependencies
.PHONY: deps
deps: requirements.in
	uv pip compile -p 3.11 --no-cache --no-strip-extras requirements.in -o requirements.txt

.PHONY: venv
lint:
	ruff check --no-cache main.py apis/ config/ handlers/ utils/

.PHONY: venv
deploy:
	ruff check --no-cache main.py apis/ config/ handlers/ utils/
	docker build -t gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest .
	docker push gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest
	gcloud run deploy $(BOT_NAME) \
	--image gcr.io/$(PROJECT_ID)/$(BOT_NAME):latest \
	--platform managed \
	--region $(REGION) \
	--allow-unauthenticated

.PHONY: venv
stop:
	gcloud run services delete $(BOT_NAME) --region $(REGION)

.PHONY: venv
sql-connect:
	gcloud beta sql connect mybots-europe-west3 --user=postgres
