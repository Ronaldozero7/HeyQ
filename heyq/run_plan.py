from __future__ import annotations
import argparse
from pathlib import Path
import yaml
from loguru import logger

from .logger import setup_logger
from .automation.engine import BrowserManager
from .automation.actions import ActionRunner
from .nlp.intent import Intent


def run_actions(plan_path: Path):
    with open(plan_path, 'r') as f:
        plan = yaml.safe_load(f)
    steps = plan.get('steps', [])
    with BrowserManager() as bm:
        runner = ActionRunner(bm)
        for s in steps:
            intent = Intent(name=s['intent'], entities=s.get('entities', {}))
            logger.info("Plan step -> {}", intent)
            runner.run(intent)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('plan', type=Path)
    args = p.parse_args()
    setup_logger()
    run_actions(args.plan)


if __name__ == '__main__':
    main()
