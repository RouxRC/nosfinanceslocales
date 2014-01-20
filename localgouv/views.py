# -*- coding: utf-8 -*-

import os
import json
from pyramid.view import view_config
from pyramid.response import FileResponse
from cornice import Service
from cornice.resource import resource, view
from .models import AdminZoneFinance, DBSession, AdminZone, Stats as StatsModel
from .maps import timemap_registry, MAPS_CONFIG

city_search = Service(name='city_search', path='/city_search', description="city search")

@city_search.get()
def get_city(request):
    term = self.request.matchdict['term']
    results = DBSession.query(AdminZone.id, AdminZone.name, AdminZone.code_insee,
                             func.ST_X(func.ST_Centroid(AdminZone.geometry)),
                             func.ST_Y(func.ST_Centroid(AdminZone.geometry)))\
        .filter(func.lower(AdminZone.name).like(func.lower(func.unaccent(term+"%")))).all()
    def format(result):
        return {'id': result[0], 'name': result[1], 'code_insee': result[2],
                'lat': result[3], 'lng': result[4]}
    return {'results': [format(res) for res in results]}

@resource(collection_path='/timemaps', path='/timemap/{id}')
class TimeMap(object):
    def __init__(self, request):
        self.request = request
    def get(self):
        id = self.request.matchdict['id']
        return {'results': {'var_name': id, 'maps': [m.info for m in map_registry[id]]}}
    def collection_get(self):
        return {'results': [{'var_name': key, 'maps': [m.info for m in map_registry[key]]} for key in MAPS_CONFIG.keys()]}

@resource(collection_path='/finance', path='/finance/{id}')
class AZFinance(object):
    def __init__(self, request):
        self.request = request
    def get(self):
        id = self.request.matchdict['id']
        res = DBSession.query(AdminZone.name, AdminZone.code_insee, AdminZone.code_department, AdminZoneFinance.year, AdminZoneFinance.data).join(AdminZoneFinance, AdminZone.id==AdminZoneFinance.adminzone_id).filter(AdminZone.id==id).order_by('year').all()
        return {'results': res}

@resource(collection_path='/stats', path='/stat/{id}')
class Stats(object):
    def __init__(self, request):
        self.request = request
    def get(self):
        id = self.request.matchdict['id']
        stat = DBSession.query(StatsModel).filter(StatsModel.name==id).first()
        return {'results': {'mean_by_year': json.loads(stat.data['mean_by_year']), 'var_name': id}}
    def collection_get(self):
        stats = DBSession.query(StatsModel).all()
        return {'results': [{'mean_by_year': json.loads(stat.data['mean_by_year']), 'var_name': stat.name} for stat in stats]}

# view for development purpose
from pyramid.response import FileResponse
def index(request):
    here = os.path.dirname(__file__)
    html_file = os.path.join(here, 'client_app', 'index.html')
    return FileResponse(html_file)
