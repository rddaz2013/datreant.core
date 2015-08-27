"""Tests for filesystem elements, including Foxhound and related objects.

"""

import datreant as dtr
import pytest
import os
import py.path


class TestFoxhound:
    """Test Foxhound functionality"""

    @pytest.fixture
    def treant(self, tmpdir):
        with tmpdir.as_cwd():
            t = dtr.treants.Container('testtreant')
        return t

    @pytest.fixture
    def group(self, tmpdir):
        with tmpdir.as_cwd():
            g = dtr.Group('testgroup')
        return g
