import json

from app.database import SessionLocal
from app.services.enterprise_demo_seed import seed_enterprise_demo


def main() -> None:
    with SessionLocal() as db:
        result = seed_enterprise_demo(db)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
