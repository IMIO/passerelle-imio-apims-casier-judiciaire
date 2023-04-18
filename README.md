Passerelle connector with BAEC services 
=======================================

This passerelle is meant to be connected to BAEC using iMio API Microservices 
(APIMS). APIMS interrogates BOSA's services.

Installation
------------

 - add to Passerelle installed apps settings:
   INSTALLED_APPS += ('passerelle_imio_apims_baec',)

 - enable module:
   PASSERELLE_APP_PASSERELLE_IMIO_APIMS_BAEC_ENABLED = True


Usage
-----

 - create and configure new connector
   - Title/description: whatever you want

 - test service by clicking on the available links
   - the /test/ endpoint to test the connection with APIMS
