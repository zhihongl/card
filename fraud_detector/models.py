from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreditCardTransaction:
    hash_card_number: str
    transaction_date: datetime
    transaction_amount: float


@dataclass(frozen=True)
class FraudTransaction:
    hash_card_number: str
