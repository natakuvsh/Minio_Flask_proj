import os
from utils import *
import pandas as pd
from minio.select import SelectRequest, CSVInputSerialization, CSVOutputSerialization


class DataManager:
    """
    A class to operate with Minio Client, process data, upload and delete objects in Minio buckets
    """

    data = {}

    def __init__(self, minio_client, src_data_path: str, processed_data_path: str):
        """
        Create a DataManager class which operates Minio, and path to its buckets
        :param initial_src_data_path: the path to the source data on local machine
        :param initial_processed_data_path: the path to the processed data on local machine
        :param src_data_path: the path to the Minio bucket with the source data
        :param processed_data_path: the path to the Minio bucket with processed data
        """
        self.src_data_path = src_data_path
        self.processed_data_path = processed_data_path
        self.minioClient = minio_client

    @classmethod
    def update_data(cls, updated_data: dict):
        """
        Updates the self.data variable, which allows to use it
        for get_average_age and get_data methods
        :param updated_data: data after processing
        """
        cls.data = updated_data

    def process_data(self):
        """
        Process the data from 'self.src_data_path' and add the results to 'self.processed_data_path'.
        """
        # Get lists of csv files and png files
        csv_files, image_files = self.get_files()
        # Create an empty dict and append data to it
        users_data = {}
        for csv_file in csv_files:
            first_name, last_name, birthts = self.read_csv_file_from_minio(csv_file)
            user_id = csv_file.split('.')[0]
            image_names = [image.split('/')[1].split('.')[0] for image in image_files]
            try:
                index = image_names.index(f'{user_id}')
                img_path = image_files[index]
            except ValueError:
                img_path = ""
            user_data = {
                user_id: {
                    'first_name': first_name,
                    'last_name': last_name,
                    'birthts': birthts,
                    'img_path': img_path,
                }
            }
            users_data.update(user_data)
        # Update self.data file with new user_data
        self.update_data(users_data)

        return users_data

    def update_output_file(self):
        """
        Updates output.csv file in the processed data bucket
        """
        # Get dict of users info
        print('Reading data...')
        users_data_dict = self.process_data()
        # Create a dataframe from users info
        df = pd.DataFrame(users_data_dict).T.rename_axis('user_id').reset_index()
        # Save dataframe as csv file
        df.to_csv('temp.csv', index=False)
        # Delete old output.csv file and upload new one to the bucket
        self.minioClient.remove_object(self.processed_data_path, 'output.csv')
        self.minioClient.fput_object(self.processed_data_path, 'output.csv', 'temp.csv')
        os.remove('temp.csv')

    def get_files(self):
        """
        Gets the names of the csv and image files from the 'self.src_data_path' path
        :return: two lists of files paths (csv_files, image_files)
        """
        # Get list of all files from the bucket
        files = [file.object_name for file in self.minioClient.list_objects(self.src_data_path)]
        # Get list of csv files
        csv_files = [file for file in files if file.endswith('.csv')]
        # Get list of png files
        image_files = [f"{self.src_data_path}/{file}" for file in files if file.endswith('.png')]

        return csv_files, image_files

    def get_average_age(self, **filters):
        """
        Calculates the average age of the users according to given filters
        :param filters: a dictionary that contains the filters to apply to the data.
        :return: float of average age
        """
        # Get data according to the applied filters
        print('Counting the average age of the users...')
        data = self.get_data(**filters)
        # Calculate average
        sum = 0
        for value in data.values():
            sum += millisec_to_age(float(value['birthts']))
        average = sum/len(data)

        return average

    def get_data(self, **filters):
        """
        Retrieves the users data according to the filters applied
        :param filters: a dictionary that contains the filters to apply to the data.
        Keys for filters dict:
        'is_image_exists' - False if user does not have an image, True if user has an image
        'min_age' - lower border of the age of the users
        'max_age' - upper border of the age of the users
        :return: dict :
        {
            user_id1: {
                first_name: 'first_name',
                last_name: 'last_name',
                birthts: 'birthts',
                img_path: 'img_path'
            },
            user_id2:{
                ...
            }
        }
        """
        # Check if self.data is not empty and use it
        if self.data:
            data = self.data
        else:
            data = self.process_data()

        # Apply is_image_exists filter
        if filters['is_image_exists'] != -1:
            if filters['is_image_exists'].lower() == 'true':
                data = {key: value for key, value in data.items() if value['img_path'] != ''}
            elif filters['is_image_exists'].lower() == 'false':
                data = {key: value for key, value in data.items() if value['img_path'] == ''}

        # Apply min_age filter
        if filters['min_age'] != -1:
            minimum_age = filters['min_age']
            data = {key: value for key, value in data.items() if millisec_to_age(float(value['birthts'])) >= minimum_age}

        # Apply max_age filter
        if filters['max_age'] != -1:
            maximum_age = filters['max_age']
            data = {key: value for key, value in data.items() if millisec_to_age(float(value['birthts'])) <= maximum_age}

        # Check if there is data which matched our filters
        if data:
            return data
        else:
            return 'Could not find users, which match your filters. Please try another filters.'

    def read_csv_file_from_minio(self, file_name: str):
        """
        Reads a csv file from minio and returns its contents
        :param file_name: the name of the file to read from
        :return: the contents of the file as a list
        """
        with self.minioClient.select_object_content(
                self.src_data_path,
                file_name,
                SelectRequest(
                    "select * from S3Object",
                    CSVInputSerialization(),
                    CSVOutputSerialization(),
                    request_progress=True,
                ),
        ) as result:
            for data in result.stream():
                data = data.decode().replace('"','').split('\n')[1].split(',')
                return data



