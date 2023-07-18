from lib.k8s_configmap_jwt_scan import is_jwt

def describe_is_jwt():
  def it_returns_false_if_not_jwt():
    assert is_jwt('foo') == False
  def it_returns_false_if_jwt_but_invalid():
    assert is_jwt('foo.bar.baz') == False
  def it_returns_true_if_jwt():
    assert is_jwt('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcnRzeSI6Im9wc3Rvb2xzIn0.FAKE') == True # pragma: allowlist secret
