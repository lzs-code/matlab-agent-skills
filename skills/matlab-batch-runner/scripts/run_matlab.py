#!/usr/bin/env python3
"""以 headless 方式驱动 MATLAB，执行 .m 代码或脚本文件，拿回 stdout。

为什么用 Python 而不是直接在 shell 里调 matlab：
- subprocess 能干净地捕获 stdout/stderr、控制工作目录、设置超时；
- 某些 Windows 打包环境里 bash 的 PATH 是坏的（mkdir/cat/head 都不存在），
  且不能接管道，用 Python 可以完全绕开。

用法：
    python run_matlab.py --code "disp(version)"
    python run_matlab.py --file analysis.m
    python run_matlab.py --file sweep.m --vars "gap=0.5,thick=3"
    python run_matlab.py --file sim.m --workdir D:/proj --timeout 3600 --json

环境变量：
    MATLAB_EXE   显式指定 matlab.exe 路径（优先级最高）

注意：MATLAB 冷启动约 25s。批量任务没问题，但不要用它做高频小交互 ——
那种场景请改用常驻的 MATLAB Engine for Python，见 SKILL.md。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

# 兜底路径；正常情况下由 find_matlab() 自动探测
FALLBACK_MATLAB = r"C:\Program Files\MATLAB"


def find_matlab() -> str | None:
    """按 MATLAB_EXE → 各盘 Program Files\\MATLAB\\<版本>\\bin\\matlab.exe 顺序探测。"""
    env = os.environ.get("MATLAB_EXE")
    if env and os.path.isfile(env):
        return env

    if sys.platform == "win32":
        roots = [f"{d}:\\Program Files\\MATLAB"
                 for d in "CDEFG" if os.path.isdir(f"{d}:\\")]
        if os.path.isdir(FALLBACK_MATLAB):
            roots.insert(0, FALLBACK_MATLAB)
        for base in roots:
            if not os.path.isdir(base):
                continue
            # 版本目录倒序 = 优先用最新的
            for rel in sorted(os.listdir(base), reverse=True):
                exe = os.path.join(base, rel, "bin", "matlab.exe")
                if os.path.isfile(exe):
                    return exe
    else:
        from shutil import which
        for name in ("matlab", "octave"):
            hit = which(name)
            if hit:
                return hit
    return None


def build_code(args) -> str:
    """把 --vars 拼到代码前面，让脚本能直接读到变量。"""
    parts = []
    if args.vars:
        for pair in args.vars.split(","):
            pair = pair.strip()
            if not pair or "=" not in pair:
                continue
            name, _, value = pair.partition("=")
            parts.append(f"{name.strip()} = {value.strip()};")
    if args.code:
        parts.append(args.code)
    if args.file:
        target = os.path.abspath(args.file)
        if not os.path.isfile(target):
            raise SystemExit(f"[错误] 脚本不存在: {target}")
        stem = os.path.splitext(os.path.basename(target))[0]
        # 切到脚本所在目录，保证脚本里的相对路径可用
        parts.append(f"cd('{os.path.dirname(target)}');")
        parts.append(f"{stem};")
    if not parts:
        raise SystemExit("[错误] 至少要给 --code 或 --file")
    return " ".join(parts)


def run(code: str, workdir: str, timeout: int, matlab: str) -> dict:
    os.makedirs(workdir, exist_ok=True)
    t0 = time.time()
    try:
        proc = subprocess.run(
            [matlab, "-batch", code],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "elapsed": round(time.time() - t0, 1),
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False, "exit_code": None,
            "elapsed": round(time.time() - t0, 1),
            "stdout": "", "stderr": f"[超时] 超过 {timeout}s 未结束",
        }
    except FileNotFoundError:
        return {
            "ok": False, "exit_code": None, "elapsed": 0.0, "stdout": "",
            "stderr": f"[错误] 找不到 MATLAB: {matlab}",
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="headless 驱动 MATLAB")
    ap.add_argument("--code", help="直接执行的 MATLAB 代码")
    ap.add_argument("--file", help="要运行的 .m 脚本路径")
    ap.add_argument("--vars", help='预置变量，如 "gap=0.5,thick=3"')
    ap.add_argument("--workdir", default=os.getcwd(), help="MATLAB 工作目录")
    ap.add_argument("--timeout", type=int, default=1800, help="超时秒数")
    ap.add_argument("--matlab", default=None, help="matlab.exe 路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    matlab = args.matlab or find_matlab()
    if not matlab:
        print("[错误] 自动探测不到 MATLAB。\n"
              "  请设置环境变量 MATLAB_EXE，或用 --matlab 指定 matlab.exe 的完整路径。\n"
              "  常见位置：C:\\Program Files\\MATLAB\\R20XXx\\bin\\matlab.exe")
        return 2

    code = build_code(args)
    result = run(code, args.workdir, args.timeout, matlab)
    result["matlab"] = matlab
    result["code"] = code

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"matlab: {matlab}")
        print(f"exit={result['exit_code']}  elapsed={result['elapsed']}s")
        print("--- stdout ---")
        print(result["stdout"].rstrip() or "(空)")
        if result["stderr"].strip():
            print("--- stderr ---")
            print(result["stderr"].rstrip())
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
