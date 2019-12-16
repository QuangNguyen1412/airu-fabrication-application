# Fabrication software installation guide for windows

## Requirement software
1. follow the link to install DYMO software
http://download.dymo.com/dymo/Software/Win/DLS8Setup.8.7.3.exe
2. Install python 3.7-64 bit https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64.exe
3. Create a Google Service account, they will give you a JSON file after that, then place your JSON file under ./credential 

## User's Guide
1. Install the required softwares
2. The executible is in the main.zip file, extract and run the executible **main.exe**
3. FW flashing tab
- Step 1: Choose the binary you want to program the device
- Step 2: Plug your AirU in, Click 'COM checking' then select your device COM port
- Step 3: Hit Flashing and wait until the progress bar reach 100%

**Note:** To print the device MAC address, you only need Step 2 then hit 'Print MAC'
4. Add google spreadsheet file as database
'This feature will be added shortly'
- Before opening the application, these steps should be followed
- Step 1: Place your API JSON file under ./credential/AirUDeviceManager_client_secret.json
- Step 2: Share your database to the email in your json file. The email should be found in a line similar to this in your JSON file 
"client_email": "airudevicemanager@airudevicemanager.iam.gserviceaccount.com"
- Step 3: Input the sheet that you share

## Developer's Guide
- Install PyQt4 to continue the development: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4
- Place your API JSON file under ./credential/
- Use pyinstaller to make the an executible program, then the executible will be under your current directory ./dist/main/main.exe:
~~~
pyinstaller /path/to/your/main.spec
~~~
