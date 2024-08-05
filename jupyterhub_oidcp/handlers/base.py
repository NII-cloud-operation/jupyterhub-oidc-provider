from oic.oic.provider import Provider
from oic.utils.http_util import Response
from tornado import web
from tornado.log import app_log


class BaseOIDHandler(web.RequestHandler):
    @property
    def log(self):
        return self.settings.get('log', app_log)

    def initialize(self, provider: Provider):
        self.provider = provider

    def finish_response(self, response: Response):
        if response.status_code == 302 or response.status_code == 303:
            self.redirect(response.message, status=response.status_code)
            return
        self.set_status(response.status_code)
        for k, v in response.headers:
            self.set_header(k, v)
        self.finish(response.message)
