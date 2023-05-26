import pytz

from datetime import datetime, timedelta

def older_than_ndays(date, ndays):
  ''' return true if date in utc is more than ndays ago '''
  now = datetime.utcnow()
  now_utc = now.replace(tzinfo=pytz.utc)
  ndays_ago_date = now_utc - timedelta(days=ndays)
  if date < ndays_ago_date:
    return True
  else:
    return False

def date_nhours_ago(nhours):
  ''' return the utc datetime that is nhours ago '''
  now = datetime.utcnow()
  now_utc = now.replace(tzinfo=pytz.utc)
  return now_utc - timedelta(hours=nhours)
