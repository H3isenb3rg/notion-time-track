from io import StringIO
import pytest
import datetime
from time_tracker.time_tracker import TimeTracker
from time_tracker import notionapi
from time_tracker.config import ConfigClass


@pytest.fixture
def mock_get_sentric_buckets(monkeypatch: pytest.MonkeyPatch):
    """Avoids request to get buckets"""

    def mock_get(*args, **kwargs):
        return [notionapi.Bucket("bkt0", "Casper", "Sentric"),
                notionapi.Bucket("bkt1", "Data-Processing", "Sentric"),
                notionapi.Bucket("bkt2", "Other Bucket", "Other")]

    monkeypatch.setattr(notionapi.NotionAPI, "_get_sentric_buckets", mock_get)


@pytest.fixture
def patch_datetime_date(monkeypatch):

    class mydate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2022, 12, 8)

    monkeypatch.setattr(datetime, 'date', mydate)
    #  To use -> datetime.date.today()


@pytest.fixture
def configuration():
    return ConfigClass(10, "", "https://localhost", "", "https://localhost", "https://localhost")


@pytest.fixture
def time_tracker(configuration, mock_get_sentric_buckets):
    return TimeTracker(configuration)


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
def test_get_times_function(test_input, expected, monkeypatch, patch_datetime_date, time_tracker: TimeTracker):
    input_times = StringIO(test_input + '\n')
    monkeypatch.setattr('sys.stdin', input_times)
    times = time_tracker.get_times()
    assert times[0] == expected[0]
    assert times[1] == expected[1]


@pytest.mark.parametrize("test_input,expected", [
    ((10, 10), "Remaining hours -> 0\n"),
    ((5, 8), "Hours pending from last week -> 2\nRemaining hours -> 7\n"),
    ((0, 12), "Hours overflowed from last week -> 2\nRemaining hours -> 8\n"),
    ((10, 0), "Hours pending from last week -> 10\nRemaining hours -> 10\n"),
])
def test_get_diff(test_input, expected, time_tracker: TimeTracker, capsys: pytest.CaptureFixture):
    time_tracker.print_diff(test_input[1], test_input[0])
    capture = capsys.readouterr()
    assert capture.out == expected
