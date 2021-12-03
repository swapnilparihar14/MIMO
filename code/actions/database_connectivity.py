import mysql.connector
import logging
import pandas as pd
from .connections import LOGGER_FORMAT, DB_PASSWORD


class DBConnection:

    def __init__(self):
        """ Constructor """
        self.log = logging.getLogger(self.__class__.__name__)
        file_handler = logging.FileHandler(f'{self.__class__.__name__}.log')
        formatter = logging.Formatter(LOGGER_FORMAT)
        file_handler.setFormatter(formatter)
        self.log.addHandler(file_handler)
        try:
            self.db = mysql.connector.connect(host="rasa-db-1.cnlv0osh7hey.us-east-2.rds.amazonaws.com",
                                              user="admin",
                                              passwd=DB_PASSWORD,
                                              database="Rasa_Patient_DB")
            self.cursor = self.db.cursor()
        except Exception as e:
            self.log.error(f"DB connection Failed.\nError {e}")

    def execute_query(self, query):
        """
        Excecute the MYSQL query with the help of the cursor
        :param query: Input query
        :return: None
        """
        try:
            self.cursor.execute(query)
            self.db.commit()
        except Exception as e:
            self.log.error(f"{query} Failed.\nError {e}")

    def add_patient_info(self, email, phone, patient_name, address):
        """
        Adds new Patient information to the database
        :param email: Email ID
        :param phone: Phone number
        :param patient_name: Name to call the patient
        :param address: City where the patient lives
        :return: None
        """
        query = f"""INSERT INTO patient_records (email,phone,patient_name,address) 
                    VALUES ("{email}","{phone}","{patient_name}","{address}");"""
        self.execute_query(query)

    def increment_patient_variables(self, email, variable):
        """
        Update Patient information
        :param email: Patient's email_id
        :param variable: variable_to_update
        :return:
        """
        query = f"""UPDATE patient_records 
        SET {variable} = {variable} + 1 
        WHERE email ="{email}" """
        self.execute_query(query)

    def add_doctor_info(self):
        """
        Adds doctor records to the table
        :return: None
        """
        df = pd.read_csv("doctor_records.csv")
        df['address'] = "101 Doctor's Avenue, " + df['city'].astype(str) + ", United States"
        for index, row in df.iterrows():
            query = f"""INSERT INTO doctor_records (email,phone,doctor_name,city,address) 
                        VALUES ("{row['email']}","{row['phone']}","{row['name']}","{row['city']}","{row['address']}");"""
            self.execute_query(query)

    def get_doctor_info(self, city):
        """
        Returns the doctor's information for a particular city
        :param city: Name of the city
        :return: doctor's information
        """
        query = f"""SELECT * FROM doctor_records WHERE city="{city}" LIMIT 5;"""
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        if records:
            text = "Here is the list of doctors available in your area:\n\n"
            for record in records:
                text += f"""Doctor Name: {record[3]} \nEmail ID: {record[1]} \nPhone: {record[2]} \nAddress: {record[4]} \n\n"""
        else:
            text = f"Sorry we don't have a medical practitioner on records in {city}."
        return text

    def get_patient_records(self, email):
        """
        Get records for a particular patient
        :param email: Patient's email ID
        :return: Patient's record as a dictionary
        """
        cursor = self.db.cursor(dictionary=True)
        query = f"""SELECT * FROM patient_records WHERE email="{email}" LIMIT 1;"""
        cursor.execute(query)
        return cursor.fetchone()
