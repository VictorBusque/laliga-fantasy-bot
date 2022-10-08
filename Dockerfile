from python:3.8-slim-buster

RUN apt-get update &&\
    apt-get install -y locales &&\
    dpkg-reconfigure locales &&\
    sed -i '/es_ES.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG es_ES.UTF-8
ENV LANGUAGE es_ES:es  
ENV LC_ALL es_ES.UTF-8  


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

ENTRYPOINT ["python"]
CMD ["run.py"]
