import os
import pytest
from func_get_tallest_superhero import get_tallest_superhero
import logging

logger = logging.getLogger(__name__)


def test_get_tallest_superhero():
    logger.debug("Hi, I'm hero")
    res = get_tallest_superhero('male', True)
    assert res