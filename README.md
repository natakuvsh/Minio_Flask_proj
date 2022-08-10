<a name="intro"></a>
### 1. Introduction
Project made by Natalia Zharikova.
Alows to upload data to Minio bucket and get it within the Flask app

<a name="prereq"></a>
### 2. Prerequisites
- Python 3.7 or greater
- Docker 19.03 or greater
- Git 2.28 or greater
- Postgres 13 or greater
- Docker-compose 1.26 or greater

To install `docker-compose` visit the following [link](https://docs.docker.com/compose/install/).


<a name="desc"></a>
### 3. Description
In this project we implemented a dockerized service to process users data, which is equivalent to **Level 3**. It extracts the users data `(first_name, last_name, birthts)` from `minio` and finds the image path `img_path` 
for each user (if any) and then stores the intermediate results in `minio`. Finally all processed data is then migrated to `postgres` database. The service 
periodically processes the data inside `minio/srcdata`. You can interact with the service with a `flask` server that works on two endpoints
- POST http://localhost:5000/data - Manually run data processing in `minio/src_data`
- GET http://localhost:5000/data - retrieves all records from `postgres` DB in JSON format:
```
{
  user_id1: {
      first_name: 'example_first_name',
      last_name: 'example_last_name',
      birthts: 'example_birthts',
      img_path: 'example_img_path'
  },
  user_id2: {
      ...
  },
  ...
}
```
You can apply the following filters for the retrieved data:
- `is_image_exists`=True/False
  - if True, it retrieves the records of all users that *have* an image.
  - if False, it retrieves the records of all users that * do not have* an image.
  - if it was not specified, it retrieves the records of all users in the database.
- `min_age`=MIN_AGE - if specified, it retrieves the records of all users that has a minimum age of `MIN_AGE`
- `max_age`=MAX_AGE - if specified, it retrieves the records of all users that has a maximum age of `MAX_AGE`

To apply a filter you can proved them as tags in the url, for example: [http://localhost:5000/data?min_age=35&max_age=40](http://localhost:5000/data?min_age=35&max_age=40)
returns the records of all users that age is between 35 and 40.


<a name="install"></a>
### 4. Installation and Running
Clone this repo to your local machine. `cd` to the directory of the repo `provectus-internship-task` and run:
```
sudo docker-compose up --build -d
```
Wait until you get an error `PermissionError: [Errno 13] Permission denied` from `pg_admin`.
The reason of the error is because you need to give access to minio and pgadmin directories. On the same terminal type `Ctrl+C` and then run:
```
sudo chmod 777 minio/
sudo chmod 777 pgadmin/
sudo chmod 777 postgres-data/
```
Now you need to restart the `docker-compose` containers you ran before. On the same terminal run:
```
sudo docker-compose down
sudo docker-compose up -d
```
Now the service is up and running on [http://localhost:5000/](http://localhost:5000/).


<a name="logic"></a>
### 5. Logic
When you run the command `sudo docker-compose up --build -d` the script `app.py` get excuted. First, it schedules a scheduler to keep
running the instance every 15 minutes. Then it initiates the `minioClient` and `postgres` instances and then it runs the flask app. 
Now, for each `GET` request to the server, the `app.py` calls a function from `main.py` that retrieves the data from `postgres` DB. And 
for each `POST` request, the `app.py` calls another function from `main.py` to manually process the data.

When `main.py` processes the data, it connects with the `minioClient` and `postgres` to read the files and then store the results in `output.csv`
inside `minio` and also in the `postgres` database.

<a name="notes"></a>
### 6. Important Notes

- After you run the `docker-compose`, to manually add data to `srcdata` you need to `cd` to `provectus-internship-task/minio` and run the following command 
to give access to `srcdata` so you can paste your data there:
```
sudo chmod 777 srcdata/
```
  Now you can paste data inside the `srcdata` and test the code.


- To see the data stored in `postgres` you need to open [http://0.0.0.0:5050/browser/](http://0.0.0.0:5050/browser/) in your browser. You will be prompted to 
enter a master password. If you haven't changed it before it should be `postgres`. Then, you need to create a server. Put any name you want, but make sure 
to put the following credintials correctly:
```
Host = db
Port = 5432
Maintenance database = postgres
Username = postgres
Password = postgres
```

- In the `Dockerfile` I added the `ENV` variables for the configuration of the connections for `minio` and `postgres`. Although these 
environment variables already exist in the `docker-compose.yml` file, but they're only available during the build of the image but not after the image is built.
Now, to run the code localy, you need to remove the `web-service` from the `docker-compose.yml`. Then run the `sudo docker-compose up --build`. Before you run the app, you need to manually install the libraries inside `requirements.txt` since docker won't download it for local use. Now you can run the flask app `python3 app.py` in the `provectus-internship-task` directory. 

- I added a `.env` file to configure the connection locally. The code is set up so that, if it's not running on docker, it will
automatically use the local `.env` file for the connections. In case you want use different configurations when testing locally, 
you can modify any of the env variables in the `.env` file.

- Note that the `.env` should not be uploaded to the repo for saftey and security reasons. However, for the purpose of this internship, I uploaded
file to let you see all the practices I've followed.
