from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset, Software


@dataclass(frozen=True)
class DemoAsset:
    asset: dict[str, object]
    software: tuple[dict[str, str | None], ...]


SITES = ("siege", "casablanca", "rabat", "tanger")
DEPARTMENTS = ("finance", "commercial", "rh", "operations", "support")

WORKSTATION_SOFTWARE = (
    {
        "name": "Google Chrome",
        "vendor": "Google",
        "version": "129.0.6668.89",
        "cpe": "cpe:2.3:a:google:chrome:129.0.6668.89:*:*:*:*:*:*:*",
        "purl": "pkg:generic/google/chrome@129.0.6668.89",
    },
    {
        "name": "Mozilla Firefox",
        "vendor": "Mozilla",
        "version": "131.0",
        "cpe": "cpe:2.3:a:mozilla:firefox:131.0:*:*:*:*:*:*:*",
        "purl": "pkg:generic/mozilla/firefox@131.0",
    },
    {
        "name": "7-Zip",
        "vendor": "7-Zip",
        "version": "23.01",
        "cpe": "cpe:2.3:a:7-zip:7-zip:23.01:*:*:*:*:*:*:*",
        "purl": "pkg:generic/7-zip/7-zip@23.01",
    },
    {
        "name": "VLC media player",
        "vendor": "VideoLAN",
        "version": "3.0.21",
        "cpe": "cpe:2.3:a:videolan:vlc_media_player:3.0.21:*:*:*:*:*:*:*",
        "purl": "pkg:generic/videolan/vlc@3.0.21",
    },
)

SERVER_SOFTWARE = (
    {
        "name": "OpenSSH",
        "vendor": "OpenBSD",
        "version": "9.2",
        "cpe": "cpe:2.3:a:openbsd:openssh:9.2:*:*:*:*:*:*:*",
        "purl": "pkg:generic/openbsd/openssh@9.2",
    },
    {
        "name": "Nginx",
        "vendor": "Nginx",
        "version": "1.24.0",
        "cpe": "cpe:2.3:a:nginx:nginx:1.24.0:*:*:*:*:*:*:*",
        "purl": "pkg:generic/nginx/nginx@1.24.0",
    },
    {
        "name": "PostgreSQL",
        "vendor": "PostgreSQL",
        "version": "15.6",
        "cpe": "cpe:2.3:a:postgresql:postgresql:15.6:*:*:*:*:*:*:*",
        "purl": "pkg:generic/postgresql/postgresql@15.6",
    },
    {
        "name": "Docker Engine",
        "vendor": "Docker",
        "version": "25.0.3",
        "cpe": "cpe:2.3:a:docker:docker:25.0.3:*:*:*:*:*:*:*",
        "purl": "pkg:generic/docker/docker@25.0.3",
    },
)

NETWORK_SOFTWARE = (
    {
        "name": "OpenSSH",
        "vendor": "OpenBSD",
        "version": "8.9",
        "cpe": "cpe:2.3:a:openbsd:openssh:8.9:*:*:*:*:*:*:*",
        "purl": "pkg:generic/openbsd/openssh@8.9",
    },
)

APPLICATION_SOFTWARE = (
    {
        "name": "Apache Tomcat",
        "vendor": "Apache",
        "version": "10.1.30",
        "cpe": "cpe:2.3:a:apache:tomcat:10.1.30:*:*:*:*:*:*:*",
        "purl": "pkg:maven/org.apache.tomcat/tomcat@10.1.30",
    },
    {
        "name": "Node.js",
        "vendor": "OpenJS Foundation",
        "version": "20.17.0",
        "cpe": "cpe:2.3:a:nodejs:node.js:20.17.0:*:*:*:*:*:*:*",
        "purl": "pkg:generic/nodejs/node@20.17.0",
    },
    SERVER_SOFTWARE[1],
)

CLOUD_SOFTWARE = (
    {
        "name": "Kubernetes",
        "vendor": "Kubernetes",
        "version": "1.30.4",
        "cpe": "cpe:2.3:a:kubernetes:kubernetes:1.30.4:*:*:*:*:*:*:*",
        "purl": "pkg:generic/kubernetes/kubernetes@1.30.4",
    },
    SERVER_SOFTWARE[3],
    SERVER_SOFTWARE[0],
)


def build_enterprise_demo_assets() -> list[DemoAsset]:
    result: list[DemoAsset] = []

    for index in range(1, 21):
        site = SITES[(index - 1) % len(SITES)]
        result.append(
            DemoAsset(
                asset={
                    "hostname": f"srv-prod-{index:03d}",
                    "ip_address": f"10.{10 + (index - 1) % 4}.10.{20 + index}",
                    "asset_type": "server",
                    "operating_system": "Ubuntu Server 22.04 LTS" if index % 2 else "Debian 12",
                    "environment": "production",
                    "criticality": "critical" if index <= 8 else "high",
                    "internet_exposed": index <= 4,
                    "owner": "Équipe infrastructure",
                    "description": f"Donnée synthétique de démonstration — serveur du site {site}.",
                },
                software=SERVER_SOFTWARE,
            )
        )

    for index in range(1, 71):
        department = DEPARTMENTS[(index - 1) % len(DEPARTMENTS)]
        site_index = (index - 1) % len(SITES)
        result.append(
            DemoAsset(
                asset={
                    "hostname": f"ws-{department}-{index:03d}",
                    "ip_address": f"10.{20 + site_index}.20.{20 + index}",
                    "asset_type": "workstation",
                    "operating_system": "Windows 11 Pro 23H2",
                    "environment": "production",
                    "criticality": "high" if department in {"finance", "rh"} else "medium",
                    "internet_exposed": False,
                    "owner": f"Service {department}",
                    "description": f"Donnée synthétique de démonstration — poste {department}, site {SITES[site_index]}.",
                },
                software=WORKSTATION_SOFTWARE,
            )
        )

    for index in range(1, 11):
        site = SITES[(index - 1) % len(SITES)]
        result.append(
            DemoAsset(
                asset={
                    "hostname": f"net-core-{index:03d}",
                    "ip_address": f"10.{30 + (index - 1) % 4}.1.{index}",
                    "asset_type": "network_device",
                    "operating_system": "Cisco IOS XE 17.9",
                    "environment": "production",
                    "criticality": "critical",
                    "internet_exposed": index in {1, 5},
                    "owner": "Équipe réseau",
                    "description": f"Donnée synthétique de démonstration — équipement réseau du site {site}.",
                },
                software=NETWORK_SOFTWARE,
            )
        )

    for index in range(1, 8):
        result.append(
            DemoAsset(
                asset={
                    "hostname": f"app-metier-{index:03d}",
                    "ip_address": f"10.40.10.{30 + index}",
                    "asset_type": "application",
                    "operating_system": "Red Hat Enterprise Linux 9",
                    "environment": "production" if index <= 5 else "development",
                    "criticality": "critical" if index <= 3 else "high",
                    "internet_exposed": index in {1, 2},
                    "owner": "Équipe applications",
                    "description": "Donnée synthétique de démonstration — application métier PME.",
                },
                software=APPLICATION_SOFTWARE,
            )
        )

    for index in range(1, 6):
        result.append(
            DemoAsset(
                asset={
                    "hostname": f"cloud-workload-{index:03d}",
                    "ip_address": None,
                    "asset_type": "cloud_resource",
                    "operating_system": "Ubuntu 22.04 container host",
                    "environment": "production" if index <= 3 else "testing",
                    "criticality": "high",
                    "internet_exposed": index <= 2,
                    "owner": "Équipe cloud",
                    "description": "Donnée synthétique de démonstration — charge de travail cloud.",
                },
                software=CLOUD_SOFTWARE,
            )
        )

    return result


def seed_enterprise_demo(db: Session) -> dict[str, int]:
    existing_hostnames = set(db.scalars(select(Asset.hostname)).all())
    assets_created = 0
    software_created = 0

    for item in build_enterprise_demo_assets():
        hostname = str(item.asset["hostname"])
        if hostname in existing_hostnames:
            continue
        asset = Asset(**item.asset)
        db.add(asset)
        db.flush()
        for software_data in item.software:
            db.add(Software(asset_id=asset.id, **software_data))
            software_created += 1
        existing_hostnames.add(hostname)
        assets_created += 1

    db.commit()
    return {"assets_created": assets_created, "software_created": software_created}
