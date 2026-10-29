"""Benchmark local HTTP transports and a real headless browser on a loopback fixture.

This harness requests no external pages. It measures transport behavior only;
fixture results do not establish LinkedIn coverage, speed or adapter suitability.
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import importlib.metadata
import json
import math
import os
import platform
import re
import resource
import socketserver
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FIXTURE_IDS = tuple(f"post-{n:03d}" for n in range(1, 21))
STATIC_HTML_TEMPLATE = '<!doctype html><html><body><article data-id="{id}"><h2>Fixture {id}</h2><p>Frozen local benchmark item.</p></article></body></html>'
JS_HTML = "<!doctype html><html><body><main id=\"posts\"></main><script>document.querySelector('#posts').innerHTML='<article data-id=\"js-post-001\"><h2>Rendered fixture</h2></article>';</script></body></html>"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


class _FixtureHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/warmup":
            body = b"<!doctype html><title>warmup</title>"
            content_type = "text/html; charset=utf-8"
        elif path == "/js":
            body = JS_HTML.encode("utf-8")
            content_type = "text/html; charset=utf-8"
        elif path.startswith("/post/") and path.rsplit("/", 1)[-1] in FIXTURE_IDS:
            post_id = path.rsplit("/", 1)[-1]
            body = STATIC_HTML_TEMPLATE.format(id=post_id).encode("utf-8")
            content_type = "text/html; charset=utf-8"
        else:
            body = b"not found"
            content_type = "text/plain; charset=utf-8"
            self.send_response(404)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return


class _Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def _extract_static_ids(html: str) -> list[str]:
    # Ignore markup literals embedded in script source. Only parsed/rendered
    # article elements count as fixture records.
    visible_markup = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", html, flags=re.IGNORECASE | re.DOTALL)
    return re.findall(r'<article\s+data-id=["\']([^"\']+)["\']', visible_markup)


def _worker(strategy: str, base_url: str) -> dict[str, Any]:
    import psutil

    expected = list(FIXTURE_IDS)
    latencies: list[float] = []
    observed: list[str] = []
    errors: list[str] = []
    startup_seconds: float | None = None
    browser_version: str | None = None
    js_observed: list[str] = []
    js_probe_error: str | None = None
    browser = None
    page = None
    browser_context = None
    pw = None
    process = psutil.Process()
    cpu_before = process.cpu_times().user + process.cpu_times().system
    run_started = time.perf_counter()
    policy_completed = False

    if strategy in {"urllib-policy", "httpx-policy"}:
        import asyncio
        from .transport import HttpxTransport, UrllibTransport

        class MemoryState:
            def get_suspension(self, _key):
                return None

            def suspend(self, _key, _reason, retry_after_seconds=None):
                raise RuntimeError("fixture must not suspend")

            def log_request(self, _source_id, _event):
                return None

        spec = {
            "source_id": "benchmark-local-fixture",
            "access_group": "benchmark-local-fixture",
            "allowed_hosts": [],
            "permitted_methods": ["GET"],
            "permissions": {"collection": True},
            "rate_per_second": 1000,
            "concurrency": 1,
            "timeout_seconds": 10,
            "max_bytes": 100_000,
            "max_attempts": 1,
            "allow_local_test": True,
        }
        transport_class = UrllibTransport if strategy == "urllib-policy" else HttpxTransport
        transport = transport_class(spec, MemoryState())

        async def run_policy() -> None:
            nonlocal observed, js_observed, js_probe_error, errors, measured_wall
            await transport.fetch(base_url + "/warmup")
            measured_started = time.perf_counter()
            for post_id in expected:
                started = time.perf_counter()
                try:
                    response = await transport.fetch(base_url + "/post/" + post_id)
                    latencies.append(time.perf_counter() - started)
                    observed.extend(_extract_static_ids(response.body.decode("utf-8")))
                except Exception as exc:
                    latencies.append(time.perf_counter() - started)
                    errors.append(f"{post_id}: {type(exc).__name__}: {exc}")
            measured_wall = time.perf_counter() - measured_started
            try:
                response = await transport.fetch(base_url + "/js")
                js_observed = _extract_static_ids(response.body.decode("utf-8"))
            except Exception as exc:
                js_probe_error = f"{type(exc).__name__}: {exc}"
            await transport.aclose()

        asyncio.run(run_policy())
        policy_completed = True
    elif strategy == "httpx-pooled":
        import httpx

        client = httpx.Client(timeout=10, follow_redirects=False, trust_env=False, limits=httpx.Limits(max_connections=1, max_keepalive_connections=1))

        def get(url: str) -> str:
            response = client.get(url)
            response.raise_for_status()
            return response.text

        get(base_url + "/warmup")
        request = get
    elif strategy == "urllib":
        from urllib.request import urlopen

        def get(url: str) -> str:
            with urlopen(url, timeout=10) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read().decode("utf-8")

        # Warmup is outside the fixed request and latency denominator.
        get(base_url + "/warmup")
        request = get
    elif strategy == "httpx":
        import httpx

        client = httpx.Client(timeout=10, follow_redirects=False, limits=httpx.Limits(max_connections=1, max_keepalive_connections=1))

        def get(url: str) -> str:
            response = client.get(url)
            response.raise_for_status()
            return response.text

        get(base_url + "/warmup")
        request = get
    elif strategy == "playwright":
        from playwright.sync_api import sync_playwright

        pw = sync_playwright().start()
        startup = time.perf_counter()
        browser = pw.chromium.launch(headless=True, executable_path=CHROME_PATH)
        browser_version = browser.version
        startup_seconds = time.perf_counter() - startup
        browser_context = browser.new_context()
        page = browser_context.new_page()
        page.goto(base_url + "/warmup", wait_until="domcontentloaded", timeout=10000)

        def get(url: str) -> str:
            page.goto(url, wait_until="domcontentloaded", timeout=10000)
            return page.content()

        request = get
    else:
        raise ValueError(f"unknown strategy: {strategy}")

    if not policy_completed:
        measured_started = time.perf_counter()
        for post_id in expected:
            started = time.perf_counter()
            try:
                html = request(base_url + "/post/" + post_id)
                latencies.append(time.perf_counter() - started)
                observed.extend(_extract_static_ids(html))
            except Exception as exc:  # report fixture errors rather than hiding failures
                latencies.append(time.perf_counter() - started)
                errors.append(f"{post_id}: {type(exc).__name__}: {exc}")
        measured_wall = time.perf_counter() - measured_started

        # Capability-only check. This request is excluded from the static latency sample.
        try:
            if strategy == "playwright":
                page.goto(base_url + "/js", wait_until="domcontentloaded", timeout=10000)
                page.wait_for_selector("article[data-id='js-post-001']", timeout=2000)
                js_observed = page.locator("article[data-id]").evaluate_all("els => els.map(el => el.dataset.id)")
            else:
                html = request(base_url + "/js")
                js_observed = _extract_static_ids(html)
        except Exception as exc:
            js_probe_error = f"{type(exc).__name__}: {exc}"

    # Close browser processes before reading child-resource high-water counters.
    if strategy in {"httpx", "httpx-pooled"}:
        client.close()
    if browser_context:
        browser_context.close()
    if browser:
        browser.close()
    if pw:
        pw.stop()
    cpu_after = process.cpu_times().user + process.cpu_times().system
    child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    child_rss_units = "bytes" if sys.platform == "darwin" else "KiB"
    child_rss_bytes = int(child_usage.ru_maxrss if child_rss_units == "bytes" else child_usage.ru_maxrss * 1024)
    result = {
        "strategy": strategy,
        "implementation": {
            "urllib-policy": "research.collector.transport.UrllibTransport",
            "httpx-policy": "research.collector.transport.HttpxTransport",
            "httpx-pooled": "standalone pooled httpx.Client diagnostic; not adoption evidence",
            "urllib": "stdlib urllib baseline without project transport policy",
            "httpx": "standalone HTTPX diagnostic",
            "playwright": "Playwright sync API with installed local Chrome headless",
        }.get(strategy, strategy),
        "requests": len(expected),
        "successful_records": len(observed),
        "unique_records": len(set(observed)),
        "duplicate_records": len(observed) - len(set(observed)),
        "ground_truth_exact": set(observed) == set(expected) and len(observed) == len(expected),
        "missing_ids": sorted(set(expected) - set(observed)),
        "unexpected_ids": sorted(set(observed) - set(expected)),
        "latency_mean_ms": statistics.mean(latencies) * 1000 if latencies else None,
        "latency_p95_ms_nearest_rank": _p95(latencies) * 1000 if latencies else None,
        "latency_samples_ms": [round(v * 1000, 4) for v in latencies],
        "measured_wall_seconds": measured_wall,
        "cold_browser_startup_seconds": startup_seconds,
        "browser_version": browser_version,
        "errors": errors,
        "error_rate_per_1000_requests": len(errors) * 1000 / len(expected),
        "js_fixture": {
            "expected_id": "js-post-001",
            "observed_ids": js_observed,
            "covered": "js-post-001" in js_observed,
            "error": js_probe_error,
            "excluded_from_static_speed_denominator": True,
        },
        "worker_cpu_seconds": max(0.0, cpu_after - cpu_before),
        "reaped_child_cpu_seconds": child_usage.ru_utime + child_usage.ru_stime,
        "reaped_child_peak_rss_bytes_highwater": child_rss_bytes,
        "reaped_child_peak_rss_source_units": child_rss_units,
        "worker_wall_seconds": time.perf_counter() - run_started,
    }

    return result


def _run_child(strategy: str, base_url: str) -> dict[str, Any]:
    command = [sys.executable, "-m", "research.collector.benchmark", "--worker", strategy, "--base-url", base_url]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        import psutil
    except ImportError as exc:
        proc.kill()
        raise RuntimeError("psutil is required for sampled process-tree RSS") from exc
    worker = psutil.Process(proc.pid)
    peak_rss = 0
    cpu_by_pid: dict[int, float] = {}
    deadline = time.monotonic() + 60
    while proc.poll() is None:
        if time.monotonic() >= deadline:
            proc.kill()
            proc.communicate()
            return {"strategy": strategy, "status": "failed", "failure": "worker_timeout_60s"}
        try:
            tree = [worker, *worker.children(recursive=True)]
        except (psutil.NoSuchProcess, psutil.Error, PermissionError):
            tree = []
        if not tree:
            try:
                tree = [worker]
            except psutil.NoSuchProcess:
                tree = []
        rss = 0
        for item in tree:
            try:
                rss += item.memory_info().rss
                times = item.cpu_times()
                cpu_by_pid[item.pid] = times.user + times.system
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        peak_rss = max(peak_rss, rss)
        time.sleep(0.01)
    stdout, stderr = proc.communicate()
    if proc.returncode:
        summary = stderr[-2000:]
        summary = re.sub(r"--user-data-dir=[^\s]+", "--user-data-dir=<isolated-temp>", summary)
        summary = re.sub(r"playwright_chromiumdev_profile-[A-Za-z0-9_-]+", "playwright_chromiumdev_profile-<redacted>", summary)
        failure = "browser_process_crashed" if strategy == "playwright" and "SIGABRT" in summary else f"worker_exit_{proc.returncode}"
        return {
            "strategy": strategy,
            "status": "failed",
            "failure": failure,
            "diagnostic_tail": summary,
            "sampled_worker_cpu_seconds": round(sum(cpu_by_pid.values()), 6),
            "worker_peak_rss_bytes_sampled": peak_rss,
            "worker_peak_rss_mib_sampled": round(peak_rss / (1024 * 1024), 3),
            "process_tree_sampling_interval_ms": 10,
        }
    result = json.loads(stdout)
    # Use sampled process-tree CPU, which includes browser children. Keep worker-only CPU separately.
    try:
        final_children = psutil.Process(proc.pid).children(recursive=True)
    except (psutil.NoSuchProcess, psutil.Error, PermissionError):
        final_children = []
    for item in final_children:
        try:
            times = item.cpu_times()
            cpu_by_pid[item.pid] = times.user + times.system
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    result["sampled_worker_cpu_seconds"] = round(sum(cpu_by_pid.values()), 6)
    result["worker_and_reaped_children_cpu_seconds"] = round(
        result["worker_cpu_seconds"] + result["reaped_child_cpu_seconds"], 6
    )
    result["worker_peak_rss_bytes_sampled"] = peak_rss
    result["worker_peak_rss_mib_sampled"] = round(peak_rss / (1024 * 1024), 3)
    result["reaped_child_peak_rss_metric_note"] = "resource.getrusage(RUSAGE_CHILDREN).ru_maxrss; OS high-water metric, not an aggregate process-tree sample"
    result["process_tree_sampling_interval_ms"] = 10
    result["status"] = "passed"
    return result


def run_benchmark() -> dict[str, Any]:
    server = _Server(("127.0.0.1", 0), _FixtureHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        strategies = [_run_child(name, base_url) for name in ("urllib-policy", "httpx-policy", "httpx-pooled", "playwright")]
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)

    try:
        import httpx
        httpx_version = httpx.__version__
    except ImportError:
        httpx_version = None
    try:
        playwright_version = importlib.metadata.version("playwright")
    except importlib.metadata.PackageNotFoundError:
        playwright_version = None
    fixture_bytes = (STATIC_HTML_TEMPLATE + JS_HTML).encode("utf-8")
    benchmark_path = Path(__file__)
    transport_path = benchmark_path.with_name("transport.py")
    contracts_path = benchmark_path.with_name("contracts.py")
    return {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "loopback frozen fixture only; no public source requests",
        "concurrency": 1,
        "ground_truth_ids": list(FIXTURE_IDS),
        "fixture_sha256": _sha256(fixture_bytes),
        "benchmark_source_sha256": _sha256(benchmark_path.read_bytes()),
        "transport_source_sha256": _sha256(transport_path.read_bytes()),
        "contracts_source_sha256": _sha256(contracts_path.read_bytes()),
        "command": "python -m research.collector.benchmark --output <verification-path>",
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "httpx": httpx_version,
            "playwright": playwright_version,
            "browser": "existing Google Chrome, launched through Playwright headless Chromium driver",
        },
        "cost_methodology": {
            "external_provider_requests": 0,
            "external_provider_spend_usd": 0,
            "on_device_cpu_and_memory": "measured; not monetized",
            "cost_per_1000_external_provider_requests_usd": 0,
            "cost_per_1000_total_workloads": "not priced; excludes hardware, electricity and operator time",
        },
        "strategies": strategies,
        "limitations": [
            "Fixture results do not establish LinkedIn-wide coverage, production latency, reliability or optimal transport.",
            "Worker RSS is sampled every 10 ms and can miss short peaks; reaped browser-child RSS is a platform high-water metric, not a summed process-tree sample.",
            "Browser cold startup is reported separately; per-page request latency is measured after startup and one warmup navigation.",
            "The JavaScript fixture is a capability check and is excluded from the static speed denominator.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", choices=("urllib", "urllib-policy", "httpx-policy", "httpx-pooled", "playwright"))
    parser.add_argument("--base-url")
    args = parser.parse_args()
    if args.worker:
        if not args.base_url:
            parser.error("--base-url is required with --worker")
        print(json.dumps(_worker(args.worker, args.base_url), separators=(",", ":")))
        return
    result = run_benchmark()
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
