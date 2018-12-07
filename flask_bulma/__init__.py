#!/usr/bin/env python
# coding=utf8

import re

from flask import Blueprint, current_app, url_for


__version__ = '0.7.2'
BULMA_VERSION = re.sub(r'^(\d+\.\d+\.\d+).*', r'\1', __version__)
JQUERY_VERSION = '3.3.1'


class CDN(object):
    """Base class for CDN objects."""

    def get_resource_url(self, filename):
        """Return resource url for filename."""
        raise NotImplementedError


class StaticCDN(object):
    """A CDN that serves content from the local application.

    :param static_endpoint: Endpoint to use.
    :param rev: If ``True``, honor ``BULMA_QUERYSTRING_REVVING``.
    """

    def __init__(self, static_endpoint='static', rev=False):
        self.static_endpoint = static_endpoint
        self.rev = rev

    def get_resource_url(self, filename):
        extra_args = {}

        if self.rev and current_app.config['BULMA_QUERYSTRING_REVVING']:
            extra_args['bulma'] = __version__

        return url_for(self.static_endpoint, filename=filename, **extra_args)


class WebCDN(object):
    """Serves files from the Web.

    :param baseurl: The baseurl. Filenames are simply appended to this URL.
    """

    def __init__(self, baseurl):
        self.baseurl = baseurl

    def get_resource_url(self, filename):
        return self.baseurl + filename


class ConditionalCDN(object):
    """Serves files from one CDN or another, depending on whether a
    configuration value is set.

    :param confvar: Configuration variable to use.
    :param primary: CDN to use if the configuration variable is ``True``.
    :param fallback: CDN to use otherwise.
    """

    def __init__(self, confvar, primary, fallback):
        self.confvar = confvar
        self.primary = primary
        self.fallback = fallback

    def get_resource_url(self, filename):
        if current_app.config[self.confvar]:
            return self.primary.get_resource_url(filename)
        return self.fallback.get_resource_url(filename)


def bulma_find_resource(filename, cdn='static', use_minified=None, local=True):
    """Resource finding function, also available in templates.

    :param filename: File to find a URL for.
    :param cdn: Name of the CDN to use.
    :param use_minified': If set to ``True``/``False``, use/don't use
                          minified. If ``None``, honors
                          ``BULMA_USE_MINIFIED``.
    :param local: If ``True``, uses the ``local``-CDN when
                  ``BULMA_SERVE_LOCAL`` is enabled. If ``False``, uses
                  the ``static``-CDN instead.
    :return: A URL.
    """
    config = current_app.config

    if use_minified is None:
        use_minified = config['BULMA_USE_MINIFIED']

    if use_minified:
        filename = '%s.min.%s' % tuple(filename.rsplit('.', 1))

    cdns = current_app.extensions['bulma']['cdns']
    resource_url = cdns[cdn].get_resource_url(filename)

    if resource_url.startswith('//'):
        resource_url = 'https:%s' % resource_url
    return resource_url


class Bulma(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('BULMA_USE_MINIFIED', True)

        app.config.setdefault('BULMA_QUERYSTRING_REVVING', True)
        app.config.setdefault('BULMA_SERVE_LOCAL', True)

        app.config.setdefault('BULMA_LOCAL_SUBDOMAIN', None)

        blueprint = Blueprint(
            'bulma',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/bulma',
            subdomain=app.config['BULMA_LOCAL_SUBDOMAIN'])

        # # add the form rendering template filter
        # blueprint.add_app_template_filter(render_form)

        app.register_blueprint(blueprint)

        # app.jinja_env.globals['bulma_is_hidden_field'] =\
        #     is_hidden_field_filter
        app.jinja_env.globals['bulma_find_resource'] =\
            bulma_find_resource
        app.jinja_env.add_extension('jinja2.ext.do')

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        local = StaticCDN('bulma.static', rev=False)
        static = StaticCDN()

        def lwrap(cdn, primary=static):
            return ConditionalCDN('BULMA_SERVE_LOCAL', primary, cdn)

        bulma = lwrap(
            WebCDN('//cdn.bootcss.com/bulma/%s/' %
                   __version__), local)

        jquery = lwrap(
            WebCDN('//cdn.bootcss.com/jquery/%s/' %
                   JQUERY_VERSION), local)

        # local - folder of the package
        # static - folder of the current app
        # bulma - TODO
        # jquery - TODO
        app.extensions['bulma'] = {
            'cdns': {
                'local': local,
                'static': static,
                'bulma': bulma,
                'jquery': jquery
            },
        }
