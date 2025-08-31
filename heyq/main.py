from __future__ import annotations
import argparse
from loguru import logger

from .config import CONFIG
from .logger import setup_logger
from .voice.voice_interface import VoiceInterface
from .nlp.parser import NLPEngine
from .automation.engine import BrowserManager, BrowserConfig
from .automation.actions import ActionRunner
from .reporting import record_voice_trace
from .security.audit import audit


def cli():
    parser = argparse.ArgumentParser(description="HeyQ - Voice-controlled automation")
    parser.add_argument("--mode", choices=["voice", "test"], default="test")
    parser.add_argument("--browser", default=CONFIG.browser)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    setup_logger(CONFIG.log_level)

    if args.mode == "voice":
        from .config import Config
        # Override config at runtime
        CONFIG_OVERRIDE = Config(browser=args.browser, headed=args.headed)
    with BrowserManager(BrowserConfig(name=args.browser, headed=args.headed)) as bm:
            nlp = NLPEngine()
            runner = ActionRunner(bm)
            vi = VoiceInterface()
            vi.start()
            try:
                while True:
                    cmd = vi.get_command(timeout=1.0)
                    if not cmd:
                        continue
                    intent = nlp.parse(cmd)
                    logger.info("Intent: {}", intent)
                    record_voice_trace(cmd, intent.name, intent.entities)
            audit("voice.intent", {"raw": "***", "intent": intent.name, "entities": {k: ("***" if isinstance(v, str) else v) for k, v in intent.entities.items()}})
                    runner.run(intent)
            except KeyboardInterrupt:
                vi.stop()
    else:
        print("Use pytest to run tests. Example: pytest -n auto --html=heyq/reports/report.html --self-contained-html")
