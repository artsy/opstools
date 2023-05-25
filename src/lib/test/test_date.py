import pytz

from datetime import datetime, timedelta

from lib.date import (
  date_nhours_ago,
  older_than_ndays
)

def describe_date_nhours_ago():
  def describe_nhours_2():
    def it_returns_date_older_than_1hour_ago():
      now = datetime.utcnow()
      now_utc = now.replace(tzinfo=pytz.utc)
      nhours = 2
      one_hour_ago = now_utc - timedelta(hours=1)
      assert date_nhours_ago(2) < one_hour_ago
    def it_returns_date_more_recent_than_3hours_ago():
      now = datetime.utcnow()
      now_utc = now.replace(tzinfo=pytz.utc)
      nhours = 2
      three_hours_ago = now_utc - timedelta(hours=3)
      assert date_nhours_ago(2) > three_hours_ago

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
