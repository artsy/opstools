from lib.util import (
  is_artsy_s3_bucket
)

def describe_is_artsy_s3_bucket():
  def it_returns_true_if_name_starts_with_artsy():
    assert is_artsy_s3_bucket('artsy-foo-bucket')
  def it_returns_false_if_name_does_not_start_with_artsy():
    assert not is_artsy_s3_bucket('foo-bucket')
  def it_returns_false_if_name_is_empty_string():
    assert not is_artsy_s3_bucket('')
