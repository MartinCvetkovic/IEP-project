FROM python:3

RUN mkdir -p /opt/src/applications/employee
WORKDIR /opt/src

COPY applications/employee/applicationEmpl.py ./applications/employee/applicationEmpl.py
COPY applications/configuration.py ./applications/configuration.py
COPY applications/models.py ./applications/models.py
COPY ./requirements.txt ./requirements.txt
COPY ./roleCheck.py ./roleCheck.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src"

ENTRYPOINT ["python", "applications/employee/applicationEmpl.py"]
