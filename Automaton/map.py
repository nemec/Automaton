#!/usr/bin/env python

import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json
import unicodedata
import re

def execute(arg = ''):
  if arg == '':
    return help()

  origin, sep, destination = arg.partition(" to ")
  if sep == '':
    return help()

  params = {
    'q':        'from:%s to:%s' % (origin, destination),
    'output':   'json',
    'oe':       'utf8',
  }

  encoded_params = urllib.urlencode(params)    
  url = 'http://maps.google.com/maps/nav?' + encoded_params
  request = urllib2.Request(url)
  resp = urllib2.urlopen(request)
  response = json.load(resp)

  status_code = response['Status']['code']
  if status_code == 200:
    steps = response['Directions']['Routes'][0]['Steps']
    ret = ""
    print steps
    for line in steps:
      ret = ret + line['descriptionHtml'] + ' for ' + line['Distance']['html'] + '\n'
      ret = re.sub(r'<.*?>', '', ret) # Strips HTML tags
      ret = re.sub(r'&[^ ]*?;', '', ret) # Strips HTML special characters (ie. &quot; )
    return ret.rstrip()
  elif status_code == 602:
    return 'malformed query'

def help():
  return """
          USAGE: map [origin] to [destination]
          Returns text directions from origin to destination from GMaps
         """
