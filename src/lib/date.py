import pytz

from datetime import datetime, timedelta
from dateutil.parser import parse as parsedatetime

def date1_older(date1, date2):
  ''' given datetime objects date1 and date2, return true if date1 older '''
  return date1 < date2

def now_utc():
  ''' return now datetime object with utc timezone '''
  now = datetime.utcnow()
  now_utc = now.replace(tzinfo=pytz.utc)
  return now_utc

def over_ndays_ago(date_str, ndays):
  '''
  return true if date_str is more than ndays ago,
  assume date_str has utc timezone info.
  '''
  date_obj = parsedatetime(date_str)
  ndays_ago_date = now_utc() - timedelta(days=ndays)
  return date1_older(date_obj, ndays_ago_date)

def over_nhours_ago(date_str, nhours):
  '''
  return true if date_str is more than nhours ago,
  assume date_str has utc timezone info.
  '''
  date_obj = parsedatetime(date_str)
  nhours_ago_date = now_utc() - timedelta(hours=nhours)
  return date1_older(date_obj, nhours_ago_date)
