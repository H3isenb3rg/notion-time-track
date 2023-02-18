import pytest
from time_tracker.notionapi import Bucket


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (("bkt1", "Bucket 1", "Buckets"), ("bkt1", "Bucket 1", "Buckets")),
        (("abc", "ABC", "Letters"), ("abc", "ABC", "Letters")),
        (("1", "casper", "Sentric"), ("1", "casper", "Sentric")),
    ],
)
def test_bucket_creation(test_input, expected):
    bucket = Bucket(test_input[0], test_input[1], test_input[2])
    assert test_input[0] == bucket.id
    assert test_input[1] == bucket.name
    assert test_input[2] == bucket.area


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((Bucket("bkt1", "Bucket 1", "Buckets"), Bucket("bkt1", "Bucket 1", "Buckets")), True),
        ((Bucket("abc", "ABC", "Letters"), Bucket("abc", "ABC", "Letters")), True),
        ((Bucket("1", "casper", "Sentric"), Bucket("1", "casper", "Sentric")), True),
        ((Bucket("abc", "ABC", "Letters"), Bucket("1", "casper", "Sentric")), False),
        ((Bucket("1", "casper", "Sentric"), Bucket("bkt1", "Bucket 1", "Buckets")), False),
        ((Bucket("abc", "ABC", "Letters"), "ABC"), True),
        ((Bucket("abc", "ABC", "Letters"), "prova"), False),
    ],
)
def test_bucket_compare(test_input, expected: bool):
    assert (test_input[0] == test_input[1]) is expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ((Bucket("bkt1", "Bucket 1", "Buckets"), 123), TypeError),
        ((Bucket("abc", "ABC", "Letters"), 150.5), TypeError),
        ((Bucket("1", "casper", "Sentric"), None), TypeError),
    ],
)
def test_bucket_compare_exceptions(test_input, expected):
    with pytest.raises(expected):
        _ = test_input[0] == test_input[1]
