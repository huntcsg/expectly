FROM python:3.6.3-slim

WORKDIR /package
COPY dev_requirements.txt ./
RUN pip install -r dev_requirements.txt
COPY . ./

RUN pip install .[dev]

ENTRYPOINT [ "./bin/manage_entrypoint" ]
