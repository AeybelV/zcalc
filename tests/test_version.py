import zcalc


def test_version():
    """Checks if __version__ attribute exists"""
    assert hasattr(zcalc, "__version__")
    assert isinstance(zcalc.__version__, str)
