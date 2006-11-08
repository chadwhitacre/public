import string


INITIAL = '_' + string.letters
INNER = INITIAL + string.digits
def is_valid_identifier(s):
    """Given a string of length > 0, return a boolean.

        >>> is_valid_identifier('.svn')
        False
        >>> is_valid_identifier('svn')
        True
        >>> is_valid_identifier('_svn')
        True
        >>> is_valid_identifier('__svn')
        True
        >>> is_valid_identifier('123')
        False
        >>> is_valid_identifier('r123')
        True

    """
    try:
        assert s[0] in INITIAL
        assert False not in [x in INNER for x in s]
        return True
    except AssertionError:
        return False


if __name__ == '__main__':
    import doctest
    doctest.testmod()
