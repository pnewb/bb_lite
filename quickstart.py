from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from IPython.core.debugger import Tracer

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    #spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    spreadsheetId = '1_h6hoQUBb9NYFV7p0j6amI5WgZB-Y2UWhT-owILDgjc'

    rangeName = 'SMS!A2:D'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    sms_sheet = []
    if not values:
        print('No data found.')
    else:
        #print('Date, Number, Message:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            #print('%s, %s, %s' % (row[0], row[1], row[3]))
            sms_sheet.append([row[0], row[1], row[3]])

    reversed_contents = list(reversed(sms_sheet)) # because we only really want the most recent update

    pilot_list = {}
    final_rangeName = 'Sheet1!A1:B'
    result = service.spreadsheets().values().get(
        spreadsheetId='1QyuHoLbFBiwRbmwyJEmAufWc4JdSFa91gpTDNknfnOk', range=final_rangeName).execute()
    values = result.get('values', [])
    for row in values:

        pilot_list[str(row[0])] = []
        pilot_list[str(row[0])].append(row[1])

    updated_status = {}
    for pilot in pilot_list:
        updated_status[pilot] = []
        for sms in reversed_contents:
            if '#' + pilot in sms[2]:
                status = 'NULL'
                if 'lok' in sms[2].lower():
                    status = 'LOK'
                elif 'pup' in sms[2].lower():
                    status = 'PUP'
                updated_status[pilot] = [pilot_list[pilot], sms[0], sms[1], status]
                break
            else:
                status = 'NULL'
                updated_status[pilot] = [pilot_list[pilot], '', '', status]
                continue
    Tracer()()

    body_contents = {'value_input_option': 'USER_ENTERED',
                      'data': json.dumps(updated_status)
                    }
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, body=body_contents)
    response = request.execute()

if __name__ == '__main__':
    main()


