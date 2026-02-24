"""CLI entry point for the Credit Card Fraud Detector."""

from __future__ import annotations

import sys

from fraud_detector.fraud_detection import detect_fraud, read_transactions_from_file


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m fraud_detector.app <transactions_file> <price_threshold>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        threshold = float(sys.argv[2])
    except ValueError:
        print("Price threshold format is incorrect.", file=sys.stderr)
        sys.exit(1)

    try:
        transactions = read_transactions_from_file(file_path)
    except FileNotFoundError:
        print("File path is invalid.", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Date or amount format is incorrect.", file=sys.stderr)
        sys.exit(1)

    fraud_list = detect_fraud(transactions, threshold)

    if not fraud_list:
        print("No fraud transaction found.")
    else:
        for fraud in fraud_list:
            print(fraud.hash_card_number)


if __name__ == "__main__":
    main()
