import json
import math
import os
import statistics
import time
import urllib.error
import urllib.request


class RequestError(ValueError):
    """Keep overload outcomes typed; callers own bounded retries and backoff."""

    def __init__(self, error, status=200, *, started=False, retry_after=None):
        super().__init__(error)
        self.error = error
        self.status = status
        self.code = error.get("code")
        self.retryable = not started and error.get("retryable", status in (408, 429, 503))
        try:
            delay = float(error.get("retry_after_ms", 1000)) / 1000
            if retry_after is not None:
                delay = float(retry_after)
            self.retry_after_s = max(0.1, min(delay, 10.0)) if math.isfinite(delay) else 1.0
        except (TypeError, ValueError):
            self.retry_after_s = 1.0


def events(response):
    pending = []
    for raw in response:
        line = raw.decode().rstrip("\r\n")
        if not line and pending:
            yield "\n".join(pending)
            pending = []
        elif line.startswith("data:"):
            pending.append(line[5:].lstrip())
    if pending:
        raise ValueError("Unterminated SSE event")


def request(
    base_url, body, barrier=None, *, on_content=None, collect_arrivals=False, timeout_s=1800
):
    headers = {"Content-Type": "application/json"}
    if os.getenv("THORUSTINFER_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["THORUSTINFER_API_KEY"]
    payload = dict(body, stream=True, stream_options={"include_usage": True})
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers=headers,
    )
    if barrier:
        barrier.wait(timeout=30)
    start = time.perf_counter()
    usage, finish, done = None, None, False
    arrivals, content, reasoning = [], [], []
    first_content, first_reasoning = None, None
    try:
        response = urllib.request.urlopen(req, timeout=timeout_s)
    except urllib.error.HTTPError as error:
        with error:
            raw = error.read()
        try:
            details = json.loads(raw)["error"]
        except (ValueError, KeyError, TypeError):
            details = {"message": raw.decode(errors="replace")}
        raise RequestError(
            details, error.code, retry_after=error.headers.get("Retry-After")
        ) from error
    with response:
        for event in events(response):
            at = time.perf_counter() - start
            if event == "[DONE]":
                done = True
                break
            value = json.loads(event)
            if value.get("error"):
                raise RequestError(value["error"], started=bool(arrivals))
            usage = value.get("usage") or usage
            for choice in value.get("choices", []):
                delta = choice.get("delta", {})
                if delta.get("content") and first_content is None:
                    first_content = at
                if delta.get("reasoning_content") and first_reasoning is None:
                    first_reasoning = at
                if (
                    delta.get("content")
                    or delta.get("reasoning_content")
                    or delta.get("tool_calls")
                ):
                    arrivals.append(at)
                    if on_content is not None:
                        on_content(at)
                content.append(delta.get("content", ""))
                reasoning.append(delta.get("reasoning_content", ""))
                finish = choice.get("finish_reason") or finish
    if not done or not usage or not finish:
        raise ValueError("Incomplete stream or missing usage")
    gaps = [b - a for a, b in zip(arrivals, arrivals[1:])]
    result = dict(
        usage=usage,
        finish_reason=finish,
        content="".join(content),
        reasoning="".join(reasoning),
        ttft_s=arrivals[0] if arrivals else None,
        wall_s=time.perf_counter() - start,
        chunk_gap_p50_s=statistics.median(gaps) if gaps else None,
        chunk_gap_max_s=max(gaps) if gaps else None,
    )
    if collect_arrivals:
        result.update(
            started_monotonic_s=start,
            arrivals_s=arrivals,
            first_content_s=first_content,
            first_reasoning_s=first_reasoning,
        )
    return result
