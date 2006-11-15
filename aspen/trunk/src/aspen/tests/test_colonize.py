from aspen import colon


def test_basic():
    from aspen.handlers import HTTP404 as expected
    actual = colon.colonize('aspen.handlers:HTTP404', 'filename', 0)
    assert expected is actual

def test_must_have_colon():
    try:
        colon.colonize('foo.bar', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeBadColonsError)

def test_but_only_one_colon():
    try:
        colon.colonize('foo.bar:baz:buz', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeBadColonsError)

def test_module_name():
    try:
        colon.colonize('foo.bar; import os; os.remove();:', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeBadModuleError)

def test_module_not_there():
    try:
        colon.colonize('foo.bar:baz', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeImportError)

def test_object_name():
    try:
        colon.colonize('string:baz; import os; os.remove();', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeBadObjectError)

def test_object_not_there():
    try:
        colon.colonize('string:foo', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeAttributeError)

def test_nested_object_not_there():
    from string import digits as expected
    actual = colon.colonize('string:digits', 'filename', 0)
    assert expected is actual
    try:
        colon.colonize('string:digits.duggems', 'filename', 0)
    except colon.ColonizeError, err:
        assert isinstance(err, colon.ColonizeAttributeError)
