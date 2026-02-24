"""Unit tests for the Credit Card Fraud Detector — mirrors all original Java test cases."""

from __future__ import annotations

import os
from datetime import date, datetime

import pytest

from fraud_detector.fraud_detection import (
    detect_fraud,
    parse_datetime,
    parse_single_transaction,
    read_transactions_from_file,
)
from fraud_detector.models import CreditCardTransaction

RESOURCES = os.path.join(os.path.dirname(__file__), "resources")

CARD_NUMBER = "10d7ce2f43e35fa57d1bbf8b1e2"
TRANSACTION_DATE = "2020-05-14T13:15:54"
TRANSACTION_DAY = "2020-05-14"
TRANSACTION_AMOUNT = 10.00
FRAUD_THRESHOLD = 10.00
NOT_FRAUD_THRESHOLD = 15.00


def test_datetime_format():
    dt = parse_datetime(TRANSACTION_DATE)
    assert isinstance(dt, datetime)
    assert dt.isoformat() == TRANSACTION_DATE


def test_date_format():
    dt = parse_datetime(TRANSACTION_DATE)
    d = dt.date()
    assert isinstance(d, date)
    assert d.isoformat() == TRANSACTION_DAY


def test_simple_transaction_with_fraud():
    txn = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    fraud_list = detect_fraud([txn], FRAUD_THRESHOLD)
    assert len(fraud_list) == 1


def test_simple_transaction_without_fraud():
    txn = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    fraud_list = detect_fraud([txn], NOT_FRAUD_THRESHOLD)
    assert len(fraud_list) == 0


def test_two_transactions_same_card_with_fraud():
    txn1 = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    txn2 = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    fraud_list = detect_fraud([txn1, txn2], NOT_FRAUD_THRESHOLD)
    assert len(fraud_list) == 1


def test_two_transactions_different_cards_with_fraud():
    txn1 = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    txn2 = CreditCardTransaction("1234562f43e35fa57d1bb123456", parse_datetime("2020-05-14T13:01:21"), 101)
    fraud_list = detect_fraud([txn1, txn2], FRAUD_THRESHOLD)
    assert len(fraud_list) == 2


def test_two_transactions_fraud_display_names():
    txn1 = CreditCardTransaction(CARD_NUMBER, parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    txn2 = CreditCardTransaction("1234562f43e35fa57d1bb123456", parse_datetime(TRANSACTION_DATE), TRANSACTION_AMOUNT)
    fraud_list = detect_fraud([txn1, txn2], FRAUD_THRESHOLD)
    card_numbers = {f.hash_card_number for f in fraud_list}
    assert CARD_NUMBER in card_numbers
    assert "1234562f43e35fa57d1bb123456" in card_numbers


def test_parse_single_transaction_string():
    line = f"{CARD_NUMBER}, {TRANSACTION_DATE}, {TRANSACTION_AMOUNT:.2f}"
    txn = parse_single_transaction(line)
    assert txn.hash_card_number == CARD_NUMBER
    assert txn.transaction_date.isoformat() == TRANSACTION_DATE
    assert txn.transaction_amount == float(f"{TRANSACTION_AMOUNT:.2f}")


def test_parse_file_with_two_transactions():
    transactions = read_transactions_from_file(os.path.join(RESOURCES, "two_transactions"))
    assert len(transactions) == 2


def test_parse_file_with_malformatted_date():
    with pytest.raises(ValueError):
        read_transactions_from_file(os.path.join(RESOURCES, "date_malformated"))


def test_parse_file_with_wrong_path():
    with pytest.raises(FileNotFoundError):
        read_transactions_from_file("wrong_file_path")


def test_fraud_detection_integration():
    transactions = read_transactions_from_file(os.path.join(RESOURCES, "transaction_file"))
    fraud_list = detect_fraud(transactions, 10)
    assert len(fraud_list) == 3


def test_big_detection():
    transactions = read_transactions_from_file(os.path.join(RESOURCES, "transaction_file_big"))
    fraud_list = detect_fraud(transactions, 10)
    assert len(fraud_list) == 0
