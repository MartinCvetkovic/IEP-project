FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/applicationAuth.py ./applicationAuth.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py
COPY ./requirements.txt ./requirements.txt
COPY ./roleCheck.py ./roleCheck.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "./applicationAuth.py"]
