from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import List

from fraud_detector.models import CreditCardTransaction, FraudTransaction


def parse_datetime(date_string: str) -> datetime:
    return datetime.fromisoformat(date_string)


def parse_single_transaction(line: str) -> CreditCardTransaction:
    parts = line.replace(" ", "").split(",")
    card_number = parts[0]
    transaction_date = parse_datetime(parts[1])
    amount = float(parts[2])
    return CreditCardTransaction(card_number, transaction_date, amount)


def read_transactions_from_file(file_path: str) -> List[CreditCardTransaction]:
    with open(file_path) as f:
        return [parse_single_transaction(line) for line in f if line.strip()]


def detect_fraud(
    transactions: List[CreditCardTransaction],
    threshold: float,
) -> List[FraudTransaction]:
    daily_totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for txn in transactions:
        day_key = txn.transaction_date.date().isoformat()
        daily_totals[txn.hash_card_number][day_key] += txn.transaction_amount

    fraud_list: List[FraudTransaction] = []
    for card_number, day_amounts in daily_totals.items():
        if any(total >= threshold for total in day_amounts.values()):
            fraud_list.append(FraudTransaction(card_number))

    return fraud_list
