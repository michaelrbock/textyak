#!/usr/bin/env python

import webapp2
import logging
import jinja2
import json
import os
from google.appengine.ext import ndb


jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class MainHandler(BaseHandler):
    def get(self):
        self.write('Hello world!')


class SmsHandler(BaseHandler):
    def post(self):
        city = self.request.get('FromCity').title()
        state = self.request.get('FromState')
        zip_code = self.request.get('FromZip')
        country = self.request.get('FromCountry')
        area_code = self.request.get('From')[2:5]
        body = self.request.get('Body')
        sms = SMS(city=city, state=state, zip_code=zip_code, country=country,
            area_code=area_code, body=body)
        sms.put()

        self.response.headers['Content-Type'] = 'text/xml'
        response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Thanks for the text from %s! Check it out at http://textyak.appspot.com</Message>
</Response>""" % city
        self.write(response)


class TextsHandler(BaseHandler):
    """Possible query param options for each of the SMS properties"""
    pass


class SMS(ndb.Model):
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    country = ndb.StringProperty()
    area_code = ndb.StringProperty()
    body = ndb.StringProperty()
    last_modified = ndb.DateTimeProperty(auto_now=True)


app = webapp2.WSGIApplication([
    ('/?', MainHandler),
    ('/api/sms/?', SmsHandler),
    ('/api/texts/?', TextsHandler)
], debug=True)
