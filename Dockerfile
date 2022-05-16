FROM mcr.microsoft.com/playwright/python:v1.22.0-focal
WORKDIR /app/
COPY . /app/
RUN pip install poetry
RUN	poetry config virtualenvs.create true
RUN	poetry config virtualenvs.in-project true
RUN	poetry install
RUN	poetry run python setup.py install
RUN playwright install
CMD poetry run python scanner/app.py
