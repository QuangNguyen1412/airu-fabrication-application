##############################################################
# Name: AirUDeviceManager.py
# Description: This class is made to interact with a google spread sheet that help managing AirU boards,
# firmware version, PM sensors and more importantly to show the pair of AirU board and PM sensor
# Author: Quang Nguyen
# Author Email: ntdquang1412@gmail.com
# Date: June 10th, 2019
# Google Sheets API v4.
# client email: airudevicemanager@airudevicemanager.iam.gserviceaccount.com
# AirU https://docs.google.com/spreadsheets/d/1eFpUv7EhIoQ9ztsbGeJe5pxPL9lmTTv1u2OkCFY9Z7E/edit?usp=sharing
# Tetrad https://docs.google.com/spreadsheets/d/1lNxwm1XUpYNcJIXxaP1tOduslou_lqlG9EJgXM6Dhdc/edit?usp=sharing

import gspread
import os, sys
import pymongo
import pprint
import datetime

from sshtunnel import SSHTunnelForwarder
from gspread import CellNotFound
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import errors
from google.cloud import bigquery

AIRU_DEVICE_SHEET = "AirUDevices"
TETRA_DEVICES = "Tetra devices"
HISTORY_SHEET_NAME = "History"
APP_PATH = os.path.dirname(os.path.realpath(__file__))
CREDENTIAL_PATH = APP_PATH + os.path.sep + 'credential'
JSON_PATH = CREDENTIAL_PATH + os.path.sep + 'scottgale-bigquery-secret.json'
PROJECT_ID = 'scottgale'
DATA_SET_ID = 'airu_hw_dataset'
BOARD_TABLE_ID = 'boards'
PRODUCT_TABLE_ID = 'products'
SENSOR_TABLE_ID = 'sensors'
HISTORY_TABLE_ID = 'pair_history'

boardsSchema = [
    bigquery.SchemaField("mac_addr", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("fw_version", "STRING"),
    bigquery.SchemaField("broken_stat", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("available_stat", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("date_create", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("date_update", "DATE", mode="REQUIRED"),
]

sensorSchema = [
    bigquery.SchemaField("sensor_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("broken_stat", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("available_stat", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("date_create", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("date_update", "DATE", mode="REQUIRED"),
]

productSchema = [
    bigquery.SchemaField("serial_number", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("pair_info", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("mac_addr", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("sensor_id", "STRING", mode="NULLABLE"),
                         ],
                         ),
    bigquery.SchemaField("user_info", "RECORD", mode="REPEATED",
                         fields=[
                             bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("first_name", "STRING", mode="NULLABLE"),
                             bigquery.SchemaField("last_name", "STRING", mode="NULLABLE"),
                         ],
                         ),
    bigquery.SchemaField("date_create", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("date_update", "DATE", mode="REQUIRED"),
]


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AirUDeviceManagerClass(object):
    def __init__(self, google_json_file, g_spread_sheet):
        scope = ['https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/feeds']
        script_dir = os.path.dirname(os.path.realpath(__file__))
        credential_json_path = script_dir + os.path.sep + 'credential' + os.path.sep + google_json_file
        print('credential_json_path:', credential_json_path)
        print('isfile:', os.path.isfile(credential_json_path))
        creds = ServiceAccountCredentials.from_json_keyfile_name(credential_json_path, scope)
        client = gspread.authorize(creds)
        self._history_sheet = client.open(g_spread_sheet).worksheet(HISTORY_SHEET_NAME)
        self.airu_mac_col_number = self._history_sheet.find("AirU MAC").col
        self.pm_mac_col_number = self._history_sheet.find("PM MAC").col
        self.sn_col_number = self._history_sheet.find("Serial").col

    def make_new_serial(self, airu_mac, pm_mac):
        print(airu_mac, pm_mac)
        max_rows_int = len(self._history_sheet.get_all_values())
        # serial_col_content = self._history_sheet.col_values(self.sn_col_number)
        i = 0
        max_rows = str(max_rows_int)
        print(max_rows)
        if max_rows_int < 9:
            serial_number = "SN000" + max_rows
        elif max_rows_int < 99:
            serial_number = "SN00" + max_rows
        elif max_rows_int < 999:
            serial_number = "SN0" + max_rows
        else:
            serial_number = "SN" + max_rows
        print("Make new serial", serial_number)
        # try:
        #     # Try to clear the previous pair of PM sensor
        #     existing_pm_mac_rows = self._history_sheet.findall(airu_mac)
        #     for cell in existing_pm_mac_rows:
        #         self._history_sheet.update_cell(cell.row, self.pm_mac_col_number, "")
        #         self._history_sheet.update_cell(cell.row, self.sn_col_number, "")
        # except CellNotFound:
        #     print("Found Unused PM sensor, this is good")
        # try:
        #     needed_row = self._history_sheet.find(airu_mac.upper()).row
        #     self._history_sheet.update_cell(needed_row, self.pm_mac_col_number, pm_mac.upper())
        #     self._history_sheet.update_cell(needed_row, self.sn_col_number, serial_number.upper())
        # except CellNotFound:
        #     print("Adding new row")
        #     self._history_sheet.update_cell(max_rows_int + 1, self.airu_mac_col_number, airu_mac.upper())
        #     self._history_sheet.update_cell(max_rows_int + 1, self.pm_mac_col_number, pm_mac.upper())
        #     self._history_sheet.update_cell(max_rows_int + 1, self.sn_col_number, serial_number.upper())

        print("Adding new row")
        max_rows_int = max_rows_int + 1
        self._history_sheet.update_cell(max_rows_int, self.airu_mac_col_number, airu_mac.upper())
        self._history_sheet.update_cell(max_rows_int, self.pm_mac_col_number, pm_mac.upper())
        self._history_sheet.update_cell(max_rows_int, self.sn_col_number, serial_number.upper())

    def update_airu_mac(self, airu_mac, fw_ver):
        print("Update airU mac" + airu_mac)
        try:
            existing_mac_row = self._history_sheet.find(airu_mac).row
            print(airu_mac, "Is already in database at row ", existing_mac_row)
        except CellNotFound:
            print("Cell is not found, going to add new row")
            max_rows = len(self._history_sheet.get_all_values())
            self._history_sheet.update_cell(max_rows + 1, self.airu_mac_col_number, airu_mac.upper())
            self._history_sheet.update_cell(max_rows + 1, self.firmware_version_col_number, fw_ver)
        # End try
# End of class

class MongoDbManagerClass(object):
    def __init__(self, db_user, db_pass):
        # server.start()
        authenticate_string = "mongodb+srv://{}:{}@airudevicesmanager-ckvk1.gcp.mongodb.net/test?retryWrites=true&w=majority"
        myclient = pymongo.MongoClient(authenticate_string.format(db_user, db_pass))

        # myclient = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
        mydb = myclient[MONGO_DB]
        try:
            # mydb.authenticate(db_user, db_pass)
            self._boardsCollection = mydb.boards
            self._devicesCollection = mydb.devices
            self._sensorsCollection = mydb.sensorStatus
            self.today = datetime.datetime.today()
            cur = list(self._devicesCollection.find())
        except errors.OperationFailure:
            raise AuthenticationError("Login failed " + db_user + "/" + db_pass)

    def _update_boards_availability(self, airu_mac, availability):
        data = list(self._boardsCollection.find({"mac_addr": airu_mac}))
        if not data:
            raise BoardMacAddressNotFound(airu_mac + " Not found")
        else:
            self._boardsCollection.update_one({"mac_addr": airu_mac}, {"$set": {"availability": availability}})

    def _update_boards_broken_status(self, airu_mac, broken):
        data = list(self._boardsCollection.find({"mac_addr": airu_mac}))
        if not data:
            raise BoardMacAddressNotFound(airu_mac + " Not found")
        else:
            self._boardsCollection.update_one({"mac_addr": airu_mac}, {"$set": {"broken": broken}})

    def update_boards_info(self, airu_mac, fw_ver, broken=False, availability=True):
        airu_mac = airu_mac.upper()
        print("Update airU mac" + airu_mac)
        data = list(self._boardsCollection.find({"mac_addr":airu_mac}))
        if data:
            print (data)
            self._boardsCollection.update_one({"mac_addr":airu_mac},  {"$set": { "fw_version": fw_ver,
                                                                                 "broken": broken,
                                                                                 "availability": availability},
                                                                       "$currentDate": { "date_modified": True } })
        else:
            print ("Create new document ", self.today)
            mydict = {"mac_addr": airu_mac,
                      "fw_version": fw_ver,
                      "broken":broken,
                      "availability": availability,
                      "date_created": self.today,
                      "date_modified": self.today}
            x = self._boardsCollection.insert_one(mydict)

    def update_sensor_info(self, sensor_id, broken=False, availability=True):
        print("Update sensor_id" + sensor_id)
        data = list(self._sensorsCollection.find({"sensorid":sensor_id}))
        if data:
            print (data)
            self._sensorsCollection.update_one({"sensorid":sensor_id},  {"$set": {"broken": broken,
                                                                                  "availability": availability},
                                                                       "$currentDate": { "date_modified": True }})
        else:
            print ("Create new document for sensor", self.today)
            mydict = {"sensorid": sensor_id,
                      "broken": broken,
                      "availability": availability,
                      "date_created": self.today,
                      "date_modified": self.today
                      }
            x = self._sensorsCollection.insert_one(mydict)

    def _set_pair_owner_email(self, serial, user_email):
        data = list(self._devicesCollection.find({"serial":serial}))
        result = self._devicesCollection.update_one({"serial": serial},
                                           {"$set": {"user_email": user_email,
                                                     "date_modified": self.today}})
        if not data:
            raise SerialNotFound(serial + " Not found")

    ##  Update/Create new board, sensorid pair and other information:
    #   board mac address
    #   sensor id
    #   device serial
    #   user email
    def update_board_sensor_pair(self, mac_addr, sensor_id, serial="", user_email=""):
        print("Update devices, latest record at index 0")
        data = list(self._devicesCollection.find({"serial":serial}))
        self.today = datetime.datetime.today()
        pair_info = {"mac_addr": mac_addr,
                     "sensorid": sensor_id,
                     "date_created": self.today}
        if data:
            latest_mac = data[0]["history"][0]["mac_addr"]
            latest_sensor_id = data[0]["history"][0]["sensorid"]
            if latest_mac != mac_addr:  # remove the latest one since we are updating new one
                self._update_boards_availability(latest_mac, True)

            if sensor_id != latest_sensor_id:  # remove the latest one since we are updating new one
                self.update_sensor_info(latest_sensor_id, availability=True)

            print (data)
            mac = list(self._devicesCollection.find({"history.mac_addr":mac_addr}))
            sensorid = list(self._devicesCollection.find({"history.sensorid":sensor_id}))
            if len(mac) > 0 and len(sensorid) > 0:
                print("Pair is already added, update owner")
                self._set_pair_owner_email(serial, user_email)
                return
            self._devicesCollection.update_one({"serial":serial},
                                               {"$push": { "history": {"$each":[pair_info],
                                                                           "$position":0}},
                                                "$set": {"user_email":user_email,
                                                         "date_modified": self.today}
                                                })
            self._update_boards_availability(mac_addr, False)
            self.update_sensor_info(sensor_id, availability=False)

        else:
            print("Making the next serial")
            serial_count = self._devicesCollection.count();
            if serial_count < 9:
                serial_number = "SN000" + str(serial_count+1)
            elif serial_count < 99:
                serial_number = "SN00" + str(serial_count)
            elif serial_count < 999:
                serial_number = "SN0" + str(serial_count)
            else:
                serial_number = "SN" + str(serial_count)
            print("Made new serial", serial_number)
            new_serial = {"serial":serial_number,
                          "history": [pair_info],
                          "user_email": user_email,
                          "date_modified": self.today
                          }
            x = self._devicesCollection.insert_one(new_serial)
            self._update_boards_availability(mac_addr, False)
            self.update_sensor_info(sensor_id, availability=False)

class BigQuerryDbManagerClass(object):
    """ A class to manipulate data from a bigquery infrastructure.
    PROJECT_ID = 'scottgale'
    DATA_SET_ID = 'airu_hw_dataset'
    BOARD_TABLE_ID = 'boards'
    PRODUCT_TABLE_ID = 'products'
    SENSORS_TABLE_ID = 'sensors'

    => 'boards' table schema
    mac_addr         fw_version       broken           availability     date_update
    31:AE:A4:EF:A9:F5 airu-version-2.0 False            True             None

    => 'products' table schema


    => 'sensors' table schema

    """
    def __init__(self, json_key):
        print(json_key)
        self._client = bigquery.Client.from_service_account_json(json_key)
        self._boards_table = self._client.get_table(self._client.dataset(DATA_SET_ID).table(BOARD_TABLE_ID))
        self._sensors_table = self._client.get_table(self._client.dataset(DATA_SET_ID).table(SENSOR_TABLE_ID))
        self._products_table = self._client.get_table(self._client.dataset(DATA_SET_ID).table(PRODUCT_TABLE_ID))
        self._history_table = self._client.get_table(self._client.dataset(DATA_SET_ID).table(HISTORY_TABLE_ID))

    def update_boards_availability(self, airu_mac, broken=False, availability=True):
        print("update_board_availability")
        query = ('UPDATE `{}.{}.{}` SET broken={}, availability={} WHERE mac_addr="{}"'
                 .format(PROJECT_ID, DATA_SET_ID, BOARD_TABLE_ID, broken, availability, airu_mac))
        query_job = self._client.query(query)  # API request - starts the query
        print(query_job.state)

    def _check_data_duplication(self, airu_mac):
        print("_check_data_duplication", airu_mac)
        rows = self._client.list_rows(self._boards_table, [bigquery.SchemaField("mac_addr", "STRING", mode="REQUIRED")])
        format_string = "{!s:<16} " * len(rows.schema)

        # query = ('SELECT * FROM scottgale.airu_hw_dataset.boards WHERE mac_addr="{}"'
        #          .format(airu_mac))
        # query_job = self._client.query(query)
        # rows = query_job.result()
        # Print row data in tabular format
        # format_string = "{!s:<16} " * len(rows.schema)
        for row in rows:
            mac_addr_data = row.get('mac_addr')
            print(mac_addr_data)
            if airu_mac.find(mac_addr_data) != -1:
                print("Found duplication")
                return True
        return False

    def insert_new_board(self, airu_mac, fw_version, broken=False, availability=True):
        print('insert new boards',airu_mac, fw_version)
        today = datetime.datetime.today()
        if self._check_data_duplication(airu_mac):
            print("Updating existing one!!")
            query = ('UPDATE `{}.{}.{}` SET fw_version="{}", broken={}, availability={}, date_update="{}" WHERE mac_addr="{}"'
                     .format(PROJECT_ID, DATA_SET_ID, BOARD_TABLE_ID, fw_version, broken, availability, today, airu_mac))
            query_job = self._client.query(query)  # API request - starts the query
            print(query_job.state)
        else:
            rows_to_insert = [
                {'mac_addr': airu_mac,
                'fw_version': fw_version,
                'broken': broken,
                'availability':availability,
                'date_update': today}
            ]
            errors = self._client.insert_rows(self._boards_table, rows_to_insert)  # API request
            print(errors)
            assert errors == []

    def add_new_product(self, airu_mac, sensorid, email=''):
        print('add_new_product')
        rows = self._client.list_rows(self._products_table, [bigquery.SchemaField("pair_info.mac_addr", "STRING", mode="REQUIRED")])
        format_string = "{!s:<16} " * len(rows.schema)
        for row in rows:
            mac_addr_data = row[0].get('f')[0].get('v')
            print(mac_addr_data)
            if airu_mac.find(mac_addr_data) != -1:
                print("Found airu_mac duplication")
                return True
        rows = self._client.list_rows(self._products_table, [bigquery.SchemaField("serial_number", "STRING", mode="REQUIRED")])
        serial_count = len(list(rows))
        print(serial_count)
        # Make new serial number
        if serial_count < 9:
            serial_number = "SN000" + str(serial_count + 1)
        elif serial_count < 99:
            serial_number = "SN00" + str(serial_count)
        elif serial_count < 999:
            serial_number = "SN0" + str(serial_count)
        else:
            serial_number = "SN" + str(serial_count)

        print(serial_number)
        # self._add_new_product(serial_number, airu_mac, sensorid, email)
        # self.add_sensor_info(sensorid)
        # self._product_pair_history(serial_number, airu_mac, sensorid)


    def _add_new_product(self, serial_number, airu_mac, sensorid, email=''):
        today = datetime.datetime.today()
        rows_to_insert = [
            {
                "serial_number": serial_number,
                'pair_info': {
                    'mac_addr': airu_mac,
                    'sensor_id': sensorid,
                },
                'user_info': {
                    'email': email,
                    'first_name': '',
                    'last_name': ''
                },
                'update_time_stamp': today
            }
        ]
        errors = self._client.insert_rows(self._products_table, rows_to_insert)  # API request
        print(errors)
        assert errors == []

    def _update_product_owner(self, serial_number, email, first_name='', last_name=''):
        today = datetime.datetime.today()
        query = (
            'UPDATE `{}.{}.{}` SET user_info.email="{}", user_info.first_name={}, user_info.last_name={}, update_time_stamp="{}" WHERE serial_number="{}"'
            .format(PROJECT_ID, DATA_SET_ID, PRODUCT_TABLE_ID, email, first_name, last_name, today, serial_number))
        query_job = self._client.query(query)  # API request - starts the query
        print(query_job.state)

    def _update_product_pair(self, serial_number, airu_mac, sensorid):
        today = datetime.datetime.today()
        query = (
            'UPDATE `{}.{}.{}` SET pair_info.mac_addr="{}", pair_info.sensor_id={}, update_time_stamp="{}" WHERE serial_number="{}"'
            .format(PROJECT_ID, DATA_SET_ID, PRODUCT_TABLE_ID, airu_mac, sensorid, today, serial_number))
        query_job = self._client.query(query)  # API request - starts the query
        print(query_job.state)
        self._product_pair_history(serial_number, airu_mac, sensorid)

    def _product_pair_history(self, serial_number, airu_mac, sensorid):
        today = datetime.datetime.today()
        rows_to_insert = [
            {
                "serial_number": serial_number,
                'mac_addr': airu_mac,
                'sensor_id': sensorid,
                'time_stamp': today
            }
        ]
        errors = self._client.insert_rows(self._history_table, rows_to_insert)  # API request

    def add_sensor_info(self, sensor_id, broken=False, availability=True):
        print('_add_sensor_info')
        rows = self._client.list_rows(self._sensors_table,
                                      [bigquery.SchemaField("sensor_id", "STRING", mode="REQUIRED")])
        format_string = "{!s:<16} " * len(rows.schema)
        for row in rows:
            mac_addr_data = row.get('sensor_id')
            print(mac_addr_data)
            if sensor_id.find(mac_addr_data) != -1:
                print("Found duplication")
                self._update_sensor_info(sensor_id, broken, availability)
                return
        # Loop ends
        today = datetime.datetime.today()
        rows_to_insert = [
            {'sensor_id': sensor_id,
             'broken': broken,
             'availability': availability,
             'date_update': today}
        ]
        errors = self._client.insert_rows(self._sensors_table, rows_to_insert)  # API request

    def _update_sensor_info(self, sensor_id, broken=False, availability=True):
        print("_update_sensor_info")
        today = datetime.datetime.today()
        query = ('UPDATE `{}.{}.{}` SET broken={}, availability={}, date_update="{}" WHERE sensor_id="{}"'
                 .format(PROJECT_ID, DATA_SET_ID, SENSOR_TABLE_ID, broken, availability, today, sensor_id))
        query_job = self._client.query(query)  # API request - starts the query
        print(query_job.state)


class SerialNotFound(Exception):
    """ Attribute not found. """
    def __init__(self, message): # real signature unknown
        super().__init__(message)
        pass

class BoardMacAddressNotFound(Exception):
    """ Attribute not found. """
    def __init__(self, message): # real signature unknown
        super().__init__(message)
        pass

class AuthenticationError(Exception):
    """ Attribute not found. """
    def __init__(self, message): # real signature unknown
        super().__init__(message)
        pass

if __name__ == '__main__':
    bquerry = BigQuerryDbManagerClass(JSON_PATH)
    bquerry.add_new_product('32:AA:A4:EF:A1:32', 'PMS00000321231233')
    # bquerry._check_data_duplication('31:AE:A4:EF:A9:E9')
    # bquerry.insert_new_board('31:AE:A4:EF:A9:A9', 'airu-version-2.5', True, True)
    # bquerry._update_boards_availability('31:AE:A4:EF:A9:A9', True, False)
    # bquerry.add_sensor_info('PMS0000001', True, False)
