# datasetws
Data set web services on Git updated thru Atom

Container requires an `instance/config.py` to be created with the following contents:
```
# Nomenclature settings
NOMENCLATURE_DATABASE_URI = ...
NOMENCLATURE_FEATURE_COLUMNS = {'name':'name', 'diameter':'diameter', 'feature_type':'feature_type'}
NOMENCLATURE_FEATURE_NAME='name'

# PGM Settings
PGM_PATH_TO_SHAPE = '/path/to/PGM_Website.shp'
PGM_SHAPENAME = 'PGM_Website'

PGM_FEATURE_COLUMNS = {'Map_Title':'Map Title', 'USGS_No':'USGS Number', 'Status':'Status', 'PI_Last':'Author Last Name', 'PI_First':'Author First Name', 'Projection':'Projection', 'Scale':'Scale', 'Body':'Target', 'Online_Pub':'Online Publication', 'Pub_Date':'Publication Date'}

PGM_FEATURE_NAME='Map_Title'
PGM_TARGET_NAME='Body'
PGM_TYPE_NAME='Status'
```
