import re
import googleanalytics as ga

def print_list(l):
    for item in l:
        print item

def match(column):
    return re.search(pattern, column.name, re.IGNORECASE)

def list(credentials, name=None, account=None, webproperty=None, profile=None, pattern=None):
    accounts = ga.auth.oauth.ask_and_authenticate(**credentials)

    if pattern:
        columns = accounts[account].columns
        filtered_columns = filter(match, columns)
        print_list(filtered_columns)
    elif profile:
        columns = accounts[account].columns
        print_list(columns)
    elif webproperty:
        profiles = accounts[account].webproperties[webproperty].profiles
        print_list(profiles)
    elif account:
        webproperties = accounts[account].webproperties
        print_list(webproperties)
    else:
        print_list(accounts)