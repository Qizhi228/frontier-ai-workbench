"""Run due daily research tasks once; intended for a systemd timer."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.daily import DailyTaskRunner
from app.runtime import build_api


def main() -> None:
    api = build_api()
    runner = DailyTaskRunner(api.service.store, api.service)
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    executed = runner.run_due(now)
    print(f"executed={executed}")


if __name__ == "__main__":
    main()
