#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import json
import opendata

# ADA of the decision to revoke
ada = u'ΑΔΑ...'
# Comment for the revocation request
comment = "reason..."

# Send request
client = opendata.OpendataClient()
client.set_credentials('10599_api', 'User@10599')
response = client.submit_revocation_request(ada, comment)

if response.status_code == 200:
    decision = response.json()
    print "Το αίτημα ανάκλησης έχει υποβληθεί."
elif response.status_code == 400:
    print "Σφάλμα στην υποβολή της πράξης"
elif response.status_code == 401:
    print str(response.status_code) + " Σφάλμα αυθεντικοποίησης"
elif response.status_code == 403:
    print str(response.status_code) + " Απαγόρευση πρόσβασης"
else:
    print("ERROR " + str(response.status_code))

