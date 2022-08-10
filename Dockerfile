FROM python:3.9.5
WORKDIR /code
ENV MINIO_HOST=myminio
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . .
CMD ["python3", "app.py"]
