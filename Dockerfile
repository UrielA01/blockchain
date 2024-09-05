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

CMD ["python3", "src/server.py"]
EXPOSE 5000