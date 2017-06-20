import gspread
from oauth2client.service_account import ServiceAccountCredentials
from IPython.core.debugger import Tracer
 
 
# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
 
spreadsheet = client.open('SMS received')
sms_sheet = spreadsheet.worksheet('SMS')
#sms_sheet = client.open('SMS received').worksheet('SMS')
 
# Extract and print all of the values
sms_list = sms_sheet.get_all_records()

pilot_sheet = client.open('SMS received').worksheet('Pilot List')
pilot_list = pilot_sheet.get_all_records()

reversed_contents = list(reversed(sms_list)) # because we only really want the most recent update

updated_status = []
updated_status.append(["Pilot Number", "Pilot Name", "Status", "Updated", "Phone Number"])
for pilot in pilot_list:
    updated = False
    for sms in reversed_contents:
        if '#' + str(pilot['pilot_number']) in str(sms['message']):
            status = 'NULL'
            if 'lok' in sms['message'].lower():
                status = 'LOK'
            elif 'pup' in sms['message'].lower():
                status = 'PUP'
            elif 'fly' in sms['message'].lower():
                status = 'FLY'
            elif 'dnf' in sms['message'].lower():
                status = 'DNF'
            elif 'aid' in sms['message'].lower():
                status = 'AID'
            updated = True
            updated_status.append([pilot['pilot_number'], pilot['pilot_name'], status, sms['date'], sms['number']])
            break
        else:
            status = 'NULL'
    if not updated:
        status = 'NULL'
        updated_status.append([pilot['pilot_number'], pilot['pilot_name'], status, '', ''])


#print updated_status
wksht = spreadsheet.worksheet('Current Status')

updated_cells = wksht.range('A1:E' + str(len(updated_status)))
for cell in updated_cells:
    cell.value = updated_status[cell.row - 1][cell.col - 1]
wksht.update_cells(updated_cells)
