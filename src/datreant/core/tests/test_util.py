import os
from unittest.mock import patch

import pytest

import datreant.core as dtr


class TestMakedirs(object):
    def test_makedirs(self, tmpdir):
        with tmpdir.as_cwd():
            dtr.util.makedirs('this/should/exist')
            assert os.path.exists('this/should/exist')
            assert os.path.isdir('this/should/exist')

    def test_makedirs_exists(self, tmpdir):
        # try and make a dir twice
        with tmpdir.as_cwd():
            os.mkdir('this/')
            dtr.util.makedirs('this/')
            assert os.path.exists('this/')
            assert os.path.isdir('this/')

    def test_makedirs_error_catch(self, tmpdir):
        # mock a disk full error
        # and make sure it gets propagated through properly
        with tmpdir.as_cwd():
            with patch('os.makedirs') as mp:
                mp.side_effect = OSError(os.errno.ENOSPC, 'Mock - disk full')
                # check the specific error code
                # ie check we don't mangle it enroute
                with pytest.raises(OSError) as error:
                    dtr.util.makedirs('this/should/fail')
                    assert error.errno == os.errno.ENOSPC
