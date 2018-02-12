from sqlalchemy import create_engine, Column, DateTime, String, Integer, func, Float, distinct
from sqlalchemy.orm import relationship, backref, sessionmaker, query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import label
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import json
from shapely.geometry import shape
from shapely.wkb import loads as wkbloads, dumps as gjdumps
from geojson import Feature, FeatureCollection
from osgeo import ogr

Base = declarative_base()
ogr.UseExceptions()

class datasourcebase(object):
  """
  The base class and factory method for data sources supported in the web services framework
  """
  def factory(source, config):
    """The factory method of the datasourcebase class is used to create data source classes such as Nome7yynclature
    and the Planetary Geologic Mappers
    
    :param source: The name of the data source class to create ('nomenclature', 'pgm')
    :param config: A Flask config object from instance/config.py

    :rtype: An instance of the class corresponding to the source
    """
    if source.lower() == 'nomenclature': return Nomenclature(config)
    if source.lower() == 'pgm': return PGM(config)
  factory = staticmethod(factory)

  def loadInterfaces(self):
    """Required class method which must be implemented by all classes available through the factory method

    :rtype: A dict of keys pointing to method handles
    """
    raise NotImplementedError()

class DailyCF(Base):
  """
  An ORM class mapping to a daily table simplifying the Nomenclature database schema
  """
  __tablename__ = 'daily_current_features'
  feature_id = Column (Integer, primary_key=True)
  name = Column (String)
  clean_name = Column (String)
  legacy_name = Column (String)
  ethnicity_name = Column (String)
  ct_ethnicity = Column (String)
  system = Column (String)
  target = Column (String)
  target_display_name = Column (String)
  mean_radius = Column (Float)
  feature_type = Column (String)
  reference = Column (String)
  description = Column (String)
  status = Column (String)
  approval_date = Column (DateTime)
  origin = Column (String)
  feature_updated_on = Column (DateTime)
  geometry = Column (Geometry('geometry'))
  gml2 = Column (String)
  gml3 = Column (String)
  center_point = Column (Geometry('center_point'))
  northmostlatitude = Column (Float)
  southmostlatitude = Column (Float)
  eastmostlongitude = Column (Float)
  westmostlongitude = Column (Float)
  diameter = Column (Float)

class DailySummary(Base):
  """
  An ORM class mapping to a summary of the daily table of Nomenclature features
  """
  __tablename__ = 'daily_summary'
  system = Column (String, primary_key=True)
  target = Column (String, primary_key=True)
  feature_type = Column (String, primary_key=True)
  total = Column (Integer)

class Nomenclature:
  """
  The data source factory class for accessing planetary nomenclature
  """

  def __init__(self, config):
    self.config = config
    self.connectionString = config['NOMENCLATURE_DATABASE_URI']

  def loadMetadata(self):
    """Loads the data source meta data for use in rendering templates

    :rtype: A dict of meta data including title, abstract, URL, provider side and details about the data
    """
    metadata = {'dataset':{'title':'Nomenclature WFS Server', 'abstract':'Planetary WFS service hosted by Astrogeology, USGS', 'provider':'Astrogeology, US Geological Survey', 'providersite':'https://astrogeology.usgs.gov', 'onlineresource':'https://planetarynames.wr.usgs.gov','geometryoperands':['gml:Point', 'gml:LineString', 'gml:Polygon', 'gml:Envelope'], 'spatialoperators':['Equals', 'Disjoint', 'Touches', 'Within', 'Overlaps', 'Crosses', 'Intersects', 'Contains', 'DWtihin', 'Beyond', 'BBOX'], 'comparisonoperators':['LessThan', 'GreaterThan', 'LessThanEqualTo', 'GreaterThanEqualTo', 'EqualTo', 'NotEqualTo', 'Like', 'Between']}, 'layers':[{'layer':'POLYGONS', 'title':'Nomenclature Boundaries', 'abstract':'Planetary nomenclature, like terrestrial nomenclature, is used to uniquely identify a feature on the surface of a planet or satellite so that the feature can be easily located, described, and discussed. This gazetteer, hosted by the USGS, contains detailed information about all names of topographic and albedo features on planets and satellites (and some planetary ring and ring-gap systems) that the International Astronomical Union (IAU) has named and approved from its founding in 1919 through the present time.'},{'layer':'CENTERS', 'title':'Nomenclature Centers', 'abstract':'Planetary nomenclature, like terrestrial nomenclature, is used to uniquely identify a feature on the surface of a planet or satellite so that the feature can be easily located, described, and discussed. This gazetteer, hosted by the USGS, contains detailed information about all names of topographic and albedo features on planets and satellites (and some planetary ring and ring-gap systems) that the International Astronomical Union (IAU) has named and approved from its founding in 1919 through the present time.'}]}

    return metadata

  def nomenSearch(self, neutralSearch):
    """Uses the neutral search from the selected protocol to search the Nomenclature database and return the results
    
    :param neutralSearch: a dict of search criteria parsed by the protocol

    :rtype: a dict of the search results
    """
    engine = create_engine(self.connectionString)

    Session = sessionmaker(bind=engine)
    session = Session()

    queryResults = session.query(DailyCF)
    if neutralSearch.get('target'):
      queryResults = queryResults.filter(DailyCF.target == neutralSearch.get('target'))
    if neutralSearch['criteria'].get('bboxWKT'):
      queryResults = queryResults.filter(DailyCF.geometry.ST_Intersects(neutralSearch['criteria'].get('bboxWKT')))

    queryResults.add_column (DailyCF.geometry.ST_AsGeoJSON().label("geojson"))

    # Create array of result column names, convert results iterator into an array
    searchResult = {}
    # searchResult['columns'] = queryResults.column_descriptions
    searchResult['columns'] = self.config['NOMENCLATURE_FEATURE_COLUMNS']
    searchResult['feature_name'] = self.config['NOMENCLATURE_FEATURE_NAME']
    searchResult['results'] = []
    for feature in queryResults.all():
      shpgeom = to_shape(feature.geometry)
      currFeature = feature.__dict__
      currFeature.pop('geometry', None)
      currFeature.pop('center_point', None)
      searchResult['results'].append(Feature(id=feature.feature_id, geometry=shpgeom, properties=currFeature))

    return searchResult

  def treeSummary(self):
    engine = create_engine(self.connectionString)

    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(DailySummary).all()

    treeResult = {}
    for result in results:
      if result.system not in treeResult.keys():
        treeResult[result.system] = {}
      if result.target not in treeResult[result.system].keys():
        treeResult[result.system][result.target] = []
        url = "https://planetarynames.wr.usgs.gov/SearchResults?target=" + result.target + "&featureType=" + result.feature_type
        # url = urllib.quote(urltmp)
      treeResult[result.system][result.target].append({"type": result.feature_type, "total": result.total, "url": url.replace(" ", "%20")})

  
    return treeResult

  def listTargets(self):
    engine = create_engine(self.connectionString)

    Session = sessionmaker(bind=engine)
    session = Session()

    targets = session.query(distinct(DailyCF.target))

    resultTargets = [t[0] for t in targets]

    return resultTargets

  def loadInterfaces(self):
    interfaces = {}
    interfaces['metadata'] = self.loadMetadata
    interfaces['search'] = self.nomenSearch
    interfaces['targets'] = self.listTargets
    interfaces['summary'] = self.treeSummary

    return interfaces

class PGM:
  """
  The data source factory class for accessing the planetary geologic mappers database
  """

  def __init__(self, config):
    self.config = config
    path_to_shape = config['PGM_PATH_TO_SHAPE']
    self.shape_table = config['PGM_SHAPENAME']
    shapedriver = ogr.GetDriverByName('ESRI Shapefile')

    self.dataSource = shapedriver.Open(path_to_shape, 0) # 0 means read-only. 1 means writeable.

    # Check to see if shapefile is found.
    if self.dataSource is None:
      print 'Could not open %s' % (path_to_shape)
    else:
      print 'Opened %s' % (path_to_shape)

  def loadMetadata(self):
    metadata = {'dataset':{'title':'Planetary Geologic Mappers WFS Server', 'abstract':'Planetary WFS service hosted by Astrogeology, USGS', 'provider':'Astrogeology, US Geological Survey', 'providersite':'https://astrogeology.usgs.gov', 'onlineresource':'https://planetarymapping.wr.usgs.gov','geometryoperands':['gml:Point', 'gml:LineString', 'gml:Polygon', 'gml:Envelope'], 'spatialoperators':['Equals', 'Disjoint', 'Touches', 'Within', 'Overlaps', 'Crosses', 'Intersects', 'Contains', 'DWtihin', 'Beyond', 'BBOX'], 'comparisonoperators':['LessThan', 'GreaterThan', 'LessThanEqualTo', 'GreaterThanEqualTo', 'EqualTo', 'NotEqualTo', 'Like', 'Between']}, 'layers':[{'layer':'POLYGONS', 'title':'Mapping Boundaries', 'abstract':'Planetary Mapping'}]}

    return metadata

  def pgmSearch(self, neutralSearch):

    # Create array of result column names, convert results iterator into an array
    searchResult = {'columns':[], 'results': []}

    searchResult['columns'] = self.config['PGM_FEATURE_COLUMNS']
    searchResult['feature_name'] = self.config['PGM_FEATURE_NAME']
    target_name = self.config['PGM_TARGET_NAME']
    path_to_shape = self.config['PGM_PATH_TO_SHAPE']
    shape_table = self.config['PGM_SHAPENAME']
    shapedriver = ogr.GetDriverByName('ESRI Shapefile')

    dataSource = shapedriver.Open(path_to_shape, 0) # 0 means read-only. 1 means writeable.
    if dataSource is None: return ['failed', 'to', 'open', 'shapefile']
    sql = 'SELECT * FROM ' + shape_table

    if (neutralSearch.get('target') and neutralSearch.get('target').upper() != 'ALL'):
      target = neutralSearch.get('target').upper()
      sql += ' WHERE ' + target_name + '=\'' + target + '\''

    layer = dataSource.ExecuteSQL(str(sql))
    ldefn = layer.GetLayerDefn()
    searchResult['results'] = []
    for feature in layer:
      shpgeom = shape(json.loads(feature.GetGeometryRef().ExportToJson()))
      currFeature = {}
      for key in searchResult['columns']:
        currFeature[key] = feature.GetField(key)
      searchResult['results'].append(Feature(id=feature.GetFID(), geometry=shpgeom, properties=currFeature))

    return searchResult

  def treeSummary(self):
    feature_name = self.config['PGM_FEATURE_NAME']
    target_name = self.config['PGM_TARGET_NAME']
    type_name = self.config['PGM_TYPE_NAME']
    path_to_shape = self.config['PGM_PATH_TO_SHAPE']
    shape_table = self.config['PGM_SHAPENAME']
    shapedriver = ogr.GetDriverByName('ESRI Shapefile')

    print "Type: " + type_name + " target: " + target_name + "\n"

    dataSource = shapedriver.Open(path_to_shape, 0) # 0 means read-only. 1 means writeable.
    if dataSource is None: return ['failed', 'to', 'open', 'shapefile']
    sql = 'SELECT * FROM ' + shape_table

    layer = dataSource.ExecuteSQL(str(sql))

    system = 'Planetary Geologic Mapping'
    treeResult = {system:{}}
    for feature in layer:
      target = feature.GetField(target_name)
      status = feature.GetField(type_name)

      if target not in treeResult[system].keys():
        treeResult[system][target] = []
        url = "https://planetarymapping.wr.usgs.gov/Project"
        treeResult[system][target].append({"type": status.upper(), "total": 1, "url": url.replace(" ", "%20")})
      else:
        if not any(d['type'].upper() == status.upper() for d in treeResult[system][target]):
          treeResult[system][target].append({"type": status.upper(), "total": 1, "url": url.replace(" ", "%20")})
        for stat in treeResult[system][target]:
          if stat['type'].upper() == status.upper():
            stat['total'] += 1
  
    return treeResult

  def listTargets(self):

    resultTargets = []
    target_name = self.config['PGM_TARGET_NAME']
    path_to_shape = self.config['PGM_PATH_TO_SHAPE']
    shape_table = self.config['PGM_SHAPENAME']
    shapedriver = ogr.GetDriverByName('ESRI Shapefile')

    dataSource = shapedriver.Open(path_to_shape, 0) # 0 means read-only. 1 means writeable.
    if dataSource is None: return ['failed', 'to', 'open', 'shapefile']
    sql = 'SELECT DISTINCT ' + target_name + ' FROM ' + shape_table
    layer = dataSource.ExecuteSQL(sql)
    for i, feature in enumerate(layer):
      resultTargets.append(feature.GetField(0))
     
    return resultTargets

  def loadInterfaces(self):
    interfaces = {}
    interfaces['metadata'] = self.loadMetadata
    interfaces['search'] = self.pgmSearch
    interfaces['targets'] = self.listTargets
    interfaces['summary'] = self.treeSummary

    return interfaces
