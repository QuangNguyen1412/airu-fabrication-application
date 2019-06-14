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
from gspread import CellNotFound
from oauth2client.service_account import ServiceAccountCredentials

AIRU_DEVICE_SHEET = "AirUDevices"
TETRA_DEVICES = "Tetra devices"


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AirUDeviceManagerClass(object):
    def __init__(self, g_spread_sheet):
        scope = ['https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/feeds']
        script_dir = os.path.dirname(os.path.realpath(__file__))
        credential_json_path = script_dir + os.path.sep + 'credential' + os.path.sep + 'AirUDeviceManager_client_secret.json'
        # credential_json_path = 'AirUDeviceManager_client_secret.json'
        # credential_json_path = resource_path('AirUDeviceManager_client_secret.json')
        print('credential_json_path:', credential_json_path)
        print('isfile:', os.path.isfile(credential_json_path))
        creds = ServiceAccountCredentials.from_json_keyfile_name(credential_json_path, scope)
        client = gspread.authorize(creds)
        self._sheet = client.open(g_spread_sheet).sheet1
        # self._sheet = client.open(TETRA_DEVICES).sheet1
        self.airu_mac_col_number = self._sheet.find("AirU MAC").col
        self.pm_mac_col_number = self._sheet.find("PM MAC").col
        self.firmware_version_col_number = self._sheet.find("Firmware Version").col
        self.housing_mac_col_number = self._sheet.find("Housing MAC").col

    def update_housing_qr(self, airu_mac, pm_mac):
        print(airu_mac, pm_mac)
        housing_mac = airu_mac + "-" + pm_mac
        print("Update housing QR ", housing_mac)
        try:
            # Try to clear the previous pair of PM sensor
            existing_pm_mac_rows = self._sheet.findall(pm_mac)
            for cell in existing_pm_mac_rows:
                self._sheet.update_cell(cell.row, self.pm_mac_col_number, "")
                self._sheet.update_cell(cell.row, self.housing_mac_col_number, "")
        except CellNotFound:
            print("Found Unused PM sensor, this is good")
        try:
            needed_row = self._sheet.find(airu_mac).row
            self._sheet.update_cell(needed_row, self.pm_mac_col_number, pm_mac.upper())
            self._sheet.update_cell(needed_row, self.housing_mac_col_number, housing_mac.upper())
        except CellNotFound:
            print("Adding new row")
            max_rows = len(self._sheet.get_all_values())
            self._sheet.update_cell(max_rows + 1, self.airu_mac_col_number, airu_mac.upper())
            self._sheet.update_cell(max_rows + 1, self.pm_mac_col_number, pm_mac.upper())
            self._sheet.update_cell(max_rows + 1, self.housing_mac_col_number, housing_mac.upper())

    def update_airu_mac(self, airu_mac, fw_ver):
        print("Update airU mac" + airu_mac)
        try:
            existing_mac_row = self._sheet.find(airu_mac).row
            print(airu_mac, "Is already in database at row ", existing_mac_row)
        except CellNotFound:
            print("Cell is not found, going to add new row")
            max_rows = len(self._sheet.get_all_values())
            self._sheet.update_cell(max_rows + 1, self.airu_mac_col_number, airu_mac.upper())
            self._sheet.update_cell(max_rows + 1, self.firmware_version_col_number, fw_ver)
        # End try
# End of class


# if __name__ == '__main__':
#     ui = AirU_Device_Manager()
#     ui.update_housing_qr("30:ae:a4:24:90:30", "124")
    #ui.update_airu_mac("aa:aa:aa:aa:aa", "ver_2.0")
