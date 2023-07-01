import pytz

from datetime import datetime, timedelta

from lib.date import (
  date1_older,
  now_utc,
  older_than_ndays,
  older_than_nhours
)

def describe_date1_older():
  def it_returns_true_when_date1_older():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    date1 = now_utc - timedelta(days=1)
    date2 = now_utc
    assert date1_older(date1, date2)
  def it_returns_false_when_date1_younger():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    date1 = now_utc
    date2 = now_utc - timedelta(days=1)
    assert not date1_older(date1, date2)
  def it_returns_false_when_both_are_the_same():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    date1 = now_utc
    date2 = now_utc
    assert not date1_older(date1, date2)

def describe_now_utc():
  def it_returns_object_with_utc_timezone():
    date1 = datetime.utcnow()
    date1_utc = date1.replace(tzinfo=pytz.utc)
    # comparison works only when both sides are utc
    assert date1_utc < now_utc()

def describe_older_than_ndays():
  def it_returns_true_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_days_ago = now_utc - timedelta(days=2)
    assert older_than_ndays(str(two_days_ago), 1)
  def it_returns_false_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_days_ago = now_utc - timedelta(days=2)
    assert not older_than_ndays(str(two_days_ago), 3)

def describe_older_than_nhours():
  def it_returns_true_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_hours_ago = now_utc - timedelta(hours=2)
    assert older_than_nhours(str(two_hours_ago), 1)
  def it_returns_false_correctly():
    now = datetime.utcnow()
    now_utc = now.replace(tzinfo=pytz.utc)
    two_hours_ago = now_utc - timedelta(hours=2)
    assert not older_than_nhours(str(two_hours_ago), 3)
