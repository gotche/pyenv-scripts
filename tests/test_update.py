import tempfile
from http import HTTPStatus
from pathlib import Path
from unittest import mock

import pytest

from update import (
    get_build_file,
    get_previous_version,
    get_target_details,
    replace_target_details,
)


class MockResponse:
    def __init__(self, content, status_code=HTTPStatus.OK, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers

    def raise_for_status(self):
        pass


@pytest.mark.parametrize("version,previous", [("3.8.1", "3.8.0"), ("3.7.6", "3.7.5")])
def test_previous_version(version, previous):
    assert previous == get_previous_version(version)


def test_previous_version_exception():
    with pytest.raises(NotImplementedError):
        assert get_previous_version("3.8.0")


def test_get_file():
    version = "3.8.1"
    filepath = get_build_file(version)
    assert version in str(filepath)
    assert isinstance(filepath, Path)


def test_convert_into_template():
    version_file = Path("./tests/examplefile")
    previous_version = "3.8.1"
    target = "3.8.2"
    with open(version_file) as prev, tempfile.TemporaryFile(mode="r+") as new_file:
        replace_target_details(
            prev, new_file, previous_version, target, {"tar.xz": "1", "tgz": "2"}
        )

        new_file.seek(0)
        for line in new_file.readlines():
            if target in line:
                break
        else:
            assert False, "New version no found in the new file"


def test_get_target_details():
    version = "3.8.1"
    mocked_response = MockResponse(content=b"asdf", status_code=HTTPStatus.OK)
    with mock.patch("requests.get", return_value=mocked_response):
        details = get_target_details(version)

    assert "tar.xz" in details
    assert len(details["tar.xz"]) == 64
