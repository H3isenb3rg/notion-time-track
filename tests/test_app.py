from io import StringIO
import pytest
from time_tracker.app import get_times, get_diff
import datetime


@pytest.fixture
def patch_datetime_date(monkeypatch):

    class mydate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2022, 12, 8)

    monkeypatch.setattr(datetime, 'date', mydate)
    #  To use -> datetime.date.today()


@pytest.mark.parametrize("test_input,expected", [
    ("14 15", ("2022-12-08T14:00:00", "2022-12-08T15:00:00")),
    ("9 12", ("2022-12-08T09:00:00", "2022-12-08T12:00:00")),
    ("20 23", ("2022-12-08T20:00:00", "2022-12-08T23:00:00")),
    ("5 6", ("2022-12-08T05:00:00", "2022-12-08T06:00:00")),
    ("14:30 15:15", ("2022-12-08T14:30:00", "2022-12-08T15:15:00")),
    ("9:45 12.30", ("2022-12-08T09:45:00", "2022-12-08T12:30:00")),
    ("20.30 23", ("2022-12-08T20:30:00", "2022-12-08T23:00:00")),
    ("5 6.30", ("2022-12-08T05:00:00", "2022-12-08T06:30:00"))
])
def test_times(test_input, expected, monkeypatch, patch_datetime_date):
    input_times = StringIO(test_input + '\n')
    monkeypatch.setattr('sys.stdin', input_times)
    times = get_times()
    assert times[0] == expected[0]
    assert times[1] == expected[1]


@pytest.mark.parametrize("test_input,expected", [
    ((10, 10), 0),
    ((10, 8), 2),
    ((10, 12), 0),
    ((10, 0), 10),
])
def test_get_diff(test_input, expected):
    result = get_diff(test_input[0], test_input[1])
    assert result == expected
