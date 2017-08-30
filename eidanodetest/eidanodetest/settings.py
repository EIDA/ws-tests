# -*- coding: utf-8 -*-
"""

EIDA Mediator settings.

This file is part of the EIDA mediator/federator webservices.

"""

import os


# NOTE: arclink servers/ports are from
# http://eida.gfz-potsdam.de/eida/status/master_table.php
# (last accessed 2017-08-17)
EIDA_NODES = {
    'gfz': {
        'name': 'Deutsches GeoForschungsZentrum Potsdam',
        'services': {
            'arclink': {
                'server': 'eida.gfz-potsdam.de',
                'port': 18002},
            'fdsn': {
                'server': 'http://geofon.gfz-potsdam.de',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://geofon.gfz-potsdam.de',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'CZ',
            'station': 'VRAC',
            'location': '--',
            'channel': 'HH?',
            'startdate': '2012-06-01T00:00:00'}
        },
        
    'odc': {
        'name': 'Orfeus Data Center',
        'services': {
            'arclink': {
                'server': 'bhlsa02.knmi.nl',
                'port': 18002},
            'fdsn': {
                'server': 'http://www.orfeus-eu.org',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://www.orfeus-eu.org',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'NL',
            'station': 'OPLO',
            'location': '01',
            'channel': 'BH?',
            'startdate': '2009-11-01T00:00:00'}
        },
        
    'eth': {
        'name': 'Swiss Seismological Service',
        'services': {
            'arclink': {
                'server': 'eida.ethz.ch',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida.ethz.ch',
                'station': True,
                'dataselect': True,
                'event': True}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://eida.ethz.ch',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'CH',
            'station': 'DAVOX',
            'location': '--',
            'channel': 'HH?',
            'startdate': '2002-08-01T00:00:00'}
        },
        
    'resif': {
        'name': u'Réseau sismologique & géodésique français',
        'services': {
            'arclink': {
                'server': 'eida.resif.fr',
                'port': 18001},
            'fdsn': {
                'server': 'http://ws.resif.fr',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': False,
                    'static_file': 'http://ws.resif.fr/eida_routing.xml'},
                'wfcatalog': {
                    'url': 'http://ws.resif.fr/eidaws/wfcatalog/1/',
                    'server': 'http://ws.resif.fr'}
                }
            },
        'testquerysncls': {
            'network': 'FR',
            'station': 'SJAF',
            'location': '00',
            'channel': 'HH?',
            'startdate': '2007-02-01T00:00:00'}
        },
        
    'ingv': {
        'name': 'Italian Seismic Data Center',
        'services': {
            'arclink': {
                'server': 'eida.ingv.it',
                'port': 18002},
            'fdsn': {
                'server': 'http://webservices.rm.ingv.it',
                'station': True,
                'dataselect': True,
                'event': True}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': ' http://eida.ingv.it',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'IV',
            'station': 'BOB',
            'location': '--',
            'channel': 'HHZ',
            'startdate': '2003-08-01T00:00:00'}
        },
        
    'bgr': {
        'name': 'BGR Hannover',
        'services': {
            'arclink': {
                'server': 'eida.bgr.de',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida.bgr.de',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://eida.bgr.de',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'GR',
            'station': 'BFO',
            'location': '--',
            'channel': 'HH?',
            'startdate': '1991-01-01T00:00:00'}
        },
        
    'lmu': {
        'name': 'BayernNetz',
        'services': {
            'arclink': {
                'server': 'erde.geophysik.uni-muenchen.de',
                'port': 18001},
            'fdsn': {
                'server': 'http://erde.geophysik.uni-muenchen.de',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://erde.geophysik.uni-muenchen.de',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'BW',
            'station': 'ZUGS',
            'location': '--',
            'channel': 'EHZ',
            'startdate': '2006-03-01T00:00:00'}
        },
        
    'ipgp': {
        'name': 'INSTITUT DE PHYSIQUE DU GLOBE DE PARIS Data Center',
        'services': {
            'arclink': {
                'server': 'eida.ipgp.fr',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida.ipgp.fr',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://eidaws.ipgp.fr',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'MQ',
            'station': 'LPM',
            'location': '00',
            'channel': 'HH?',
            'startdate': '2013-05-01T00:00:00'}
        },
        
    'niep': {
        'name': 'National Institute for Earth Physics Romania',
        'services': {
            'arclink': {
                'server': 'eida-sc3.infp.ro',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida-sc3.infp.ro',
                'station': True,
                'dataselect': True,
                'event': True}, 
            'eida': {
                'routing': {
                    'service': False,
                    'static_file': 'http://eida-routing.infp.ro/eidaws/routing/1/routing.xml'},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'RO',
            'station': 'MLR',
            'location': '--',
            'channel': 'HH?',
            'startdate': '2001-04-01T00:00:00'}
        },
        
    'koeri': {
        'name': 'Bogazici University Kandilli Observatory and ERI',
        'services': {
            'arclink': {
                'server': 'eida-service.koeri.boun.edu.tr',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida-service.koeri.boun.edu.tr',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://eida.koeri.boun.edu.tr',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'KO',
            'station': 'ELL',
            'location': '--',
            'channel': 'BH?',
            'startdate': '2006-10-01T00:00:00'}
        },
        
    'noa': {
        'name': 'National Observatory of Athens, Institute of Geodynamics',
        'services': {
            'arclink': {
                'server': 'eida.gein.noa.gr',
                'port': 18001},
            'fdsn': {
                'server': 'http://eida.gein.noa.gr',
                'station': True,
                'dataselect': True,
                'event': False}, 
            'eida': {
                'routing': {
                    'service': True,
                    'server': 'http://eida.gein.noa.gr',
                    'static_file': ''},
                'wfcatalog': {
                    'url': '',
                    'server': ''}
                }
            },
        'testquerysncls': {
            'network': 'HL',
            'station': 'IDI',
            'location': '--',
            'channel': 'HH?',
            'startdate': '2011-01-01T00:00:00'}
        }
    }


FDSN_EVENT_SERVICES = {
    'eth': {
        'server': 'http://arclink.ethz.ch'},
    'ingv': {
        'server': 'http://webservices.rm.ingv.it'},
    'niep': {
        'server': 'http://eida-sc3.infp.ro'},
    'iris': {
        'server': 'http://service.iris.edu'},
    'usgs': {
        'server': 'https://earthquake.usgs.gov'},
    'ncedc': {
        'server': 'http://service.ncedc.org'},
    'scedc': {
        'server': 'http://service.scedc.caltech.edu'},
    'isc': {
        'server': 'http://www.isc.ac.uk'}
}


OTHER_SERVERS = {
    'iris': {
        'name': 'IRIS Data Management Center',
        'services': {
            
            # is there an IRIS arclink server?
            'fdsn': {
                'server': 'http://service.iris.edu',
                'station': True,
                'dataselect': True,
                'event': True}
            },
        
        # HHZ, HH1, HH2 (100 sps) ??
        'testquerysncls': {
            'network': 'IU',
            'station': 'ULN',
            'location': '10',
            'channel': 'BH?',
            'startdate': '2013-10-01T00:00:00'}
    },
    
    # service.ncedc.org
    'ncedc': {
        'name': 'Northern California Earthquake Data Center',
        'services': {
            
            'fdsn': {
                'server': 'http://service.ncedc.org',
                'station': True,
                'dataselect': True,
                'event': True}
            },
        
        # ????
        'testquerysncls': {
            'network': 'BK',
            'station': 'VAK',
            'location': '00',
            'channel': 'BH?',
            'startdate': '2010-09-01T00:00:00'}
    },
    
    # scedc.caltech.edu/
    # disabled, because it seems to have strict surge protection, and does not
    # provide POST
    #'scedc': {
        #'name': 'SCEDC',
        #'services': {
            
            #'fdsn': {
                #'server': 'http://service.scedc.caltech.edu',
                #'station': True,
                #'dataselect': True,
                #'event': True}
            #},
        
        #'testquerysncls': {
            #'network': 'CI',
            #'station': 'CJM',
            #'location': '--',
            #'channel': 'HH?',
            #'startdate': '2011-11-01T00:00:00'}
    #},

        
    # www.moho.iag.usp.br
    'usp': {
        'name': u'Centro de Sismologia da Universidade de São Paulo',
        'services': {
            'arclink': {
                'server': 'seisrequest.iag.usp.br',
                'port': 18001},
            
            'fdsn': {
                'server': 'http://seisrequest.iag.usp.br',
                'station': True,
                'dataselect': True,
                'event': False}
            },
        
        'testquerysncls': {
            'network': 'BR',
            'station': 'SALV',
            'location': '--',
            'channel': 'HH?',
            'startdate': '2012-06-01T00:00:00'}
    }   
}

        
DEFAULT_ROUTING_SERVICE = 'gfz'
DEFAULT_EVENT_SERVICE = 'usgs'

SERVER_NAME = 'EIDA Mediator (alpha)'
VERSION = '0.9.1'
SHARE_DIR = 'share'


FDSN_STATION_PATH = '/fdsnws/station/1/'
FDSN_DATASELECT_PATH = '/fdsnws/dataselect/1/'
FDSN_EVENT_PATH = '/fdsnws/event/1/'

EIDA_ROUTING_PATH = '/eidaws/routing/1/'

EIDA_MEDIATOR_PATH = '/eidaws/mediator/'

EIDA_MEDIATOR_DQ_PATH = '/eidaws/mediator/dq/'
EIDA_MEDIATOR_RQ_PATH = '/eidaws/mediator/rq/'
EIDA_MEDIATOR_AQ_PATH = '/eidaws/mediator/aq/'

MEDIATOR_QUERY_METHOD_TOKEN = 'query'
MEDIATOR_VERSION_METHOD_TOKEN = 'version'

EIDA_FEDERATOR_BASE_URL = 'http://mediator-devel.ethz.ch'
EIDA_FEDERATOR_PORT = 80

EIDA_FEDERATOR_SERVICES = ('dataselect', 'station')

IRIS_FDSNWS_BASE_URL = 'http://service.iris.edu'
IRIS_FDSNWS_PORT = 80

IRIS_FDSNWS_SERVICES = ('dataselect', 'station')


# -----------


FDSN_QUERY_METHOD_TOKEN = 'query'
FDSN_VERSION_METHOD_TOKEN = 'version'
FDSN_WADL_METHOD_TOKEN = 'application.wadl'
FDSN_DATASELECT_QUERYAUTH_METHOD_TOKEN = 'queryauth'

FDSN_DATASELECT_VERSION = '1.1.0'
FDSN_STATION_VERSION = '1.1.0'

FDSN_WADL_DIR = SHARE_DIR
FDSN_DATASELECT_WADL_FILENAME = 'dataselect.wadl'
FDSN_STATION_WADL_FILENAME = 'station.wadl'

DATASELECT_MIMETYPE = 'application/vnd.fdsn.mseed'
STATION_MIMETYPE_XML = 'application/xml'
STATION_MIMETYPE_TEXT = 'text/plain'
VERSION_MIMETYPE = 'text/plain'
WADL_MIMETYPE = 'application/xml'


FDSN_DEFAULT_NO_CONTENT_ERROR_CODE = 204

FDSN_SERVICE_DOCUMENTATION_URI = 'http://www.fdsn.org/webservices/'


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_SHARE = os.path.join(APP_ROOT, SHARE_DIR)