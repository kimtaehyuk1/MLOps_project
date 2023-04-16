FROM python:3.9.16-bullseye AS builder

WORKDIR /backend

COPY . /backend

RUN pip3 install -r requirements.txt

ENV FLASK_APP "service"
ENV FLASK_RUN_PORT 8000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 8000

ENTRYPOINT [ "flask" ]
CMD ["run"]