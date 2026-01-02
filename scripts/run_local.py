import logging
from pathlib import Path

from rim_engine.config import RIMConfig
from rim_engine.panel import run_end_to_end
from rim_engine.util.errors import (
    EmptyResultError,
    InvalidArgumentsError,
    MissingInputsError,
    RimEngineError,
)
from rim_engine.util.logging import setup_logging

log = logging.getLogger("rim_engine.run_local")


def main() -> int:
    setup_logging()

    try:
        cfg = RIMConfig()
        data_dir = Path("data")
        out_dir = Path("outputs")

        ts, panel = run_end_to_end(data_dir, out_dir, cfg)

        print(
            "OK | rows =",
            len(ts),
            "| latest =",
            panel["latest_timestamp"],
            "| RIM =",
            round(panel["latest"]["RIM_0_100"], 2),
        )

        return 0

    except InvalidArgumentsError as e:
        log.error("INVALID_ARGUMENT | %s", e)
        return 2

    except MissingInputsError as e:
        log.error("MISSING_INPUTS | %s", e)
        return 3

    except EmptyResultError as e:
        log.error("EMPTY_RESULT | %s", e)
        return 3

    except RimEngineError as e:
        log.exception("RIM_ENGINE_ERROR | %s", e)
        return 4

    except Exception as e:
        log.exception("INTERNAL_ERROR | %s", e)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
