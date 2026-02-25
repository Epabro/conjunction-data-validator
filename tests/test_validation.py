from validator.io import load_message
from validator.rules import load_rules
from validator.validation import validate_message


def test_good_message_ok():
    msg = load_message("samples/good.json")
    rules = load_rules("rules.yaml")
    report = validate_message(msg, rules)
    assert report.ok is True
    assert report.summary["fail"] == 0


def test_bad_time_fails():
    msg = load_message("samples/bad_time.json")
    rules = load_rules("rules.yaml")
    report = validate_message(msg, rules)
    assert report.ok is False
    assert report.summary["fail"] >= 1

def test_bad_cov_fails():
    msg = load_message("samples/bad_cov.json")
    rules = load_rules("rules.yaml")
    report = validate_message(msg, rules)
    assert report.ok is False
    assert report.summary["fail"] >= 1
