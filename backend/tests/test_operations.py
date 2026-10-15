import sqlite3

from scripts.backup_database import backup_sqlite_database


def test_readiness_and_prometheus_metrics(client):
    readiness = client.get("/health/ready")
    metrics = client.get("/metrics")

    assert readiness.status_code == 200
    assert readiness.json()["checks"]["database"] == "ok"
    assert metrics.status_code == 200
    assert "sentinel_http_requests_total" in metrics.text
    assert 'path="/health/ready"' in metrics.text


def test_sqlite_backup_is_consistent(tmp_path):
    source = tmp_path / "source.db"
    destination = tmp_path / "backups"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, value TEXT)")
        connection.execute("INSERT INTO events(value) VALUES ('sentinel')")
        connection.commit()

    created = backup_sqlite_database(source, destination, retention=2)

    assert created.exists()
    with sqlite3.connect(created) as connection:
        assert connection.execute("SELECT value FROM events").fetchone() == ("sentinel",)
