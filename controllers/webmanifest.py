from odoo import http
from odoo.addons.web.controllers import webmanifest
from odoo.http.stream import Stream

ICON = '/weberq_branding/static/img/icon-%s.png'


class WebManifest(webmanifest.WebManifest):
    """ The WeberQ icon for the app installed from the browser. """

    def _get_webmanifest(self):
        manifest = super()._get_webmanifest()
        for icon in manifest.get('icons', []):
            if '/web/static/img/odoo-icon' in icon.get('src', ''):
                icon['src'] = ICON % icon.get('sizes', '192x192')
        return manifest

    def _icon_path(self):
        return 'weberq_branding/static/img/icon-192x192.png'

    @http.route()
    def scoped_app(self, app_id, path='', app_name=''):
        response = super().scoped_app(app_id, path, app_name)
        if hasattr(response, 'qcontext') and response.qcontext.get('apple_touch_icon', '').startswith('/web/static/img/odoo-icon'):
            response.qcontext['apple_touch_icon'] = ICON % 'ios'
        return response


class Favicon(http.Controller):

    @http.route('/favicon.ico', type='http', auth='none', methods=['GET'], save_session=False, readonly=True)
    def favicon(self):
        return Stream.from_path('weberq_branding/static/img/favicon.ico').get_response(max_age=86400)
