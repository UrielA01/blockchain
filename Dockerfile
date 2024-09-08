FROM python:3.10
LABEL authors="urielazar"

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY ./src /app/src
COPY ./mem_pools /app/mem_pools

ENV PORT=5000
ENV PYTHONPATH="/app"

CMD ["python3", "src/server.py"]
EXPOSE 5000