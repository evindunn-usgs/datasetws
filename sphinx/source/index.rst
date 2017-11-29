.. Database Web Services documentation master file, created by
   sphinx-quickstart on Wed Jul 19 09:30:34 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Database Web Services' documentation
====================================
.. toctree::
   :maxdepth: 2

Database Web Services
---------------------
The USGS Astrogeology Science Center's database web services is a ReSTful framework for accessing multiple databases
with consistent protocols. These services are provided to allow web developers, GIS users and anyone using an OGC
compliant tool to access the data through a single gateway that is simple to configure in tools.  Currently, the Planetary Nomenclature database is searchable using the OGC WFS protocol in both GeoJSON and GML formats.  

* List of available `Nomenclature WFS Services`_

Additionally, there is a summary JSON interface for each database which can be used to populate navigation tools 

* A `D3 Javascript`_ visualization of `Nomenclature Summary`_ and `PGM Summary`_ 

  * The raw `Nomenclature Summary JSON`_
  * The raw `PGM Summary JSON`_

Tests and Coding Examples
-------------------------
We have OpenLayer 3 examples that access the Io Nomenclature data through WFS using the database web services and a
MapServer baseline.

* `Io WFS Nomenclature Openlayers Example`_

.. _Nomenclature WFS Services: ../data
.. _Nomenclature Summary: ../examples/d3/circlepack.html
.. _PGM Summary: ../examples/d3/pgmpack.html
.. _Nomenclature Summary JSON: ../data/nomenclature/summary
.. _PGM Summary JSON: ../data/nomenclature/summary
.. _Io WFS Nomenclature Openlayers Example: ../examples/ol_vector_w_code.html
.. _D3 Javascript: https://d3js.org/


Classes and Files
-----------------
.. toctree::
   datasetws
   dswfs
   datasource

* :ref:`search`

