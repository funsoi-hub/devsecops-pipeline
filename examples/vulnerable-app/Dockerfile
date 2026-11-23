# [Trivy] end-of-life base image, runs as root, no healthcheck: all intentional
FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
