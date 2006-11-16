def assert_raises(Exc, call, *arg, **kw):
    exc = None
    try:
        call(*arg, **kw)
    except Exception, exc:
        pass
    assert isinstance(exc, Exc)
    return exc
