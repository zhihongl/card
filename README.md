# Credit Card Fraud Detector

A CLI tool that reads credit card transactions from a file and flags cards whose total spending on any single day meets or exceeds a configurable price threshold.

## Prerequisites

- Python 3.9+

## Install dependencies

```bash
pip install -r requirements.txt
```

## Get started

```bash
python -m fraud_detector <transactions_file> <price_threshold>
```

### Example

```bash
# Detect cards with daily spend >= $10
python -m fraud_detector transactions_file 10.00

# Detect cards with daily spend >= $50
python -m fraud_detector transactions_file 50.00
```

### Input format

Each line in the transactions file:

```
<hashed_card_number>, <ISO-8601 datetime>, <amount>
```

Example:
```
10d7ce2f43e35fa57d1bbf8b1e2, 2020-05-11T14:15:54, 10.00
```

## Development

```bash
# Run tests
pytest

# Lint
ruff check .

# Format check
ruff format --check .
```

## Limitations

Currently loads all transactions into memory. For datasets exceeding available RAM, a streaming or distributed approach (e.g. chunked processing, Spark) would be needed.
