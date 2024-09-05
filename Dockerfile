FROM python:3.10
LABEL authors="urielazar"

WORKDIR /app
COPY requirements.txt /app/
COPY ./src /app/src
COPY ./mem_pools /app/mem_pools
RUN pip3 install -r requirements.txt

ENV PORT=5000
ENV HOST=0.0.0.0
ENV PYTHONPATH="/app"

# run.sh is used to run the cleanup script in server.py
RUN echo "#!/bin/bash \n exec python3 src/server.py \$PORT \$HOST" > ./run.sh
RUN chmod +x ./run.sh
CMD ["./run.sh"]
EXPOSE 5000