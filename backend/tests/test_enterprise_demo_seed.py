from sqlalchemy import func, select

from app.database import SessionLocal
from app.models.asset import Asset, Software
from app.services.enterprise_demo_seed import build_enterprise_demo_assets, seed_enterprise_demo


def test_enterprise_demo_dataset_is_realistic_and_unique():
    dataset = build_enterprise_demo_assets()
    hostnames = [str(item.asset["hostname"]) for item in dataset]

    assert len(dataset) == 112
    assert len(set(hostnames)) == 112
    assert sum(len(item.software) for item in dataset) == 406
    assert {item.asset["asset_type"] for item in dataset} == {
        "server", "workstation", "network_device", "application", "cloud_resource"
    }
    assert all("Donnée synthétique" in str(item.asset["description"]) for item in dataset)


def test_enterprise_demo_seed_is_idempotent(client):
    with SessionLocal() as db:
        first = seed_enterprise_demo(db)
        second = seed_enterprise_demo(db)
        asset_count = db.scalar(select(func.count(Asset.id)))
        software_count = db.scalar(select(func.count(Software.id)))

    assert first == {"assets_created": 112, "software_created": 406}
    assert second == {"assets_created": 0, "software_created": 0}
    assert asset_count == 112
    assert software_count == 406
