#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""
opendata
~~~~~~~~

This module contains a simple client for the Diavgeia Opendata API. It 
can be used by Python developers as a starting point to create applications
that interact with Diavgeia, or extend existing ones.

Note that this client is not production-ready and is merely used to help
developers create their own libraries. In other words, if you use it
in a production system and it breaks, it's your fault :)

"""

import json
import requests
from requests.auth import HTTPBasicAuth

class OpendataClient(object):
    """Client operations for the Diavgeia Opendata API.
    
    Supports every read operation that is available to Opendata API clients,
    as well as decision submission and editing. This client makes use
    of the requests library (http://docs.python-requests.org), and only
    supports JSON requests/responses.
    
    Read operations return a dict containing the JSON response data,
    while the write operations (submit_decision, edit_published_decision)
    return an instance of requests.Response (detailed description is here:
    http://docs.python-requests.org/en/latest/api/#requests.Response).
    """
    
    def __init__(self, root=None):
        self.root = root or 'https://test3.diavgeia.gov.gr/luminapi/opendata'
        self.auth = False
        self.username = None
        self.password = None
        self.default_headers = {
            'Accept': 'application/json',
            'Connection': 'Keep-Alive'
        }
    
    def set_credentials(self, username, password):
        self.auth = True
        self.username = username
        self.password = password
    
    def unset_credentials(self):
        self.auth = False
        self.username = None
        self.password = None
    
    def get_dictionaries(self):
        """Returns the available dictionaries.
        
        Output format:
          - dictionaries: list of dicts with the following contents
            - uid: dictionary identifier
            - label: dictionary title
        """
        return self._get_resource('/dictionaries')
    
    
    def get_dictionary(self, dict_name):
        """Returns the items of the dictionary with the specified ID.
        
        Arguments:
        dict_name: uid of the dictionary
        
        Output format:
          - name: dictionary identifier
          - items: list of dicts with the following contents:
            - uid: dictionary identifier
            - label: dictionary title
            - parent: identifier of parent item, if any
        """
        return self._get_resource('/dictionaries/' + dict_name)
    
    
    def get_decision_types(self):
        """Returns the available decision types.
        
        Output format:
          - decisionTypes: list of dicts with the following contents:
            - uid: decision type identifier
            - label: decision type title
            - parent: identifier of parent type, if any
            - allowedInDecisions: true if the decision type
              can be used to publish decisions
        """
        return self._get_resource('/types')
    
    
    def get_decision_type(self, type_id):
        """Returns the decision type with the specified ID.
        
        Arguments:
        type_id: uid of the decision type
        
        Output format:
          - uid: decision type identifier
          - label: decision type title
          - parent: identifier of parent type, if any
          - allowedInDecisions: true if the decision type
            can be used to publish decisions
        """
        return self._get_resource('/types/{0}/'.format(type_id))
    
    
    def get_decision_type_details(self, type_id):
        """Returns the decision type with the specified ID, with extra field definitions.
        
        Arguments:
        type_id: uid of the decision type
        
        Output format:
          - uid: decision type identifier
          - label: decision type title
          - parent: identifier of parent type, if any
          - allowedInDecisions: true if the decision type
            can be used to publish decisions
          - extraFields: list of dicts with the following contents:
            - uid: identifier of extra field
            - label: title of extra field
            - type: 'integer' | 'number' | 'string' | 'boolean' | 'object
            - required: true | false
            - multiple: true | false
            - maxLength: 
            - searchTerm: the name of the search term that can be used to
              issue search queries
            - validation: denotes fields whose accepted values follow some
              specific validation rule, or are defined in a discrete set.
              Some typical validation types are:
                'ada': for fields whose values are ADA of other decisions
                'dictionary': for fields whose accepted values are defined
                in one of the available dictionaries
                'afm': for afm records
                'orgStructure': for fields whose values are identifiers
                of organizations that are registered in Diavgeia
            - dictionary: dictionary identifier, only used when the current
              extra field has validation type 'dictionary'
            - relAdaDecisionTypes: list of decision types, only used when
              the current extra field has validation type 'ada'; denotes
              the types of the referenced decisions
            - relAdaConstrainedInOrganization: true | false, only used when
              the current extra field has validation type 'ada'; if true,
              the referenced decisions are always issued from the same
              organization that has published the current decision
            - nestedFields: list of extra fields (see above)
        """
        return self._get_resource('/types/{0}/details'.format(type_id))
    
    
    def get_organizations(self, status='active', category=None):
        """Returns a collection of organizations matching the specified criteria.
        
        Arguments:
        status: active | inactive | pending | all
        category: uid of a valid item of the ORG_CATEGORY dictionary
        """
        return self._get_resource('/organizations?status=' + status +
            ('' if category is None else '&category=' + category))
    
    
    def get_organization(self, org):
        """Returns the organization with the specified uid or latin name.
        
        Arguments:
        org: uid or latin name of an organization
        """
        return self._get_resource('/organizations/{0}/'.format(org))
    
    
    def get_organization_details(self, org):
        """Returns the details of the specified organization.
        
        Arguments:
        org: uid or latin name of an organization
        """
        return self._get_resource('/organizations/{0}/details'.format(org))
    
    
    def get_organization_signers(self, org):
        """Returns the signers that belong to the specified organization.
        
        Arguments:
        org: uid or latin name of an organization
        """
        return self._get_resource('/organizations/{0}/signers'.format(org))
    
    
    def get_organization_positions(self, org):
        """Returns the positions that are defined for the specified organization.
        
        Arguments:
        org: uid or latin name of an organization
        """
        return self._get_resource('/organizations/{0}/positions'.format(org))
    
    
    def get_organization_units(self, org, descendants='children'):
        """Returns the units that belong to the specified organization.
        
        Arguments:
        org: uid or latin name of an organization
        descendants: children | all
        """
        return self._get_resource('/organizations/{0}/units?descendants={1}'.format(org, descendants))
    
    
    def get_positions(self):
        """Returns all the available organization positions.
        """
        return self._get_resource('/positions')
    
    
    def get_unit(self, unit_id):
        """Returns the unit with the specified ID.
        
        Arguments:
        unit_id: unit uid
        """
        return self._get_resource('/units/{0}/'.format(unit_id))
    
    
    def get_signer(self, signer_id):
        """Returns the signer with the specified ID.
        
        Arguments:
        signer_id: signer uid
        """
        return self._get_resource('/signers/{0}/'.format(signer_id))
    
    
    def get_decision(self, ada):
        """Returns the decision with the specified ada.
        
        Arguments:
        ada: decision identifier
        """
        return self._get_resource('/decisions/{0}/'.format(ada))
    
    
    def get_decision_version(self, version_id):
        """Returns the decision with the specified version id.
        
        Arguments:
        versionId: decision version identifier
        """
        return self._get_resource('/decisions/v/{0}/'.format(version_id))
    
    def get_decision_version_log(self, ada):
        """Returns the version log of the decision with the specified ada.
        
        Arguments:
        ada: decision identifier
        """
        return self._get_resource('/decisions/{0}/versionlog'.format(ada))
    
    def get_advanced_search_results(self, q, page=0, size=10):
        """Performs search with the given criteria and returns the results.
        
        Arguments:
        q: search query. The syntax is available to the API doc page
           and the search terms can be obtained with related service calls
        page: result page number (0-based). Default value: 0
        size: result page number (0-based). Default value depends on
              whether the client is authenticated and is configured
              by the Diavgeia administators.
        """
        return self._get_resource(
            '/search/advanced?q={0}&page={1}&size={2}'.format(q, page, size))
    
    
    def get_simple_search_results(self, **kwargs):
        """Performs search with the given criteria and returns the results.
        
        Keyword arguments:
        ada: Diavgeia decision identifier
        subject: Subject of the decision
        protocol: Protocol number
        term: General search term
        org: uid or latin name of the issuing organization
        unit: uid of the organization issuing organization unit
        signer: uid of the signer
        type: decision type uid
        tag: thematic category uid
        from_date: Search decisions published/edited/revoked
                   after this timestamp (format: YYYY-MM-DD)
        to_date: Search decisions published/edited/revoked
                 before this timestamp (format: YYYY-MM-DD)
        from_issue_date: Search decisions with issue date
                         after this date (format: YYYY-MM-DD)
        to_issue_date: Search decisions published/edited/revoked
                       before this date (format: YYYY-MM-DD)
        status: Accepted values are 'published', 'revoked', 
               'pending_revocation', and 'all'. Default: 'all'
        page: Result page number. Default: 0
        size: Result page size. The default value is based on whether
              the client is authenticated or not
        sort: Accepted values are 'recent', 'relative'. Default: 'recent'
        """
        args = ['{0}={1}'.format(kw, kwargs[kw]) for kw in kwargs]
        return self._get_resource('/search?' + '&'.join(args))
    
    
    def get_search_terms(self):
        """Returns all the terms that can be used to form search queries.
        """
        return self._get_resource('/search/terms')
    
    
    def get_common_search_terms(self):
        """Returns the terms that can be used to search decisions
        of every type.
        """
        return self._get_resource('/search/terms/common')
    
    
    def get_search_terms_by_decision_type(self, type_id):
        """Returns the terms that can be used to search decisions
        of a specific type.
        
        Arguments:
        type_id: decision type uid
        """
        return self._get_resource('/types/{0}/terms'.format(type_id))
    
    def submit_decision(self, metadata, pdf, attachments=[], recipients=[]):
        """Submits a new decision in Diavgeia.
        
        Arguments:
        
        metadata: dict containing the decision metadata as described
        in the API documentation page. Depending on the decision type,
        extra fields may be required.
        
        pdf: file handler for the decision document
        
        attachments: file handlers and descriptions for the attachments
        of the decision, if any; tuple consisting of the following values
         - file handler
         - description
         
        recipients: list of email addresses where a notification will be
        sent when the decision is published
        """
        
        self._add_recipients(metadata, recipients)
        
        metadata_str = json.dumps(metadata)
        data = {'metadata': metadata_str}
        files = [('decisionFile', pdf)]
        
        if attachments:
            # Stringify attachment description list
            data['attachmentDescr'] = json.dumps([att[1] for att in attachments])
            for att in attachments:
                files.append(('attachments', att[0]))
        
        return requests.post(url=self._get_resource_url("/decisions"), 
              data=data, files=tuple(files), verify=False,
              auth=self._create_auth())
    
    
    def edit_published_decision(self, ada, metadata, pdf=None):
        """Updates a Diavgeia decision.
        
        Arguments:
        
        metadata: dict containing the decision metadata as described
        in the API documentation page. Depending on the decision type,
        extra fields may be required.
        
        pdf: file handler for the decision document, if this is an
        attempt for a corrected copy. Note that if this is the case,
        metadata['correctedCopy'] MUST be set to True
        """
        
        metadata_str = json.dumps(metadata)
        response = None
        if pdf is None:
            headers = self.default_headers.copy()
            headers['Content-type'] = 'application/json'
            response = requests.post(
                url=self._get_resource_url("/decisions/" + ada), 
                data=metadata_str, headers=headers, verify=False,
                auth=self._create_auth())
        else:
            data = {'metadata': metadata_str}
            files = (('decisionFile', pdf), )
            response = requests.post(
                url=self._get_resource_url("/decisions/" + ada), 
                data=data, files=files, verify=False,
                auth=self._create_auth())
        
        return response
    
    def submit_revocation_request(self, ada, comment):
        """Sends a request for the revocation of the decision with the
        specified ADA, using the specified comment for the reasoning of
        the revocation. If this operation succeeds, then the status of 
        the decision will be 'PENDING_REVOCATION'.
        
        Arguments:
        ada: decision identifier
        comment: reason for revocation of the decision
        """
        request_str = json.dumps({'ada': ada, 'comment': comment})
        headers = self.default_headers.copy()
        headers['Content-type'] = 'application/json'
        response = requests.post(
            url=self._get_resource_url("/decisions/requests/revocations"), 
            data=request_str, headers=headers, verify=False, 
            auth=self._create_auth())
        return response
    
    
    ## PRIVATE
    
    def _add_recipients(self, metadata, recipients):
        if recipients and metadata['publish']:
            metadata['actions'] = [
                {
                    'name': 'notifyRecipients',
                    'args': recipients
                }
            ]
    
    def _get_resource(self, resource, addheaders={}):
        headers = self.default_headers.copy()
        for addh in addheaders.keys():
            headers[addh] = addheaders[addh]
        response = requests.get(self._get_resource_url(resource), 
            auth=self._create_auth(),
            headers=headers,
            verify=False)
        return response.json()
    
    def _get_resource_url(self, url_part):
        return self.root + ('' if url_part[0] == '/' else '/') + url_part
    
    def _create_auth(self):
        return HTTPBasicAuth(self.username, self.password) if self.auth else None

