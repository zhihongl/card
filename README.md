# Credit Card Fraud Detector

This repository also contains **Legal RAG (WI-000001)** for Victoria Supreme Court judgments: see `legal_rag/`, `tests/`, `infra/docker-compose.yml`, and `AllocationsManagement.Content/specs/active/WI-000001/runbook.md`.

This project is build in maven so just use normal maven command to build and test

### Prerequisites

Java

Maven

Python 3 and `pip` (optional today; used by Cursor/cloud setup and future Legal RAG tooling)

### Cursor / cloud environment

The hosted environment may run `pip install -r requirements.txt`. This repo includes a root `requirements.txt` so that step does not fail.

For a full sync (Python deps + Maven tests), set the **update script** to:

```bash
bash scripts/cloud-setup.sh
```

To **show project progress** in a browser (e.g. for screen recording instead of an empty desktop), run:

```bash
bash scripts/open-progress-dashboard.sh
```

## Get started

This application takes two input values: 
1. transactions file path
2. price threshold

## What the application support

Currently this application only support limited amount of transaction like definate below 2^30 transaction. 
Because it will cause java.lang.OutOfMemoryError: Java heap space due to the way of implementation. 
And the last test case in AppTest file is regarding this. 

### Improvements

1. redesign the system to support 2^30 transactions, eg: involve Threads
2. use distributed system to handle this maybe try hadoop to handle big data
