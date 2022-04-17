import logging
from pymongo import MongoClient

class TemperatureReadings():
    """"" CRUD operations for Temperature Readings in MongoDB """

    def __init__(self, username: str, password: str) -> None:
        self.client = MongoClient('mongodb://%s:%s@localhost:27017' % (username, password))
        self.database = self.client['Weather']
        self.collection = self.database['Temperature']


    def insert_temperatures(self, time_stamp, temp_f, humidity):
        """ Add new records to collection """
        document = {
            'Timestamp': time_stamp,
            'Temperature': temp_f,
            'Humidity': humidity,
        }

        try:
            return self.collection.insert_one(document)
        except Exception as e: 
            logger.error('Failed to insert temperature '+ str(e))

    def read(self, query, projection=None):
        """ Read records from collection """
        if query is not None:
            try:
                return self.collection.find(query)
            except Exception as e: 
                logger.error('Failed to query ' + str(e))

    def update(self, query, data):
        """ Update records from collection """
        if query is not None and data is not None:
            try:
                return self.collection.update_one(query, data)
            except Exception as e: 
                logger.error('Failed to update ' + str(e))

    def delete(self, query):
        """ Delete records from collection """
        if query is not None:
            try:
                return self.collection.delete_one(query)
            except Exception as e: 
                logger.error('Failed to delete ' + str(e))