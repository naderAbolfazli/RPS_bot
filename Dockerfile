FROM dockerproxy.bale.ai/python:3.7

WORKDIR /rps_root

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./ ./
CMD ["python", "RPS_bot.py"]
ENV PYTHONPATH /rps_root
