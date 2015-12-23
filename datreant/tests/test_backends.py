"""Tests for TreantFiles.

Some are tests to compare performance across backends.

"""

import pandas as pd
import numpy as np
import pytest
import os
import shutil
import py

from pytest import mark

import datreant as dtr
from datreant.backends.pytables import TreantFileHDF5
from datreant.backends.pyjson import TreantFileJSON
from datreant.backends.pyyaml import TreantFileYAML


def add_tags(treantfile, tags):
    treantfile.add_tags(*tags)


def add_tags_individually(treantfile, tags):
    for tag in tags:
        treantfile.add_tags(tag)


class TreantFileMixin:
    """Test generic TreantFile features"""

    def test_add_tags(self, treantfile):
        treantfile.add_tags('marklar')
        assert 'marklar' in treantfile.get_tags()

        treantfile.add_tags('lark', 'bark')
        assert 'marklar' in treantfile.get_tags()
        assert 'lark' in treantfile.get_tags()
        assert 'bark' in treantfile.get_tags()

    @mark.bench('add_tags')
    def test_add_single_tag(self, treantfile):
        tags = ['yes this {}'.format(i) for i in range(100)]
        treantfile.add_tags(*tags)

        add_tags(treantfile, 'a single tag')

    @mark.bench('add_tags')
    def test_add_many_tags_at_once(self, treantfile):
        tags = ['yes this {}'.format(i) for i in range(100)]
        add_tags(treantfile, tags)

    @mark.bench('add_tags_individually')
    def test_add_many_tags_individually(self, treantfile):
        tags = ['yes this {}'.format(i) for i in range(10)]
        add_tags_individually(treantfile, tags)


class TestTreantFileHDF5(TreantFileMixin):

    @pytest.fixture
    def treantfile(self, tmpdir):
        with tmpdir.as_cwd():
            c = TreantFileHDF5('testfile.h5')
        return c


class TestTreantFileJSON(TreantFileMixin):

    @pytest.fixture
    def treantfile(self, tmpdir):
        with tmpdir.as_cwd():
            c = TreantFileJSON('testfile.json')
        return c


class TestTreantFileYAML(TreantFileMixin):

    @pytest.fixture
    def treantfile(self, tmpdir):
        with tmpdir.as_cwd():
            c = TreantFileYAML('testfile.yaml')
        return c