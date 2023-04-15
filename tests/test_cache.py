import os
import shutil

import pytest

import joblib


@pytest.fixture
def refresh_environment():
    """Refresh the test environment.

    This deletes any reference to `outlines` in the modules dictionary and unsets the
    `OUTLINES_CACHE_DIR` environment variable if set. This is necessary because we
    are using a module variable to hold the cache.

    """
    import sys

    for key in list(sys.modules.keys()):
        if "outlines" in key:
            del sys.modules[key]

    try:
        del os.environ["OUTLINES_CACHE_DIR"]
    except KeyError:
        pass


@pytest.fixture
def test_cache(refresh_environment):
    """Initialize a temporary cache and delete it after the test has run."""
    os.environ["OUTLINES_CACHE_DIR"] = "~/.cache/outlines_tests"
    import outlines

    memory = outlines.cache.get()
    assert memory.location == "~/.cache/outlines_tests"

    yield memory

    memory.clear()
    home_dir = os.path.expanduser("~")
    shutil.rmtree(f"{home_dir}/.cache/outlines_tests")


def test_get_cache(test_cache):
    import outlines

    memory = outlines.cache.get()
    assert isinstance(memory, joblib.Memory)

    # If the cache is enable then the size
    # of `store` should not increase the
    # second time `f` is called.
    store = list()

    @memory.cache
    def f(x):
        store.append(1)
        return x

    f(1)
    store_size = len(store)

    f(1)
    assert len(store) == store_size

    f(2)
    assert len(store) == store_size + 1


def test_disable_cache(test_cache):
    """Make sure that we can disable the cache."""
    import outlines

    outlines.cache.disable()
    memory = outlines.cache.get()

    # If the cache is disabled then the size
    # of `store` should increase every time
    # `f` is called.
    store = list()

    @memory.cache
    def f(x):
        store.append(1)
        return x

    f(1)
    store_size = len(store)
    f(1)
    assert len(store) == store_size + 1


def test_clear_cache(test_cache):
    """Make sure that we can clear the cache."""

    store = list()

    @test_cache.cache
    def f(x):
        store.append(1)
        return x

    # The size of `store` does not increase since
    # `f` is cached after the first run.
    f(1)
    store_size = len(store)
    f(1)
    assert len(store) == store_size

    # The size of `store` should increase if we call `f`
    # after clearing the cache.
    test_cache.clear()
    f(1)
    assert len(store) == store_size + 1
