FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install build-essential cmake -y && \
    apt-get install libopenblas-dev liblapack-dev -y && \
    apt-get install libx11-dev libgtk-3-dev -y

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "faceSwap.py" ]
