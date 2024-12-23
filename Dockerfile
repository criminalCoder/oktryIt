FROM python:3.10
WORKDIR /app
COPY . /app/
RUN apt update && apt upgrade -y
RUN pip install -r requirements.txt
RUN apt install git python-pip ffmpeg -y
CMD ["python", "bot.py"]
