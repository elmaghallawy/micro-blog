FROM python:3.8-alpine


ENV FLASK_APP micro_blog.py
ENV FLASK_CONFIG docker

RUN adduser -D micro_blog
USER micro_blog

WORKDIR /home/micro_blog


COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY micro_blog.py config.py boot.sh ./

# runtime configurations
EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]