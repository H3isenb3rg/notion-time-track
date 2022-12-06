# File to create fixtures for tests
import datetime
import pytest


@pytest.fixture
def patch_datetime_date(monkeypatch):

    class mydate(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2022, 12, 8)

    monkeypatch.setattr(datetime, 'date', mydate)
