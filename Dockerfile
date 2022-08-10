FROM python:3.9.5
WORKDIR /code
ENV FLASK_APP=app.py
ENV MINIO_ACCESS_KEY=admin
ENV MINIO_SECRET_KEY=password
ENV MINIO_HOST=myminio
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . .
CMD ["python3", "app.py"]