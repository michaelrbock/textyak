#!/usr/bin/env python

import datetime
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
    def get(self):
        """Possible query param options for each of the SMS properties"""

        city = self.request.get('city')
        state = self.request.get('state')
        zip_code = self.request.get('zip_code')
        country = self.request.get('country')
        area_code = self.request.get('area_code')

        if area_code:
            qry = SMS.query(SMS.area_code == area_code).order(-SMS.last_modified)
        elif city:
            qry = SMS.query(SMS.city == city).order(-SMS.last_modified)
        elif state:
            qry = SMS.query(SMS.state == state).order(-SMS.last_modified)
        elif zip_code:
            qry = SMS.query(SMS.zip_code == zip_code).order(-SMS.last_modified)
        elif country:
            qry = SMS.query(SMS.country == country).order(-SMS.last_modified)
        else:
            qry = SMS.query().order(-SMS.last_modified)

        response = {'data': []}
        for text in qry:
            time_since_seconds = (datetime.datetime.utcnow() - text.last_modified).seconds
            hours, remainder = divmod(time_since_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_since = '%sh:%sm:%ss' % (hours, minutes, seconds)
            response['data'].append({'city': text.city, 'state': text.state, 'zip_code':
                text.zip_code, 'country': text.country, 'area_code': text.area_code, 'body':
                text.body, 'time_since': time_since})

        self.write(json.dumps(response))


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
