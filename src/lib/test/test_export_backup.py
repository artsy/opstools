from lib.export_backup import write_file

def describe_write_file():
  def it_creates_file_with_default_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data')
    assert os.stat(file_path).st_mode == int(0o100600)
    with open(file_path, 'r') as f:
      assert f.readline().strip() == 'foo data'
  def it_creates_file_with_custom_permissions(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data', mode=0o755)
    assert os.stat(file_path).st_mode == int(0o100755)
  def it_writes_heading(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data', heading='foo heading\n')
    with open(file_path, 'r') as f:
      assert f.readline().strip() == 'foo heading'
  def it_balks_when_file_exists(tmp_path):
    file_path = os.path.join(tmp_path, 'foo.txt')
    write_file(file_path, 'foo data')
    write_file(file_path, 'foo data')
    with pytest.raises(FileExistsError):
      write_file(file_path, 'foo data', exist_ok=False)
