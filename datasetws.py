from datetime import datetime

from flask import Flask, abort, flash, redirect, render_template, request, url_for, Response
from flask_cors import CORS
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datasource import datasourcebase, Nomenclature, PGM
# from nomenclature import Nomenclature
from dswfs import wfs

WSApp = Flask(__name__, instance_relative_config=True)
CORS(WSApp)
WSApp.debug=True
WSApp.config.from_pyfile('config.py')

@WSApp.route("/")
def indexHandler():
  return redirect("docs/index.html")

@WSApp.route("/data")
def listDataServices():
  # WSApp.logger.debug("listDataServices called.")
  interfaces = {}
  datasrc = datasourcebase.factory ('nomenclature', WSApp.config)
  interfaces['nomenclature'] = datasrc.loadInterfaces()
  datasrc2 = datasourcebase.factory ('pgm', WSApp.config)
  interfaces['pgm'] = datasrc2.loadInterfaces()
  dswfs = wfs (WSApp.config)
  interfaces['wfs'] = dswfs.loadInterfaces()

  metadata = {}
  metadata['datasets'] = {'nomenclature':{}, 'pgm':{}}
  metadata['protocols'] = ['WFS']
  metadata['datasets']['nomenclature']['targets'] = interfaces['nomenclature']['targets']()
  metadata['datasets']['nomenclature']['metadata'] = interfaces['nomenclature']['metadata']()
  metadata['datasets']['nomenclature']['neutralsearch'] = interfaces['wfs']['neutralSearch'](request)
  metadata['datasets']['pgm']['targets'] = interfaces['pgm']['targets']()
  metadata['datasets']['pgm']['metadata'] = interfaces['pgm']['metadata']()
  metadata['datasets']['pgm']['neutralsearch'] = interfaces['wfs']['neutralSearch'](request)
  
  return render_template('datalist.html', metadata=metadata)

@WSApp.route("/data/<dataset>/summary", methods=['GET', 'POST'])
def dataSummary(dataset):
  interfaces = {}
  datasrc = datasourcebase.factory (dataset, WSApp.config)
  interfaces[dataset] = datasrc.loadInterfaces()
  summaryresults = interfaces[dataset]['summary']()

  # WSApp.logger.debug(summaryresults)
  return Response(render_template('astro/summary.json', results=summaryresults), mimetype='application/json')
  #return render_template('astro/summary.json', results=summaryresults)

@WSApp.route("/data/<dataset>/<target>/<protocol>", methods=['GET', 'POST'])
def dataRequest(dataset, target, protocol):
  # WSApp.logger.debug("dataRequest called.")
  interfaces = {}
  datasrc = datasourcebase.factory (dataset, WSApp.config)
  interfaces[dataset] = datasrc.loadInterfaces()
  dswfs = wfs (WSApp.config)
  interfaces['wfs'] = dswfs.loadInterfaces()

  metadata = {"dataset":dataset, "target":target, "protocol":protocol, "request":request}
  # try:
  metadata['datasetmeta'] = interfaces[dataset.lower()]['metadata']()

  metadata['neutralsearch'] = interfaces[protocol.lower()]['neutralSearch'](request)
  metadata['neutralsearch']['target'] = target.upper()
  metadata['searchresults'] = interfaces[dataset.lower()]['search'](metadata['neutralsearch'])
  # WSApp.logger.debug(metadata['searchresults']['columns'])

  return interfaces[protocol.lower()]['renderResponse'](metadata)

  # except:
  #   dump = dir(__builtins__)
  #   WSApp.logger.debug("Exception triggered")
  #   WSApp.logger.debug(metadata)
  #   WSApp.logger.debug(interfaces)

  #   return render_template('datasetresult.html', searchargs=metadata)

if __name__ == "__main__":
  WSApp.run(debug=True)

