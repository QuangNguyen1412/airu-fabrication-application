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
from PyQt4.QtCore import Qt
from functools import partial

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
SCRIPTS_PATH = APP_PATH + os.path.sep + 'scripts'
CREDENTIAL_PATH = APP_PATH + os.path.sep + 'credential'
ESPTOOL_PATH = SCRIPTS_PATH + os.path.sep + 'esptool.py'
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
                    # msg = QMessageBox()
                    # msg.setIcon(QMessageBox.Information)
                    # msg.setText("Check the USB serial connection!!")
                    # msg.setStandardButtons(QMessageBox.Ok)
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
    def __init__(self, device_manager):
        self.ports = list(serial.tools.list_ports.comports())
        self.com_Choice = "COM0"
        self.device_manager = device_manager
        self.binary_name = "None"
        self.fw_version = "airu-firmware-2.0"
        self.board_mac_textbox = QLineEdit()

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
        self.device_manager.insert_new_board(esp.macAddress_string.upper(), self.fw_version)

    def b1_flashing(self):
        print("flashing")
        self.progress.setStyleSheet(COMPLETED_STYLE)
        esp = Esp_Tool(self.com_Choice, DEFAULT_BAUDRATE)
        esp.Esp_Write_Flash(self.progress, self.b1, self.b2, self.button_print_airu_mac, self.binary_name)
        # esp.mac_address_print()
        self.device_manager.insert_new_board(esp.macAddress_string.upper(), self.fw_version)

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

    def tabOneSetLayout(self):
        html_reader = HtmlReaderClass()
        self.binary_combo_box = QComboBox()
        self.binary_combo_box.addItem("Choose a firmware for flashing")
        self.binary_combo_box.addItems(list(html_reader.data))
        self.binary_combo_box.activated[str].connect(self.binary_combo_choice)

        # progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximum(100)
        self.progress.setStyleSheet(COMPLETED_STYLE)

        # Button definition
        self.b1 = QPushButton("FW Flashing")
        self.button_print_airu_mac = QPushButton("MAC Printing")
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
        self.housing_qr_print_btn = QPushButton("Update/Create new pair")
        self.housing_qr_print_btn.setSizePolicy(
           QSizePolicy.Preferred,
           QSizePolicy.Expanding)

        self.housing_qr_print_btn.clicked.connect(self.makeNewSerial)
        device_mac_lbl = QLabel()
        device_mac_lbl.setText("Device MAC address:")
        device_owner_lbl = QLabel()
        device_owner_lbl.setText("Device Owner:")
        pm_mac_lbl = QLabel()
        pm_mac_lbl.setText("PM sensor MAC address:")
        self.device_mac_input = QLineEdit()
        self.device_mac_input.setToolTip("aa:aa:aa:aa:aa:aa")
        self.device_owner_input = QLineEdit()
        self.device_owner_input.setToolTip("example@gmail.com")
        self.pm_mac_input = QLineEdit()
        self.pm_mac_input.setMaxLength(21)
        self.pm_mac_input.setToolTip("PMS5003-201608161931")
        tab2Vbox = QVBoxLayout()
        tab2Vbox.addWidget(device_mac_lbl)
        tab2Vbox.addWidget(self.device_mac_input)
        tab2Vbox.addWidget(pm_mac_lbl)
        tab2Vbox.addWidget(self.pm_mac_input)
        tab2Vbox.addWidget(device_owner_lbl)
        tab2Vbox.addWidget(self.device_owner_input)
        tab2Vbox.addWidget(self.housing_qr_print_btn)
        self.device_mac_input.textChanged[str].connect(self.checkMAC)
        self.tab2.setLayout(tab2Vbox)
        self.housing_qr_print_btn.setDisabled(True)

    def makeNewSerial(self):
        if self.device_mac_input.text() and self.pm_mac_input.text():
            combine_mac = self.device_manager.add_new_product(self.device_mac_input.text().upper(),
                                                self.pm_mac_input.text().upper(),
                                                self.device_owner_input.text())
            if combine_mac == -1:
                return
            print("printing the label " + combine_mac)
            dymo_args = [DYMO_PRINTER_PATH,
            DYMO_PRINTERNAME_OPT,
            DYMO_TRAY_OPT,
            DYMO_COPIES_OPT,
            DYMO_OBJECTDATA_OPT, "Text=" + combine_mac + "\n" +
                         self.device_mac_input.text().upper() + "\n" + self.pm_mac_input.text().upper(),
            DYMO_OBJECTDATA_OPT, "QR=" + combine_mac,
            DYMO_LABEL_PATH]
            subprocess.run(dymo_args)
            self.pm_mac_input.clear()
            self.device_mac_input.clear()
            self.device_mac_input.setFocus()

    def _update_sensor_func(self, broking_true, available_true):
        print('update_sensor_func')
        broken = broking_true.isChecked()
        available = available_true.isChecked()
        mac_address = self.sensor_id_textbox.text().upper()
        print('update sensor info', mac_address, broken, available)
        self.device_manager.add_sensor_info(mac_address, broken=broken,
                                                         availability=available)
        self.sensor_id_textbox.clear()

    def tabFourSetLayout(self):
        print('tabFourSetLayout')
        class_num = QButtonGroup(self.tab4)
        broking_true = QRadioButton("Broken")
        class_num.addButton(broking_true, 0)
        broking_false = QRadioButton("Working")
        class_num.addButton(broking_false, 1)
        broking_false.setChecked(True)

        class_num1 = QButtonGroup(self.tab4)
        available_true = QRadioButton("Available")
        class_num1.addButton(available_true, 0)
        available_false = QRadioButton("Unavailable")
        class_num1.addButton(available_false, 1)
        available_true.setChecked(True)


        self.add_sensor_button = QPushButton("Update Sensor info")
        self.add_sensor_button.clicked.connect(partial(self._update_sensor_func, broking_true, available_true))
        board_mac_lbl = QLabel()
        board_mac_lbl.setText("Sensor id:")

        self.add_sensor_button.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding)

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        self.sensor_id_textbox = QLineEdit()
        self.sensor_id_textbox.setToolTip("PMS5003-201608161931")

        # Add widget to the layout
        hbox.addWidget(self.add_sensor_button, 3)
        vbox.addWidget(board_mac_lbl)
        vbox.addWidget(self.sensor_id_textbox)
        vbox.addWidget(broking_false)
        vbox.addWidget(broking_true)
        vbox.addWidget(available_true)
        vbox.addWidget(available_false)
        hbox.addLayout(vbox)

        self.tab4.setLayout(hbox)

    def tabThreeSetLayout(self):
        print('tabThreeSetLayout')
        broking_true = QRadioButton("Broken")
        broking_false = QRadioButton("Working")
        broking_false.setChecked(True)
        available_true = QRadioButton("Available")
        available_true.setChecked(True)
        available_false = QRadioButton("Unavailable")
        class_num = QButtonGroup(self.tab3)
        class_num.addButton(available_true)
        class_num.addButton(available_false)

        class_num1 = QButtonGroup(self.tab3)
        class_num1.addButton(broking_true)
        class_num1.addButton(broking_false)

        self.add_board_info_button = QPushButton("Update Board info")
        self.add_board_info_button.clicked.connect(partial(self._update_board_info_func, broking_true, available_true))
        board_mac_lbl = QLabel()
        board_mac_lbl.setText("Board Mac Address:")

        self.add_board_info_button.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding)

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        self.board_mac_textbox.setToolTip("30:AE:A4:EF:A9:F4")

        # Add widget to the layout
        hbox.addWidget(self.add_board_info_button, 3)
        vbox.addWidget(board_mac_lbl)
        vbox.addWidget(self.board_mac_textbox)
        vbox.addWidget(broking_false)
        vbox.addWidget(broking_true)
        vbox.addWidget(available_true)
        vbox.addWidget(available_false)
        hbox.addLayout(vbox)
        self.tab3.setLayout(hbox)

    def _update_board_info_func(self, broking_true, available_true):
        print('_update_board_info_func')
        broken = broking_true.isChecked()
        available = available_true.isChecked()
        mac_address = self.board_mac_textbox.text().upper()
        print('update board info', mac_address, broken, available)
        self.device_manager.update_boards_availability(mac_address, broken=broken,
                                                       availability=available)
        self.board_mac_textbox.clear()

    def window(self):
        app = QApplication(sys.argv)
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont('Arial', 11))
        self.comDescription = QLabel(self.com_Choice)

        # tab definition
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        tab_widget.addTab(self.tab1, "Programming")
        tab_widget.addTab(self.tab2, "Management")
        tab_widget.addTab(self.tab3, "Boards")
        tab_widget.addTab(self.tab4, "Sensors")
        self.tabOneSetLayout()
        self.tabTwoSetLayout()
        self.tabThreeSetLayout()
        self.tabFourSetLayout()

        tab_widget.setWindowTitle("AirU Flashing Tool")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        tab_widget.setWindowIcon(QIcon(script_dir + os.path.sep + 'AIRU.png'))
        tab_widget.resize(450, 250)
        tab_widget.show()
        self.device_mac_input.setFocus()
        sys.exit(app.exec_())
# End of class


class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        QApplication.setStyle(QStyleFactory.create("GTK+"))
        self._jsonFiles = os.listdir(CREDENTIAL_PATH)
        print("jsons", self._jsonFiles)
        self._jsonFile = "Choose a Google Account Service JSON"
        v_layout = QVBoxLayout(self)
        self._jsonDropDownBoxInit(v_layout)
        self._acceptButtonInit(v_layout)

    def _jsonFileSelectorFunc(self, text):
        self._jsonFile = CREDENTIAL_PATH + os.path.sep + text

    def _jsonDropDownBoxInit(self, vbox):
        json_file_selection = QComboBox()
        json_file_selection.addItem(self._jsonFile)
        json_file_selection.addItems(self._jsonFiles)
        json_file_selection.activated[str].connect(self._jsonFileSelectorFunc)
        vbox.addWidget(json_file_selection)

    def _acceptButtonFunc(self):
        try:
            self.deviceManager = AirUDeviceManager.BigQuerryDbManagerClass(self._jsonFile)
            self.accept()
            QMessageBox.information(self, 'Success', 'Logging in')
        except google.api_core.exceptions.Forbidden as error:
            self.reject()
            QMessageBox.critical(self, 'Error', str(error))

    def _acceptButtonInit(self, vbox):
        self.ok_push_button = QPushButton('OK')
        self.ok_push_button.clicked.connect(self._acceptButtonFunc)
        vbox.addWidget(self.ok_push_button, alignment=Qt.AlignHCenter)

    def _label_init(self, hbox):
        username_label = QLabel()
        username_label.setText("DB user")
        pwd_label = QLabel()
        pwd_label.setText("DB password")
        hbox.addWidget(pwd_label, 3)
        hbox.addWidget(username_label, 3)

    def _db_pass_input_init(self, vbox):
        h_layout = QHBoxLayout(self)
        vbox.addLayout(h_layout)
        self.pwd_input = QLineEdit()
        self.pwd_input.setToolTip("Password")
        pwd_label = QLabel()
        pwd_label.setText("DB password")
        h_layout.addWidget(pwd_label, 3)
        h_layout.addWidget(self.pwd_input)

    def _db_username_input_init(self, vbox):
        h_layout = QHBoxLayout(self)
        vbox.addLayout(h_layout)
        self.username_input = QLineEdit()
        self.username_input.setToolTip("DB user")
        username_label = QLabel()
        username_label.setText("DB user")
        h_layout.addWidget(username_label, 3)
        h_layout.addWidget(self.username_input)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = Login()
    if login.exec_() == QDialog.Accepted:
        mainUi = Ui_MainWindow(login.deviceManager)
        mainUi.window()
    app.exec_()
