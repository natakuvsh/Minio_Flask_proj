from minio import Minio
from data_manager import *
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler


src_data_path = 'src-data'
processed_data_path = 'processed-data'
initial_src_data_path = '02-src-data'
initial_processed_data_path = 'processed_data'

minio = Minio(
    'minio' + ":9000",
    access_key='admin',
    secret_key='password',
    secure=False
)

app = Flask(__name__)
data_manager = DataManager(minio_client=minio, src_data_path=src_data_path,
                           processed_data_path=processed_data_path)
data_manager.update_output_file()

scheduler = BackgroundScheduler()
scheduler.add_job(data_manager.update_output_file, 'interval', seconds=1500)
scheduler.start()


@app.route("/data", methods=['POST'])
def process_data():
    data_manager.update_output_file()
    return jsonify("Output.csv file has been updated successfully!")


@app.route("/data", methods=['GET'])
def get_data():
    is_image_exists = request.args.get('is_image_exists', -1)
    min_age_years = request.args.get('min_age', -1, type=int)
    max_age_years = request.args.get('max_age', -1, type=int)

    data = data_manager.get_data(is_image_exists=is_image_exists, min_age=min_age_years, max_age=max_age_years)
    return jsonify(data)


@app.route("/stats", methods=['GET'])
def get_stats():
    # Read the filters
    is_image_exists = request.args.get('is_image_exists', -1)
    min_age_years = request.args.get('min_age', -1, type=int)
    max_age_years = request.args.get('max_age', -1, type=int)

    average_years = data_manager.get_average_age(is_image_exists=is_image_exists, min_age=min_age_years,
                                                 max_age=max_age_years)

    return f"Average age is {average_years:.2f} years"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
