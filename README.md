# Fabrication software installation guide for windows

## Requirement software
1. follow the link to install DYMO software
http://download.dymo.com/dymo/Software/Win/DLS8Setup.8.7.3.exe
2. Install python 3.7
https://www.python.org/downloads/

## User's Guide
1. Install the required softwares
2. The executible is in the main.zip file, extract and run the executible **main.exe**
3. The application has 2 tabs: Programming and Management
- Programming tab: This tab for programming the AirU board and storing their MAC address to a google spreadsheet-based-database (database).
- Management tab: We manage devices by pairing every AirU board with PM sensor, then we could have user's information for each device/pair. And all the information (AirU, PM sensor, devices, User's information) will be stored in the database. We can get the device Serial Number printed out

**Programming steps**
Step 1: Choose the binary you want to program the device
Step 2: Plug your AirU in, Click 'COM checking' then select your device COM port
Step 3: Hit Flashing and wait until the progress bar reach 100%

Note: To print the device MAC address, you only need Step 2 then hit 'Print MAC'

**Add google spreadsheet file as database** 'This feature will be added shortly'
Before opening the application, these steps should be followed
Step 1: Place your API JSON file under ./credential/AirUDeviceManager_client_secret.json
Step 2: Share your database to the email in your json file. The email should be found in a line similar to this in your JSON file 
"client_email": "airudevicemanager@airudevicemanager.iam.gserviceaccount.com"
Step 3: Input the sheet that you share

## Developer's Guide
- Use pyinstaller to make the an executible program, then the executible will be under your current directory ./dist/main/main.exe:
>> pyinstaller /path/to/your/main.spec
