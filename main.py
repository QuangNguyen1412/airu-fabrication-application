##############################################################
# Name: main.py
# Description: Emulating esptool.py as a GUI and specifically modified to use with AirU devices ESP version.
# This script also make used of a sub-program based on DYMO SDK ( a Supported SDK for Label Printing with DYMO devices)
# that could help us easily get AirU board MAC address printed
# We can flash every ESP-based AirU device,
# Author: Quang Nguyen
# Author Email: ntdquang1412@gmail.com
# esptool.py v2.6
# Date: June 10th, 2019

import sys
import os
import esptool
import subprocess
import serial
import serial.tools.list_ports
import AirUDeviceManager
from PyQt4.QtGui import *
from htmlReader import HtmlReaderClass

COMPLETED_STYLE = """
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: #01DF01;
    width: 2px;
    margin: .2px;
}
"""
FAILED_STYLE = """
QProgressBar{
    border: 2px solid red;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: red;
    width: 2px;
    margin: .2px;
}
"""

APP_PATH = os.path.dirname(os.path.realpath(__file__))
ESPTOOL_PATH = APP_PATH + os.path.sep + 'esptool.py'
SCRIPTS_PATH = APP_PATH + os.path.sep + 'scripts'
DYMO_SCRIPT = SCRIPTS_PATH + os.path.sep + "DYMO"
RESOURCE_LABEL_PATH = APP_PATH + os.path.sep + "resources" + os.path.sep + "label"
RESOURCE_BIN_PATH = APP_PATH + os.path.sep + "resources" + os.path.sep + "binary"

DYMO_PRINTER_PATH = DYMO_SCRIPT + os.path.sep + "PrintLabel.exe"
# DYMO_PRINTER_PATH = "PrintLabel.exe"
DYMO_PRINTERNAME_OPT = "/printer \"LabelWriter 450 Twin Turbo\""
DYMO_TRAY_OPT = "/tray 0"
DYMO_COPIES_OPT = "/copies 1"
DYMO_OBJECTDATA_OPT = "/objdata"
DYMO_LABEL_PATH = RESOURCE_LABEL_PATH + os.path.sep + "Small.label"
# DYMO_LABEL_PATH = "Small.label"
DEFAULT_BAUDRATE = 115200

AIRU_DEVICE_SHEET = "AirUDevices"
TETRA_DEVICES = "Tetra devices"

class Esp_Tool(object):
    def __init__(self, com_port, baudRate):
        self.comPort = com_port
        self.baudRate = baudRate
        esp = esptool.ESPLoader.detect_chip(self.comPort, DEFAULT_BAUDRATE)
        mac_tuple = esp.read_mac()
        esp._port.close()
        self.macAddress_string = '%s' % ':'.join(map(lambda x: '%02x' % x, mac_tuple))

    def mac_address_print(self):
        print(self.macAddress_string.upper())
        sys.stdout.flush()
        dymo_args = [DYMO_PRINTER_PATH,
        DYMO_PRINTERNAME_OPT,
        DYMO_TRAY_OPT,
        DYMO_COPIES_OPT,
        DYMO_OBJECTDATA_OPT, "Text=" + self.macAddress_string.upper(),
        DYMO_OBJECTDATA_OPT, "QR=" + self.macAddress_string.upper(),
        DYMO_LABEL_PATH]
        subprocess.run(dymo_args)

    def Esp_Write_Flash(self, progress, b1, b2, b3, file_name):
        print("Start Flashing...")
        b1.setDisabled(True)
        b2.setDisabled(True)
        b3.setDisabled(True)

        # flashing information constant
        FLASHING_CHIP_OPTION = "-c"
        FLASHING_CHIP_OPTION_VALUE = "esp32"
        FLASHING_PORT_OPTION = "-p"
        FLASHING_BAUD_OPTION = "-b"
        FLASHING_BEFORE_OPTION = "--before"
        FLASHING_BEFORE_OPTION_DEFAULT_RESET = "default_reset"
        FLASHING_AFTER_OPTION = "--after"
        FLASHING_AFTER_OPTION_NO_RESET = "no_reset"
        FLASHING_WRITEFLASH = "write_flash"
        FLASHING_COMPRESS_OPTION = "-z"
        FLASHING_FLASHMODE_OPTION = "--flash_mode"
        FLASHING_FLASHMODE_OPTION_VALUE = "dio"
        FLASHING_FLASHFREQ_OPTION = "--flash_freq"
        FLASHING_FLASHFREQ_OPTION_VALUE = "80m"
        FLASHING_FLASHSIZE_OPTION = "--flash_size"
        FLASHING_FLASHSIZE_OPTION_VALUE = "detect"
        FLASHING_OTA_BIN_ADDR = "0xd000"
        FLASHING_OTA_BIN_LOCATION = RESOURCE_BIN_PATH + os.path.sep + "ota_data_initial.bin"
        FLASHING_BOOTLOADER_BIN_ADDR = "0x1000"
        FLASHING_BOOTLOADER_LOCATION = RESOURCE_BIN_PATH + os.path.sep + "bootloader.bin"
        FLASHING_FW_BIN_ADDR = "0x10000"
        FLASHING_FW_LOCATION = RESOURCE_BIN_PATH + os.path.sep + file_name
        FLASHING_OTA_PT2_BIN_ADDR = "0x8000"
        FLASHING_OTA_PT2_LOCATION = RESOURCE_BIN_PATH + os.path.sep + "partitions_two_ota.bin"
        print(ESPTOOL_PATH)
        flashing_args = ['python', ESPTOOL_PATH, FLASHING_CHIP_OPTION, FLASHING_CHIP_OPTION_VALUE,
         FLASHING_PORT_OPTION, self.comPort,
         FLASHING_BAUD_OPTION, str(self.baudRate),
         FLASHING_BEFORE_OPTION, FLASHING_BEFORE_OPTION_DEFAULT_RESET,
         FLASHING_AFTER_OPTION, FLASHING_AFTER_OPTION_NO_RESET,
         FLASHING_WRITEFLASH, FLASHING_COMPRESS_OPTION,
         FLASHING_FLASHMODE_OPTION, FLASHING_FLASHMODE_OPTION_VALUE,
         FLASHING_FLASHFREQ_OPTION, FLASHING_FLASHFREQ_OPTION_VALUE,
         FLASHING_FLASHSIZE_OPTION, FLASHING_FLASHSIZE_OPTION_VALUE,
         FLASHING_FW_BIN_ADDR, FLASHING_FW_LOCATION,
         FLASHING_OTA_BIN_ADDR, FLASHING_OTA_BIN_LOCATION,
         FLASHING_BOOTLOADER_BIN_ADDR, FLASHING_BOOTLOADER_LOCATION,
         FLASHING_OTA_PT2_BIN_ADDR, FLASHING_OTA_PT2_LOCATION
         ]
        try:
            proc = subprocess.Popen(flashing_args, stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE)
            while True:
              line_raw = proc.stdout.readline()
              line = line_raw.rstrip()
              if not line_raw:
                break
              # the real code does filtering here
              if line_raw.find('Writing') != -1:
                  try:
                      print(line)
                      sys.stdout.flush()
                      start = line.find('(') + 1
                      end = line.find('%)', start + 1)
                      percent = line[start:end]
                      progress.setValue(int(percent))
                  except AttributeError:
                      percent = 0
                      progress.setStyleSheet(FAILED_STYLE)
            # End While

            while True:
                error_raw = proc.stderr.readline()
                er = error_raw.rstrip()
                if not error_raw:
                    break
                elif (er.find('serial.serialutil') != -1) | (er.find('SerialException') != -1):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Check the USB serial connection!!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    print ("Check the USB serial connection")
                    b2.setDisabled(False)
                    progress.setStyleSheet(FAILED_STYLE)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Check the USB serial connection!!")
                    msg.setInformativeText("Reconnect ESP32 again then hit 'COM Checking'")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    return
                print("ERROR: " + error_raw.rstrip())
                sys.stdout.flush()
                progress.setStyleSheet(FAILED_STYLE)
            # End While
        except:
            e = sys.exc_info()[0]
            print("Exception " + str(e))
            return
        # End Try
        b1.setDisabled(False)
        b2.setDisabled(False)
        b3.setDisabled(False)

class Ui_MainWindow(object):
    def __init__(self, g_spread_sheet):
        self.ports = list(serial.tools.list_ports.comports())
        QApplication.setStyle(QStyleFactory.create("Cleanlooks"))
        # Button definition
        self.com_Choice = "COM0"
        self.device_manager = AirUDeviceManager.AirUDeviceManagerClass(g_spread_sheet)
        self.binary_name = "None"
        self.fw_version = "None"

    def comport_choice(self, text):
        self.com_Choice = text
        for p in self.ports:
            if p.device == text:
                self.comDescription.setText(p.description)
                break
        print(self.com_Choice)

    def airu_mac_print_func(self):
        print("Printing mac")
        self.progress.setStyleSheet(COMPLETED_STYLE)
        esp = Esp_Tool(self.com_Choice, DEFAULT_BAUDRATE)
        esp.mac_address_print()
        self.device_manager.update_airu_mac(esp.macAddress_string.upper(), self.fw_version)

    def b1_flashing(self):
        print("flashing")
        self.progress.setStyleSheet(COMPLETED_STYLE)
        esp = Esp_Tool(self.com_Choice, DEFAULT_BAUDRATE)
        esp.Esp_Write_Flash(self.progress, self.b1, self.b2, self.button_print_airu_mac, self.binary_name)
        # esp.mac_address_print()
        self.device_manager.update_airu_mac(esp.macAddress_string.upper(), self.fw_version)

    def b2_checking(self):
        print("Checking COM " + self.com_Choice)
        self.ports = list(serial.tools.list_ports.comports())
        self.comboBox.clear()
        if self.ports:
            index = self.binary_name.find('.bin')
            if index != -1:
                self.b1.setDisabled(False)
                self.button_print_airu_mac.setDisabled(False)
            for p in self.ports:
                print(p)
                self.comboBox.addItem(p.device)
                self.comport_choice(p.device)
        else:
            self.comboBox.addItem("No availabe device")
            self.comDescription.setText("No availabe device")
            self.b1.setDisabled(True)
            self.button_print_airu_mac.setDisabled(True)

    def binary_combo_choice(self, text):
        index = text.find('.bin')
        if index != -1:
            self.fw_version = text[0:index]
            print("Downloading", text)
            print("fw version", self.fw_version)
            self.binary_name = text
            html_reader = HtmlReaderClass()
            html_reader.get_file(text)
            self.b1.setDisabled(False)
            self.b2_checking()

    def tabOneSetLayout(self):
        html_reader = HtmlReaderClass()
        self.binary_combo_box = QComboBox()
        self.binary_combo_box.addItem("Choose a firmware for flashing")
        print("data", html_reader.data)
        for a in html_reader.data:
            print('>>>>',a)
            self.binary_combo_box.addItem(a)
        self.binary_combo_box.activated[str].connect(self.binary_combo_choice)


        # progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximum(100)
        self.progress.setStyleSheet(COMPLETED_STYLE)

        # Button definition
        self.b1 = QPushButton("Flashing")
        self.button_print_airu_mac = QPushButton("Print MAC")
        self.b2 = QPushButton("COM Checking")
        self.b1.setSizePolicy(
           QSizePolicy.Preferred,
           QSizePolicy.Expanding)
        self.b2.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding)
        self.button_print_airu_mac.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding)

        # Bind function
        self.b1.clicked.connect(self.b1_flashing)
        self.b2.clicked.connect(self.b2_checking)
        self.button_print_airu_mac.clicked.connect(self.airu_mac_print_func)
        # Combo box definition
        self.comboBox = QComboBox()
        self.comboBox.addItem(self.com_Choice)
        # Detect com port
        self.b2_checking()
        # Combo box function binding
        self.comboBox.activated[str].connect(self.comport_choice)
        # QT box layout definition
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        # Add buttons
        hbox.addWidget(self.b1, 3)
        hbox.addWidget(self.button_print_airu_mac, 3)
        hbox.addWidget(self.b2, 1)
        # Add combo box
        vbox.addWidget(self.comDescription)
        vbox.addWidget(self.comboBox)
        vbox.addWidget(self.progress)
        vbox.addWidget(self.binary_combo_box)
        self.tab1.setLayout(vbox)
        self.b1.setDisabled(True)
        self.button_print_airu_mac.setDisabled(True)

    def checkMAC(self, text):
        if len(text) >= 17:
            self.pm_mac_input.setFocus()
            self.housing_qr_print_btn.setDisabled(False)

    def tabTwoSetLayout(self):
        self.housing_qr_print_btn = QPushButton("Print QR")
        self.housing_qr_print_btn.setSizePolicy(
           QSizePolicy.Preferred,
           QSizePolicy.Expanding)

        self.housing_qr_print_btn.clicked.connect(self.printHousingQR)
        device_mac_lbl = QLabel(self.com_Choice)
        device_mac_lbl.setText("Device MAC address:")
        pm_mac_lbl = QLabel(self.com_Choice)
        pm_mac_lbl.setText("PM sensor MAC address:")
        self.device_mac_input = QLineEdit()
        self.device_mac_input.setToolTip("aa:aa:aa:aa:aa:aa")
        self.pm_mac_input = QLineEdit()
        self.pm_mac_input.setMaxLength(20)
        self.pm_mac_input.setToolTip("PMS5003-201608161931")
        tab2Vbox = QVBoxLayout()
        tab2Vbox.addWidget(device_mac_lbl)
        tab2Vbox.addWidget(self.device_mac_input)
        tab2Vbox.addWidget(pm_mac_lbl)
        tab2Vbox.addWidget(self.pm_mac_input)
        tab2Vbox.addWidget(self.housing_qr_print_btn)
        self.device_mac_input.textChanged[str].connect(self.checkMAC)
        self.tab2.setLayout(tab2Vbox)
        self.housing_qr_print_btn.setDisabled(True)

    def printHousingQR(self):
        if self.device_mac_input.text() & self.pm_mac_input.text():
            combine_mac = self.device_mac_input.text() + "%20" + self.pm_mac_input.text()
            print("printing the label " + combine_mac)
            dymo_args = [DYMO_PRINTER_PATH,
            DYMO_PRINTERNAME_OPT,
            DYMO_TRAY_OPT,
            DYMO_COPIES_OPT,
            DYMO_OBJECTDATA_OPT, "Text=" + combine_mac.upper(),
            DYMO_OBJECTDATA_OPT, "QR=" + self.device_mac_input.text().upper() + "-" + self.pm_mac_input.text().upper(),
            DYMO_LABEL_PATH]
            subprocess.run(dymo_args)
            self.device_manager.update_housing_qr(self.device_mac_input.text().upper(), self.pm_mac_input.text().upper())
            self.device_mac_input.clear()
            self.pm_mac_input.clear()
            self.device_mac_input.setFocus()

    def window(self):
        app = QApplication(sys.argv)
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont('Arial', 11))
        self.comDescription = QLabel(self.com_Choice)

        # tab definition
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        tab_widget.addTab(self.tab1, "Programming")
        tab_widget.addTab(self.tab2, "Management")

        self.tabOneSetLayout()
        self.tabTwoSetLayout()

        tab_widget.setWindowTitle("AirU Flashing Tool")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        tab_widget.setWindowIcon(QIcon(script_dir + os.path.sep + 'AIRU.png'))
        tab_widget.resize(450, 200)
        tab_widget.show()
        self.device_mac_input.setFocus()
        sys.exit(app.exec_())
# End of class


if __name__ == '__main__':
   ui = Ui_MainWindow(AIRU_DEVICE_SHEET)
   ui.window()
