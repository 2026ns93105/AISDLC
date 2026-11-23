"""Natural Language Reminder Agent API and command-line entry point."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Optional

try:
    from .parser import parse_reminder_text
except ImportError:
    from parser import parse_reminder_text


def process_request(text: str, now: Optional[datetime] = None) -> dict:
    """Return a structured response for one natural-language reminder request."""
    return parse_reminder_text(text, now=now)


def main() -> int:
    request = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read().strip()
    print(json.dumps(process_request(request), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
