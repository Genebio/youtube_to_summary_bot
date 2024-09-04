# Variables
FUNCTION_NAME = youtube_to_summary_bot
REGION = europe-west10
ENTRY_POINT = telegram_bot
RUNTIME = python311

# Deploy the Google Cloud Function
.PHONY: deploy
deploy:
	gcloud functions deploy $(FUNCTION_NAME) \
		--region $(REGION) \
		--runtime $(RUNTIME) \
		--gen2 \
		--entry-point $(ENTRY_POINT) \
		--allow-unauthenticated

.PHONY: logs
logs:
	gcloud functions logs read $(FUNCTION_NAME) --region $(REGION)