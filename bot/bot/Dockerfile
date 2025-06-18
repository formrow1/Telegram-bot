FROM python:3.13.2-bookworm
ENV TZ="Europe/Moscow"
# tzdata for timzone
RUN apt update -y
RUN apt install -y tzdata
# Go to app directory
WORKDIR /usr/src/app
RUN cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime

COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /usr/src/app/log

COPY ./src/* . 
COPY ./*.bot_token .

CMD [ "python", "./main.py" ]