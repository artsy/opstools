from lib.s3_interface import S3Interface

from lib.test.fixtures.s3_interface import (
  mock_s3_client, # indirect usage
  s3_interface_obj
)

def describe_s3_interface():

  def describe_instantiation():
    def it_instantiates(s3_interface_obj, mock_s3_client):
      assert s3_interface_obj._s3 is mock_s3_client

  def describe_delete_object():
    def it_calls_s3_client_delete_object(s3_interface_obj, mocker):
      spy = mocker.spy(s3_interface_obj._s3, 'delete_object')
      s3_interface_obj.delete_object('foobucket', 'fookey')
      spy.assert_has_calls([mocker.call(Bucket='foobucket', Key='fookey')])

  def describe_list_objects():
    def it_returns_objects(s3_interface_obj):
      assert s3_interface_obj.list_objects('foobucket', 'fooprefix') == 'objects'

  def describe_put_file():
    def it_calls_s3_client_upload_fileobj(s3_interface_obj, mocker):
      # how to mock file open in binary read mode?
      pass
