#### Provectus Internship task by Natalia Zharikova

<a name="intro"></a>
### 1. Introduction
Project made by Natalia Zharikova.

Alows to upload data to Minio bucket and process it within the Flask app.

<a name="prereq"></a>
### 2. Prerequisites
- Python 3.9.5
- Docker 20.10.16 
- Git  2.37.0
- Docker-compose 1.29.2

<a name="desc"></a>
### 3. Description

# Preperations (made from docker-compose.yml)
1. Creating 'src-data' and 'processed-data' buckets in Minio
2. Upload source data to 'src-data' bucket 

# Data processing 

1. Reading CSV files from Minio 'src-data' bucket
2. Match images to users 
3. Aggregate data into a single CSV file
4. Removing existing output.csv file and uploading a new one to 'processed-data' bucket 

# Scheduling output.csv update 
Creating a BackgroundScheduler to update the output.csv file every 25 minute

# Serving the data
Web server implemented with following endpoints:

* `GET /data` - get all records from self.data variable in JSON format. Supports filtering by: is_image_exists = True/False, user min_age and max_age in years.
* `POST /data` - manually trigger reprocessing the source dataand updating output.csv file
* `GET /stats` - calculate and return the average age of users matching the filters (`is_image_exists=True/False`, `min_age`, `max_age`)

To apply a filter you can write them as tags in the url, for example: (http://localhost:8080/data?is_image_exists=false&min_age=25&max_age=40)
returns the records of all users that does not have images, with age is between 25 and 40 in Json format


<a name="install"></a>
### 4. Installation and Running
Clone this repo to your local machine. Run:
```
cd ProvectusInternship_NataliaZharikova-master
```
```
docker-compose up --build -d
```

Now the Flask app is up and running on [http://0:0:0:0:8080/](http://localhost:8080/).
Minio is up and running on (http://localhost:9001/)

<a name="logic"></a>
### 5. Logic

After running `docker-compose up --build -d` command:

1. MinIO Client creates 'processed-data' and 'src-data' buckets, sets their policy to public.
2. MinIO Client uploads initial files from '02-src-data' to 'scr-data' bucket.
3. Required packages are installed from 'requirements.txt' file.
4. App.py initiates minio and DataManager.
5. Starts the BackgroundScheduler, which allows to update output.csv file every 25 minutes.
6. Runs initial upload of output.csv file to 'processed-data' bucket and stores a dict with users info in DataManager self.data variable.
7. For each `GET /data` request to the server, the `app.py` calls a function from DataManager class that retrieves the data from self.data variable and applies filters if needed.  
8. For each `POST /data` request, the `app.py` calls another function from DataManager to manually process the data.
9. For each `GET /stats` request, the `app.py` calls another function from DataManager to get the average age of users according to the filters applied.


