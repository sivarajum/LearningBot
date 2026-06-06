"""Shared fixtures for integration tests.

Creates and tears down real BigQuery datasets for each test function.
Requires valid GCP credentials (Application Default Credentials or
GOOGLE_APPLICATION_CREDENTIALS env var) and the --bq-project flag.

Run integration tests with:
    pytest tests/integration/ -v --bq-project ai-trading-prod -m integration
"""

import uuid

import pytest
from google.cloud import bigquery


def pytest_addoption(parser):
    parser.addoption(
        "--bq-project",
        default="ai-trading-prod",
        help="GCP project ID for integration tests",
    )
    parser.addoption(
        "--bq-location",
        default="US",
        help="BigQuery dataset location (default: US)",
    )


@pytest.fixture(scope="session")
def bq_project(request):
    """Return the GCP project ID from the --bq-project CLI option."""
    return request.config.getoption("--bq-project")


@pytest.fixture(scope="session")
def bq_location(request):
    """Return the BQ dataset location from the --bq-location CLI option."""
    return request.config.getoption("--bq-location")


@pytest.fixture(scope="session")
def bq_client(bq_project):
    """Return a session-scoped BigQuery client.

    The client is shared across all integration tests in the session to avoid
    the overhead of OAuth token refresh on each test.
    """
    return bigquery.Client(project=bq_project)


@pytest.fixture(scope="function")
def bq_test_dataset(bq_client, bq_project, bq_location):
    """Create a fresh BQ dataset for each test function, then tear it down.

    Each test gets a unique dataset name of the form poc10_test_{8hex chars}
    so that tests can run in parallel without collision.

    Yields a dict with keys:
        project  — GCP project ID
        dataset  — dataset ID (short name)
        full_id  — fully qualified ID: "{project}.{dataset}"

    Teardown deletes the dataset and all its contents unconditionally.
    """
    dataset_id = f"poc10_test_{uuid.uuid4().hex[:8]}"
    full_id = f"{bq_project}.{dataset_id}"
    dataset = bigquery.Dataset(full_id)
    dataset.location = bq_location
    bq_client.create_dataset(dataset)

    yield {
        "project": bq_project,
        "dataset": dataset_id,
        "full_id": full_id,
    }

    bq_client.delete_dataset(full_id, delete_contents=True, not_found_ok=True)


@pytest.fixture(scope="function")
def trades_table(bq_client, bq_test_dataset) -> bigquery.Table:
    """Create a standard 'trades' table in the test dataset.

    Schema matches the baseline defined in CHANGELOG.md:
        trade_id    STRING NOT NULL
        symbol      STRING NOT NULL
        amount      FLOAT64 NOT NULL
        ccy         STRING NOT NULL
        traded_at   TIMESTAMP NOT NULL
        _load_id    STRING NOT NULL

    Returns the created Table object.
    """
    project = bq_test_dataset["project"]
    dataset = bq_test_dataset["dataset"]
    table_id = f"{project}.{dataset}.trades"

    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("amount", "FLOAT64", mode="REQUIRED"),
        bigquery.SchemaField("ccy", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("traded_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("_load_id", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    return bq_client.create_table(table)
