"""
Multi-Server Manager for Pharmacy Matcher.
Supports dual local AI servers:
1. MSEMAX ChatGPT (OpenAI Web Hook) on Port 8000
2. MSEMAX Google AI Studio (Gemini Web Hook) on Port 8001

Provides start, stop, test (live latency & ping), session login, and 1-click active switching.
"""

import subprocess
import os
import signal
import time
import sys
import threading
import socket
from pathlib import Path
import requests
from src.config import gateway_api_key

DEFAULT_SERVERS = {
    "chatgpt": {
        "name": "MSEMAX (ChatGPT / OpenAI)",
        "default_dir": r"D:\AI_Engineer\MSEMAX",
        "port": 8000,
        "default_model": "gpt-4o",
        "url": "http://127.0.0.1:8000/v1/chat/completions",
        "api_key": gateway_api_key()
    },
    "gaistudio": {
        "name": "MSEMAX (Google AI Studio - Vision)",
        "default_dir": r"D:\AI_Engineer\MSEMAX-GAIStudio-vision",
        "port": 8001,
        "default_model": "gemini-3.8-flash",
        "url": "http://127.0.0.1:8001/v1/chat/completions",
        "api_key": gateway_api_key()
    }
}

def is_port_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def get_best_python() -> str:
    """Finds the best python executable containing project dependencies (fastapi, uvicorn, etc.)."""
    try:
        import fastapi  # noqa
        return sys.executable
    except ImportError:
        pass
    
    candidates = [
        r"D:\miniconda3\envs\venv\python.exe",
        str(Path(sys.prefix) / "python.exe"),
        str(Path(sys.executable).parent / "envs" / "venv" / "python.exe"),
    ]
    for c in candidates:
        if Path(c).exists():
            return str(c)
            
    return sys.executable

class ServerInstance:
    def __init__(self, key: str, config: dict, logger_callback=None):
        self.key = key
        self.name = config.get("name", key)
        self.dir = config.get("dir", config.get("default_dir", ""))
        self.port = int(config.get("port", 8000))
        self.default_model = config.get("default_model", "gpt-4o")
        self.url = config.get("url", f"http://127.0.0.1:{self.port}/v1/chat/completions")
        self.api_key = config.get("api_key", gateway_api_key())
        self.process = None
        self.logger = logger_callback

    def log(self, message: str):
        prefix = f"[{self.name}]"
        if self.logger:
            self.logger(f"{prefix} {message}")
        else:
            print(f"{prefix} {message}")

    def is_running(self) -> bool:
        if self.process is not None and self.process.poll() is None:
            return True
        return is_port_listening(self.port)

    def _read_output(self, pipe):
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    self.log(line.strip())
        except Exception:
            pass
        finally:
            pipe.close()

    def start(self) -> dict:
        if self.is_running():
            self.log(f"Server is already running on port {self.port}.")
            return {"success": True, "message": "already running", "port": self.port}

        target_dir = Path(self.dir)
        if not target_dir.exists():
            self.log(f"Error: Directory not found: {self.dir}")
            return {"success": False, "message": f"Directory not found: {self.dir}"}

        app_script = target_dir / "app.py"
        if not app_script.exists():
            self.log(f"Error: app.py not found in {self.dir}")
            return {"success": False, "message": f"app.py not found in {self.dir}"}

        try:
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW

            python_bin = get_best_python()
            self.log(f"Starting server in {self.dir} on port {self.port} with {python_bin}...")
            self.process = subprocess.Popen(
                [python_bin, "-u", "app.py"],
                cwd=str(target_dir),
                creationflags=creationflags,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            t = threading.Thread(target=self._read_output, args=(self.process.stdout,), daemon=True)
            t.start()

            # Brief check for early crash
            time.sleep(1.5)
            if self.process.poll() is not None:
                return {"success": False, "message": f"Process exited early with code {self.process.returncode}"}

            self.log(f"Server process started successfully (PID: {self.process.pid}).")
            return {"success": True, "message": "started", "pid": self.process.pid, "port": self.port}
        except Exception as e:
            self.log(f"Failed to start server: {e}")
            return {"success": False, "message": str(e)}

    def stop(self) -> dict:
        try:
            self.log(f"Stopping {self.name} on port {self.port}...")
            
            # Step 1: Call graceful /shutdown endpoint
            try:
                requests.get(f"http://127.0.0.1:{self.port}/shutdown", timeout=1.5)
            except Exception:
                pass

            # Wait briefly for port to release
            for _ in range(8):
                if not is_port_listening(self.port):
                    break
                time.sleep(0.15)

            # Step 2: Terminate tracked process if still alive
            if self.process is not None:
                try:
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)], capture_output=True)
                    else:
                        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except Exception:
                    pass
                self.process = None

            # Step 3: Check if port is still listening by any orphaned process
            if is_port_listening(self.port) and os.name == 'nt':
                try:
                    res = subprocess.run(
                        f'netstat -ano | findstr ":{self.port} "',
                        shell=True, capture_output=True, text=True
                    )
                    pids_to_kill = set()
                    for line in res.stdout.strip().splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 5 and "LISTENING" in line:
                            pids_to_kill.add(parts[-1])

                    pids_needing_elevation = set()
                    for pid in pids_to_kill:
                        r_kill = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, text=True)
                        if "Access is denied" in r_kill.stderr or r_kill.returncode != 0:
                            pids_needing_elevation.add(pid)

                    if pids_needing_elevation:
                        try:
                            import ctypes
                            pid_args = " ".join([f"/PID {p}" for p in pids_needing_elevation])
                            self.log(f"Process {pid_args} requires administrator privileges. Requesting elevation...")
                            ctypes.windll.shell32.ShellExecuteW(
                                None, "runas", "cmd.exe", f"/c taskkill /F {pid_args}", None, 0
                            )
                        except Exception as ce:
                            self.log(f"Elevation request failed: {ce}")
                except Exception as e:
                    self.log(f"Error checking port {self.port}: {e}")

            time.sleep(1.2)
            if is_port_listening(self.port):
                self.log(f"⚠️ Port {self.port} is still in use by an external elevated process.")
                return {
                    "success": False,
                    "message": f"المنفذ {self.port} محجوز بعملية سابقة تعمل كمسؤول (Administrator). يمكنك الضغط على 'تحرير المنافذ' أو تشغيل scripts\\free_ports.bat كمسؤول.",
                    "elevated": True,
                    "port": self.port
                }

            self.log(f"{self.name} stopped successfully.")
            return {"success": True, "message": "stopped"}
        except Exception as e:
            self.log(f"Failed to stop server: {e}")
            return {"success": False, "message": str(e)}

    def test(self) -> dict:
        """Sends a test ping to the server to check connectivity and response time."""
        if not self.is_running():
            return {
                "success": False,
                "latency_ms": 0,
                "error": "السيرفر متوقف حالياً. يرجى الضغط على 'تشغيل السيرفر' أولاً ثم إعادة فحص الاتصال.",
                "is_stopped": True,
                "name": self.name,
                "port": self.port
            }
        t0 = time.time()
        self.log(f"Sending test ping to {self.name} on port {self.port}...")
        try:
            # First check health endpoint
            health_url = f"http://127.0.0.1:{self.port}/health"
            health_info = {}
            try:
                r_h = requests.get(health_url, timeout=3)
                if r_h.status_code == 200:
                    health_info = r_h.json()
            except Exception:
                pass

            # Next, test chat completions
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "user", "content": "Reply with only the exact word: PONG"}
                ],
                "stream": False
            }
            r = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=25
            )
            elapsed_ms = int((time.time() - t0) * 1000)

            if r.status_code == 200:
                resp = r.json()
                reply = resp.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return {
                    "success": True,
                    "latency_ms": elapsed_ms,
                    "reply": reply,
                    "model": self.default_model,
                    "port": self.port,
                    "health": health_info
                }
            else:
                return {
                    "success": False,
                    "latency_ms": elapsed_ms,
                    "error": f"HTTP {r.status_code}: {r.text[:200]}",
                    "port": self.port
                }
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            return {
                "success": False,
                "latency_ms": elapsed_ms,
                "error": str(e),
                "port": self.port
            }

    def run_get_session(self) -> dict:
        try:
            self.log("Launching get_session.py...")
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NEW_CONSOLE

            script_file = Path(self.dir) / "get_session.py"
            if not script_file.exists():
                return {"success": False, "output": f"get_session.py not found in {self.dir}"}

            python_bin = get_best_python()
            subprocess.Popen(
                [python_bin, "get_session.py"],
                cwd=str(self.dir),
                creationflags=creationflags
            )
            return {"success": True, "output": f"Session browser opened for {self.name}."}
        except Exception as e:
            self.log(f"Failed to launch session: {e}")
            return {"success": False, "output": str(e)}

    def get_status(self) -> dict:
        is_listening = is_port_listening(self.port)
        is_managed = (self.process is not None and self.process.poll() is None)
        running = is_listening or is_managed
        is_external = is_listening and not is_managed
        pid = self.process.pid if is_managed else None
        return {
            "key": self.key,
            "name": self.name,
            "running": running,
            "is_managed": is_managed,
            "is_external": is_external,
            "pid": pid,
            "port": self.port,
            "dir": self.dir,
            "model": self.default_model,
            "url": self.url
        }

class MultiServerManager:
    def __init__(self, settings: dict, logger_callback=None, server_logger_callback=None):
        self.logger = server_logger_callback or logger_callback
        self.servers = {}

        # 1. ChatGPT Server configuration
        default_c_dir = DEFAULT_SERVERS["chatgpt"]["default_dir"]
        explicit_c_dir = settings.get("msemax_chatgpt_dir")
        if not explicit_c_dir and settings.get("msemax_dir") and "gaistudio" not in settings.get("msemax_dir").lower():
            explicit_c_dir = settings.get("msemax_dir")
        c_dir = explicit_c_dir or default_c_dir
        c_conf = dict(DEFAULT_SERVERS["chatgpt"])
        c_conf["dir"] = c_dir
        self.servers["chatgpt"] = ServerInstance("chatgpt", c_conf, logger_callback=self.logger)

        # 2. Google AI Studio Server configuration (strictly MSEMAX-GAIStudio-vision)
        default_g_dir = DEFAULT_SERVERS["gaistudio"]["default_dir"]
        explicit_g_dir = settings.get("msemax_gaistudio_dir")
        if not explicit_g_dir:
            # If msemax_dir is set and explicitly contains vision, use it; otherwise strictly default_g_dir
            if settings.get("msemax_dir") and "vision" in settings.get("msemax_dir").lower():
                explicit_g_dir = settings.get("msemax_dir")
        g_dir = explicit_g_dir or default_g_dir
        g_conf = dict(DEFAULT_SERVERS["gaistudio"])
        g_conf["dir"] = g_dir
        self.servers["gaistudio"] = ServerInstance("gaistudio", g_conf, logger_callback=self.logger)

    def get_server(self, key: str) -> ServerInstance | None:
        return self.servers.get(key)

    def get_all_status(self, active_key: str = "chatgpt") -> dict:
        return {
            k: {**srv.get_status(), "is_active": (k == active_key)}
            for k, srv in self.servers.items()
        }

    def start(self, key: str = "chatgpt") -> dict:
        srv = self.get_server(key)
        if srv:
            return srv.start()
        return {"success": False, "message": f"Server {key} not found"}

    def stop(self, key: str = "chatgpt") -> dict:
        srv = self.get_server(key)
        if srv:
            return srv.stop()
        return {"success": False, "message": f"Server {key} not found"}

    def is_running(self, key: str = "chatgpt") -> bool:
        srv = self.get_server(key)
        return srv.is_running() if srv else False

    def test(self, key: str = "chatgpt") -> dict:
        srv = self.get_server(key)
        if srv:
            return srv.test()
        return {"success": False, "error": f"Server {key} not found"}

    def run_get_session(self, key: str = "chatgpt") -> dict:
        srv = self.get_server(key)
        if srv:
            return srv.run_get_session()
        return {"success": False, "output": f"Server {key} not found"}

    def force_free_ports(self) -> dict:
        """Kills any process listening on ports 8000 and 8001 using elevated taskkill if necessary."""
        killed = []
        pids_needing_elevation = set()
        for port in [8000, 8001]:
            if is_port_listening(port) and os.name == 'nt':
                try:
                    res = subprocess.run(
                        f'netstat -ano | findstr ":{port} "',
                        shell=True, capture_output=True, text=True
                    )
                    for line in res.stdout.strip().splitlines():
                        parts = line.strip().split()
                        if len(parts) >= 5 and "LISTENING" in line:
                            pid = parts[-1]
                            r_k = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, text=True)
                            if "Access is denied" in r_k.stderr or r_k.returncode != 0:
                                ps_cmd = f"Invoke-CimMethod -InputObject (Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}') -MethodName Terminate"
                                r_ps = subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True, text=True)
                                if r_ps.returncode == 0 and "ReturnValue = 0" in r_ps.stdout:
                                    killed.append(pid)
                                else:
                                    pids_needing_elevation.add(pid)
                            else:
                                killed.append(pid)
                except Exception as e:
                    if self.logger:
                        self.logger(f"Error freeing port {port}: {e}")

        elevated_needed = False
        if pids_needing_elevation and os.name == 'nt':
            elevated_needed = True
            try:
                import ctypes
                pid_args = " ".join([f"/PID {p}" for p in pids_needing_elevation])
                if self.logger:
                    self.logger(f"[ELEVATION] Requesting administrator rights to terminate PIDs: {pid_args}")
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", "cmd.exe", f"/c taskkill /F {pid_args}", None, 0
                )
            except Exception as e:
                if self.logger:
                    self.logger(f"Elevation request failed: {e}")

        time.sleep(1.2)
        return {"success": True, "killed": killed, "elevated_needed": elevated_needed}

    def cleanup(self):
        for srv in self.servers.values():
            if srv.process is not None:
                srv.stop()

# Backward compatibility alias
MSEMAXServerManager = MultiServerManager

