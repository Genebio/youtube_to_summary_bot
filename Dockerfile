FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py handlers.py config.py /app/

EXPOSE 8080

ENV PORT 8080

CMD ["python", "main.py"]