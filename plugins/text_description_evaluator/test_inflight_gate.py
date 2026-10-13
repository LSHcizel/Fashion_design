"""Rewriter HTTP timeout starts after a local inflight slot is acquired."""

import json
import threading
import time
import unittest
from unittest.mock import patch

from plugins.text_description_evaluator.design_text_evaluator_api import (
    ApiLLMJudge,
    InflightGate,
)


class _Body:
    def __init__(self, hold: threading.Event, entered: threading.Event) -> None:
        self._hold = hold
        self._entered = entered

    def __enter__(self):
        self._entered.set()
        self._hold.wait(2)
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"content": "a wool coat"}}]}
        ).encode("utf-8")


class InflightGateTimeoutTest(unittest.TestCase):
    def test_queue_wait_is_outside_the_http_timeout(self) -> None:
        gate = InflightGate(1)
        judge = ApiLLMJudge(
            api_key="local",
            api_base="http://127.0.0.1:8001/v1",
            model="rewriter",
            timeout=300,
            inflight_gate=gate,
        )
        first_hold = threading.Event()
        first_entered = threading.Event()
        second_entered = threading.Event()
        timeouts = []
        order = []

        def fake_urlopen(request, timeout, context=None):
            del request, context
            timeouts.append(timeout)
            if not first_entered.is_set():
                order.append("first")
                return _Body(first_hold, first_entered)
            order.append("second")
            ready = threading.Event()
            ready.set()
            return _Body(ready, second_entered)

        def call():
            return judge._request_completion("system", "user")

        with patch("urllib.request.urlopen", fake_urlopen):
            first = threading.Thread(target=call)
            second = threading.Thread(target=call)
            first.start()
            self.assertTrue(first_entered.wait(2))
            second.start()
            time.sleep(0.2)
            self.assertFalse(second_entered.is_set())
            first_hold.set()
            first.join(2)
            second.join(2)

        self.assertEqual(order, ["first", "second"])
        self.assertEqual(timeouts, [300, 300])
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())


if __name__ == "__main__":
    unittest.main()
