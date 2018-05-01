from flask import Flask, abort, render_template, request, url_for, Response
import re

class wfs:
  'Web Feature Service (WFS) protocol class implementation'

  def __init__(self, config):
    self.config = config

  def neutralSearch(self, request):
    neutralCriteria = {}
    neutralCriteria['protocol'] = {}
    neutralCriteria['criteria'] = {}

    # neutralCriteria['base_url'] = request.url_root
    neutralCriteria['base_url'] = request.url_root.replace('http://', 'https://')

    request.args = {k.lower():v for k,v in request.args.items()}
    if request.args.get('request'):
      neutralCriteria['protocol']['request'] = request.args.get('request').lower()
    else:
      neutralCriteria['protocol']['request'] = ''
    if request.args.get('outputformat'):
      neutralCriteria['protocol']['outputformat'] = request.args.get('outputformat').lower()
    else:
      neutralCriteria['protocol']['outputformat'] = ''

    # The following are required parameters, if they are missing we return an error
    # protocolKeywords = ['request', 'service', 'version', 'outputformat']
    protocolKeywords = ['request', 'service', 'version']
    if (request.args.get('request') and neutralCriteria['protocol']['request'] != 'getcapabilities' and neutralCriteria['protocol']['request'] != 'describefeaturetype'):
      for pk in protocolKeywords:
        if request.args.get(pk):
          neutralCriteria['protocol'][pk.lower()] = request.args.get(pk).lower()
        else:
          neutralCriteria['protocol']['code'] = "MissingParameterValue"
          neutralCriteria['protocol']['locator'] = pk
          neutralCriteria['protocol']['error'] = "Request is missing required WFS parameter '" + pk + "'"

    criteriaKeywords = {'typeName':'featureType', 'featureID':'id', 'id':'id', 'maxFeatures':'limit', 'sortBy':'sortby', 'propertyName':'columns', 'bbox':'boundingbox'}

    for key, map in criteriaKeywords.items():
      if request.args.get(key):
        if isinstance(request.args.get(key), basestring):
          neutralCriteria['criteria'][map] = request.args.get(key).lower()
        else:
          neutralCriteria['criteria'][map] = request.args.get(key)

    # also add WKT from bounding box, if it exists
    # BBOX=38.71,-114.33,43.36,-105.36
    if request.args.get('bbox'):
      extents = [x.strip for x in request.args.get('bbox').split(',')]
      neutralCriteria['criteria']['bboxWKT'] = "POLYGON ({a} {b}, {a} {d}, {c} {d}, {c} {b}, {a} {b})".format(a=extents[0], b=extents[1], c=extents[2], d=extents[3])

    return neutralCriteria

  def renderGetCapabilities(self, metadata):
    return Response(render_template('wfs/getcapabilities.xml', metadata=metadata), mimetype='text/xml')

  def renderDescribeFeatureType(self, metadata):
    return Response(render_template('wfs/describefeaturetype.xml', metadata=metadata), mimetype='text/xml')

  def renderGetFeature(self, metadata):
    mime = 'text/xml'
    layout = 'wfs/getfeature.xml'
    if metadata['neutralsearch']['protocol'].get('outputformat'):
      if re.match(r'.*json$', metadata['neutralsearch']['protocol'].get('outputformat').lower()):
        #code=metadata['neutralsearch']['protocol']['outputformat']
        #locator='WFS'
        #error='Matched on matching *.json$'
        #return render_template('wfs/error.xml', exceptioncode=code, locator=locator, error=error)
        layout = 'wfs/getfeature.json'
        mime = 'application/json;charset=UTF-8'

    return Response(render_template(layout, metadata=metadata), mimetype=mime)
    # return Response(render_template(layout, metadata=metadata), mimetype=mime)

  def renderError(code, locator, error):
    return render_template('wfs/error.xml', exceptioncode=code, locator=locator, error=error)

  def renderResponse(self, metadata):
    requests = {}
    requests['getcapabilities'] = self.renderGetCapabilities
    requests['describefeaturetype'] = self.renderDescribeFeatureType
    requests['getfeature'] = self.renderGetFeature

    if metadata['neutralsearch']['protocol'].get('code'):
      return renderError (metadata['neutralsearch']['protocol']['code'], metadata['neutralsearch']['protocol']['locator'], metadata['neutralsearch']['protocol']['error'])
    # try:
    wfsrequest = metadata['neutralsearch']['protocol']['request'].lower()
    return requests[wfsrequest](metadata)
    # except:
    #   return renderError("OperationNotSupported", "request", "Unknown operation requested '" + wfsrequest + "'")

  def loadInterfaces(self):
    interfaces = {}
    interfaces['neutralSearch'] = self.neutralSearch
    interfaces['renderResponse'] = self.renderResponse

    return interfaces
