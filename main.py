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
        self.render('index.html')


class ViewHandler(BaseHandler):
    def get(self):
        self.render('view.html')


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
    <Message>Thanks for the text from area code (%s)! Check it out at http://textyak.appspot.com/view</Message>
</Response>""" % area_code
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
            qry = SMS.query(SMS.area_code == area_code).order(-SMS.date)
        elif city:
            qry = SMS.query(SMS.city == city).order(-SMS.date)
        elif state:
            qry = SMS.query(SMS.state == state).order(-SMS.date)
        elif zip_code:
            qry = SMS.query(SMS.zip_code == zip_code).order(-SMS.date)
        elif country:
            qry = SMS.query(SMS.country == country).order(-SMS.date)
        else:
            qry = SMS.query().order(-SMS.date)

        response = {'data': []}
        for text in qry:
            time_since_seconds = (datetime.datetime.utcnow() - text.date).seconds
            hours, remainder = divmod(time_since_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_since = '%sh:%sm:%ss' % (hours, minutes, seconds)
            response['data'].append({'city': text.city, 'state': text.state, 'zip_code':
                text.zip_code, 'country': text.country, 'area_code': text.area_code, 'body':
                text.body, 'time_since': time_since})

        self.write(json.dumps(response))


class CategoriesHandler(BaseHandler):
    def get(self):
        qry = SMS.query().order(-SMS.date)

        response = {'cities': set(), 'states': set(), 'zip_codes': set(), 'countries': set(),
            'area_codes': set()}

        for text in qry:
            response['cities'].add(text.city)
            response['states'].add(text.state)
            response['zip_codes'].add(text.zip_code)
            response['countries'].add(text.country)
            response['area_codes'].add(text.area_code)

        for key in response:
            response[key] = list(response[key])

        self.write(json.dumps(response))


class SMS(ndb.Model):
    city = ndb.StringProperty()
    state = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    country = ndb.StringProperty()
    area_code = ndb.StringProperty()
    body = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


app = webapp2.WSGIApplication([
    ('/?', MainHandler),
    ('/view/?', ViewHandler),
    ('/api/sms/?', SmsHandler),
    ('/api/texts/?', TextsHandler),
    ('/api/categories/?', CategoriesHandler)
], debug=True)
