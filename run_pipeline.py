from pathlib import Path
from datetime import datetime
import json
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "metadata"
    / "pipeline_status.json"
)

STEPS = [
    (
        "ECB data extraction",
        PROJECT_ROOT / "src" / "extract" / "ecb_rates.py"
    ),
    (
        "Interest rate transformation",
        PROJECT_ROOT / "src" / "transform"
        / "prepare_interest_rates.py"
    ),
    (
        "Synthetic customer generation",
        PROJECT_ROOT / "src" / "generate"
        / "generate_customer_portfolio.py"
    ),
    (
        "Database load",
        PROJECT_ROOT / "src" / "load" / "load_database.py"
    ),
    (
        "Data quality validation",
        PROJECT_ROOT / "src" / "quality" / "validate_data.py"
    ),
    (
        "Analytical exports",
        PROJECT_ROOT / "src" / "export" / "export_analytics.py"
    )
]


def write_metadata(status, started_at, completed_steps,
                   current_step=None, error=None):

    now = datetime.now().astimezone()

    metadata = {
        "status": status,
        "started_at": started_at.isoformat(timespec="seconds"),
        "updated_at": now.isoformat(timespec="seconds"),
        "last_refresh": (
            now.isoformat(timespec="seconds")
            if status == "success"
            else None
        ),
        "pipeline_steps": len(STEPS),
        "completed_steps": completed_steps,
        "current_step": current_step,
        "error": error
    }

    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = METADATA_PATH.with_suffix(".tmp")

    temporary_path.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    temporary_path.replace(METADATA_PATH)


def run_step(number, total, name, script):

    print(f"\n[{number}/{total}] {name}", flush=True)

    subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT,
        check=True
    )

    print(f"[OK] {name}", flush=True)


def main():

    start_time = datetime.now().astimezone()
    completed_steps = 0
    current_step = None

    print("=" * 60)
    print("BANKING PRICING INTELLIGENCE PIPELINE")
    print("=" * 60, flush=True)

    write_metadata(
        status="running",
        started_at=start_time,
        completed_steps=completed_steps
    )

    try:
        for number, (name, script) in enumerate(STEPS, start=1):
            current_step = name

            write_metadata(
                status="running",
                started_at=start_time,
                completed_steps=completed_steps,
                current_step=current_step
            )

            run_step(number, len(STEPS), name, script)
            completed_steps += 1

    except (subprocess.CalledProcessError, OSError) as error:

        write_metadata(
            status="failed",
            started_at=start_time,
            completed_steps=completed_steps,
            current_step=current_step,
            error=str(error)
        )

        print(f"\n[FAILED] Pipeline stopped: {current_step}")
        print(f"Error: {error}")

        if isinstance(error, subprocess.CalledProcessError):
            return error.returncode

        return 1

    write_metadata(
        status="success",
        started_at=start_time,
        completed_steps=completed_steps
    )

    elapsed = (
        datetime.now().astimezone() - start_time
    ).total_seconds()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Execution time: {elapsed:.1f} seconds")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())