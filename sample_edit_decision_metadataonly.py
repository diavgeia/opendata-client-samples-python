#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import json
import opendata

# ADA of the decision to edit
ada = u'ΑΔΑ...'

# Decision metadata
json_file = open('SampleDecisionMetadata.json', 'r')
metadata = json.load(json_file)
json_file.close()

metadata['subject'] = u'ΑΠΟΦΑΣΗ ΑΝΑΛΗΨΗΣ ΥΠΟΧΡΕΩΣΗΣ (ΔΙΟΡΘΩΣΗ)'
metadata['extraFieldValues']['entryNumber'] = u'1001'

# Send request
client = opendata.OpendataClient()
client.set_credentials('10599_api', 'User@10599')
response = client.edit_published_decision(ada, metadata)

if response.status_code == 200:
    decision = response.json()
    print "ΑΔΑ: " + decision['ada'].encode('utf8')
elif response.status_code == 400:
    print "Σφάλμα στην υποβολή της πράξης"
    err_json = response.json()
    for err in err_json['errors']:
        print("{0}: {1}".format(err['errorCode'], err['errorMessage'].encode('utf8')))
elif response.status_code == 401:
    print "Σφάλμα αυθεντικοποίησης"
elif response.status_code == 403:
    print "Απαγόρευση πρόσβασης"
else:
    print("ERROR " + str(response.status_code))

