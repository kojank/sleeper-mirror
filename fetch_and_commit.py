#!/usr/bin/env python3
"""
Runs INSIDE the GitHub Action (on GitHub's own runner, which has full,
unrestricted internet access) — not part of the Claude skill's own execution.
Snapshots this league's Sleeper data into JSON files and leaves them staged for
the workflow to commit. See references/github_mirror_setup.md for setup.

Requires the SLEEPER_LEAGUE_ID environment variable (set as a repository
variable in GitHub: Settings > Secrets and variables > Actions > Variables).
"""

import json
import os
import urllib.request

BASE = "https://api.sleeper.app/v1"
LEAGUE_ID = os.environ["SLEEPER_LEAGUE_ID"]


def get(path):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    write("data/league.json", get(f"/league/{LEAGUE_ID}"))
    write("data/rosters.json", get(f"/league/{LEAGUE_ID}/rosters"))
    write("data/users.json", get(f"/league/{LEAGUE_ID}/users"))
    write("data/trending_add.json", get("/players/nfl/trending/add?lookback_hours=24&limit=25"))
    write("data/trending_drop.json", get("/players/nfl/trending/drop?lookback_hours=24&limit=25"))

    # Matchups are small per week (one entry per team) — mirroring all 18 weeks
    # avoids needing to update a "current week" variable manually all season.
    for week in range(1, 19):
        write(f"data/matchups/week_{week:02d}.json", get(f"/league/{LEAGUE_ID}/matchups/{week}"))

    print("Mirror updated.")


if __name__ == "__main__":
    main()
