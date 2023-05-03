import pytz

from datetime import datetime, timedelta

from lib.date import \
  older_than_ndays

def describe_older_than_ndays():
  def it_returns_true_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_days_ago = now_utc - timedelta(days=2)
    assert older_than_ndays(two_days_ago, 1)
  def it_returns_false_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_days_ago = now_utc - timedelta(days=2)
    assert not older_than_ndays(two_days_ago, 3)
