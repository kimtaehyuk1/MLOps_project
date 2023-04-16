# docker build --no-cache -t agent:1.0 ./model_agent
# botocore.exceptions.NoCredentialsError: Unable to locate credentials 해결
# docker run -itd --name agent_model -v ~/.aws/:/root/.aws:ro --env AWS_PROFILE=default agent:1.0 
# docker logs agent_model
# docker container stop agent_model
# docker container rm agent_model
# docker image ls
# docker image rm agent:1.0
FROM python:3.9.16-bullseye

WORKDIR /model_agent2

COPY requirements.txt /model_agent2

RUN pip3 install -r requirements.txt

COPY insert_db.py /model_agent2

ENTRYPOINT [ "python" ]
CMD ["insert_db.py"]