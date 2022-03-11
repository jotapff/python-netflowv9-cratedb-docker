#docker build -t netflow_collector-py:latest ./
FROM python:3.9.10-bullseye

ENV HOST_IP="0.0.0.0"
ENV HOST_PORT=2055
#ENV DB_NAME="netflowDB"
ENV Debug="True"
ENV DB_HOST="http://cratedb01:4200/ http://cratedb02:4200/ http://cratedb03:4200/"
ENV DB_ROOT_USER="root"
ENV DB_ROOT_PASS=" " 
ENV GET_DST_COUNTRY="False"
ENV ADD_DNS_NAME="False"

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "netflowCollector.py"]
#CMD ["python", "test/cratedb.py"]

