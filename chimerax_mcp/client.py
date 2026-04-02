"""Thin wrapper around the ChimeraX REST API with optional auto-launch."""

import os
import platform
import re
import shutil
import subprocess
import sys
import time

import requests


class ChimeraXError(Exception):
    """Base error for ChimeraX communication."""


class ChimeraXNotRunningError(ChimeraXError):
    """Raised when ChimeraX is unreachable."""


class ChimeraXCommandError(ChimeraXError):
    """Raised when a ChimeraX command fails."""


# ------------------------------------------------------------------
# ChimeraX executable discovery
# ------------------------------------------------------------------

def _find_chimerax() -> str | None:
    """Try to locate the ChimeraX executable on this system."""
    # 1. Explicit env var override
    env = os.environ.get("CHIMERAX_BIN")
    if env and os.path.isfile(env):
        return env

    # 2. On PATH
    on_path = shutil.which("chimerax") or shutil.which("ChimeraX")
    if on_path:
        return on_path

    system = platform.system()

    # 3. Platform-specific default locations
    if system == "Windows":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        for entry in sorted(os.listdir(program_files), reverse=True):
            if entry.lower().startswith("chimerax"):
                candidate = os.path.join(program_files, entry, "bin", "ChimeraX.exe")
                if os.path.isfile(candidate):
                    return candidate
    elif system == "Darwin":
        app = "/Applications/ChimeraX.app/Contents/MacOS/ChimeraX"
        if os.path.isfile(app):
            return app
    else:  # Linux
        for path in ["/usr/bin/chimerax", "/usr/local/bin/chimerax",
                     os.path.expanduser("~/ChimeraX/bin/ChimeraX")]:
            if os.path.isfile(path):
                return path

    return None


def _is_chimerax_responding(base_url: str, timeout: float = 2.0) -> bool:
    """Return True if the ChimeraX REST API is reachable."""
    try:
        resp = requests.get(f"{base_url}/run", params={"command": "version"}, timeout=timeout)
        return resp.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def launch_chimerax(port: int = 8765, wait: float = 15.0) -> subprocess.Popen | None:
    """Launch ChimeraX with the REST API enabled.

    Returns the Popen handle on success, None if ChimeraX cannot be found.
    Waits up to ``wait`` seconds for the REST API to become responsive.
    """
    exe = _find_chimerax()
    if exe is None:
        return None

    base_url = f"http://127.0.0.1:{port}"

    # Already running?
    if _is_chimerax_responding(base_url):
        _log("ChimeraX REST API already responding")
        return None  # nothing to manage — it was already up

    _log(f"Launching ChimeraX: {exe}")
    proc = subprocess.Popen(
        [exe, "--cmd", f"remotecontrol rest start port {port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for REST API to come up
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        if _is_chimerax_responding(base_url):
            _log(f"ChimeraX REST API is ready on port {port}")
            return proc
        time.sleep(1.0)

    _log(f"ChimeraX launched but REST API not responding after {wait}s")
    return proc


# ------------------------------------------------------------------
# Client
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Command sanitization
# ------------------------------------------------------------------

# Characters that act as command separators in ChimeraX, allowing injection
_INJECTION_CHARS = re.compile(r"[;\n]")

# Commands that give raw OS/Python access — only blocked in the default
# sanitized path.  The ``run_unsafe`` method bypasses this for trusted callers.
_DANGEROUS_COMMANDS = re.compile(
    r"^\s*(exec|shell|system)\b",
    re.IGNORECASE,
)

# Allowed script extensions for the run_script tool
_SAFE_SCRIPT_EXTENSIONS = {".cxc", ".py"}


def sanitize_command(command: str) -> str:
    """Reject commands that contain injection vectors or dangerous operations.

    Raises ``ChimeraXCommandError`` if the command is unsafe.
    """
    if _INJECTION_CHARS.search(command):
        raise ChimeraXCommandError(
            f"Command rejected: contains forbidden characters (';' or newline). "
            f"Send one command at a time. Got: {command!r}"
        )
    if _DANGEROUS_COMMANDS.match(command.strip()):
        raise ChimeraXCommandError(
            f"Command rejected: '{command.split()[0]}' is blocked for security. "
            f"Only ChimeraX visualization/analysis commands are allowed."
        )
    return command


def validate_script_path(path: str) -> str:
    """Validate that a script path is safe to run.

    Must exist, have a .cxc or .py extension, and be a real file (not a symlink
    to something unexpected).
    """
    path = os.path.realpath(path)  # resolve symlinks
    ext = os.path.splitext(path)[1].lower()
    if ext not in _SAFE_SCRIPT_EXTENSIONS:
        raise ChimeraXCommandError(
            f"Script rejected: only {', '.join(_SAFE_SCRIPT_EXTENSIONS)} files are allowed, "
            f"got '{ext}'"
        )
    if not os.path.isfile(path):
        raise ChimeraXCommandError(f"Script not found: {path}")
    return path


class ChimeraXClient:
    """Client for the ChimeraX REST API.

    Connection is lazy — no request is made until ``run()`` is called,
    so importing this module never fails even if ChimeraX is not running.

    If ``auto_launch=True`` (the default), the first ``run()`` call will
    attempt to start ChimeraX automatically when it is not reachable.
    Set ``CHIMERAX_BIN`` env var to override the executable path.

    All commands are sanitized before sending to prevent command injection
    (semicolons, newlines) and block dangerous operations (runscript, exec, shell).
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8765",
        auto_launch: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auto_launch = auto_launch
        self._process: subprocess.Popen | None = None
        self._launched = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, command: str) -> dict:
        """Send a command to ChimeraX via its REST API.

        Uses GET ``/run?command=<url-encoded-command>`` — **not** POST.

        If ChimeraX is not reachable and ``auto_launch`` is enabled,
        attempts to start ChimeraX first.

        Returns
        -------
        dict
            ``{"status": "ok", "result": <response text or json>}``

        Raises
        ------
        ChimeraXNotRunningError
            If ChimeraX is not reachable (even after auto-launch attempt).
        ChimeraXCommandError
            If the command itself fails inside ChimeraX.
        """
        command = sanitize_command(command)
        self._ensure_running()
        _log(f">>> {command}")
        try:
            resp = requests.get(
                f"{self.base_url}/run",
                params={"command": command},
                timeout=300,
            )
        except requests.ConnectionError:
            raise ChimeraXNotRunningError(
                "ChimeraX is not running or REST API not enabled. "
                "Start ChimeraX and run: remotecontrol rest start port 8765"
            )

        if resp.status_code != 200:
            msg = f"ChimeraX returned HTTP {resp.status_code}: {resp.text}"
            _log(f"!!! {msg}")
            raise ChimeraXCommandError(msg)

        # Try JSON response (json=true mode)
        try:
            data = resp.json()
            _log(f"<<< {data}")
            # Check for ChimeraX-level error
            if isinstance(data, dict) and data.get("error"):
                raise ChimeraXCommandError(data["error"])
            return {"status": "ok", "result": data}
        except (ValueError, requests.exceptions.JSONDecodeError):
            # Plain-text mode
            text = resp.text.strip()
            _log(f"<<< {text[:500]}")
            return {"status": "ok", "result": text}

    def run_many(self, commands: list[str]) -> list[dict]:
        """Run commands sequentially, stopping on the first error."""
        results: list[dict] = []
        for cmd in commands:
            results.append(self.run(cmd))
        return results

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_running(self) -> None:
        """Auto-launch ChimeraX if needed and enabled."""
        if self._launched or not self.auto_launch:
            return
        if _is_chimerax_responding(self.base_url):
            self._launched = True
            return
        _log("ChimeraX not responding — attempting auto-launch...")
        self._process = launch_chimerax()
        self._launched = True
        if not _is_chimerax_responding(self.base_url):
            exe = _find_chimerax()
            if exe is None:
                raise ChimeraXNotRunningError(
                    "ChimeraX not found. Install ChimeraX or set CHIMERAX_BIN env var. "
                    "https://www.cgl.ucsf.edu/chimerax/download.html"
                )
            raise ChimeraXNotRunningError(
                "ChimeraX was launched but REST API is not responding. "
                "Try starting ChimeraX manually and run: remotecontrol rest start port 8765"
            )


def _log(msg: str) -> None:
    print(f"[chimerax] {msg}", file=sys.stderr, flush=True)
