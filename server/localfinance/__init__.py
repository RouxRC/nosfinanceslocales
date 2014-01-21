"""Main entry point
"""
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    # XXX Add app static files and index route for dev purpose only
    config.add_static_view('app', settings['app_dir'], cache_max_age=3600)
    config.add_view('localfinance.views.index', route_name='index')
    config.add_route('index', '/')

    # API
    config.include("cornice")
    config.route_prefix = '/api'
    config.scan("localfinance.views")
    return config.make_wsgi_app()
