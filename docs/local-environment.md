# 本机环境备忘（不上传，已被 .gitignore 排除）

> 这份文件只在本机保留，记录了具体的安装路径和授权情况。
> 仓库里的技能是**通用版**，靠自动探测 + 环境变量工作，不含这些个人路径。

记录时间：2026-09-19

---

## MATLAB

- 安装位置：`E:\Program Files\MATLAB\R2026a\bin\matlab.exe`
- 版本：R2026a（`26.1.0.3346908` Update 5）
- 冷启动耗时实测：`matlab -batch` 约 **25.4s**

### 已授权的工具箱

Control System · Curve Fitting · MATLAB Coder · Optimization · Simscape ·
**Simscape Electrical** · Simscape Multibody · Simulink · Simulink Coder ·
**Simulink Design Optimization** · Stateflow · **Vehicle Dynamics Blockset**

### 缺失的工具箱（写 .m 之前必须避开）

| 缺失 | 后果 |
|------|------|
| **Parallel Computing** | **没有 `parfor`，扫参不能并行** |
| Symbolic Math | 不能 `syms`，符号推导走 Python `sympy` |
| Statistics / ML | 没有 `fitlm` / `fitrgp`，数据分析走 Python |
| Signal Processing | 没有 `pwelch` / 滤波器设计工具，走 `scipy.signal` |
| Global Optimization | 只有 `fmincon` 局部优化，需多起点 |
| Deep Learning | 不能训网络 |

---

## Python

- 托管解释器：`C:\Users\30463\.workbuddy\binaries\python\versions\3.13.12\python.exe`
- 隔离 venv：`C:\Users\30463\.workbuddy\binaries\python\envs\default`
  - Python 3.13.14，已装 `matlabengine 26.1`
- 系统 Python：`E:\Program Files\Python312\python.exe`（3.12.6）

### MATLAB Engine for Python 实测

| 调用方式 | 成本 |
|----------|------|
| `matlab -batch` | 25.4s / 每次 |
| 常驻引擎 | 启动 **16.4s 一次**，之后 **0.14s / 每次** |

连续 3 次调用总耗时 0.41s。装法：

```bash
"C:\Users\30463\.workbuddy\binaries\python\envs\default\Scripts\python.exe" \
  -m pip install "E:/Program Files/MATLAB/R2026a/extern/engines/python"
```

R2026a 官方支持 Python 3.9–3.13。

---

## 其他软件（不在 C 盘）

| 软件 | 路径 |
|------|------|
| CATIA V5R21 | `E:/CATIA1/intel_a/`（Automation 接口可用 pycatia） |
| AutoCAD 2027 | `E:/Program Files/Autodesk/AutoCAD 2027`（含 Interop.dll，COM 可自动化） |
| CarSim 2019 | `E:/Program Files (x86)/CarSim2019.0_Prog` |
| Motor-CAD 2024 R1 | `E:/Program Files/ANSYS Inc/MOTORCAD24R1/`（已非主力） |

**找软件不要按默认 C 盘路径猜，实际都在 E 盘。**
扫目录名关键词（ansys / dassault / autodesk / matlab / catia），深度限 2 层即可；
递归 glob 整盘会超时。

---

## 本机 bash 工具的限制

某些打包环境里 bash 的 PATH 是坏的：`mkdir` / `cat` / `head` / `grep` / `tee` 都不存在，
而且**不能接管道**（读端不存在会让 Python 首个 `print` 抛 `BrokenPipeError` 中断脚本）。

→ 建目录、读文件、过滤输出全部交给 Python，不要在 shell 里拼管道。

---

## 未决事项

- 本机 **git 没有配置凭据**（`credential.helper` 为空，无 `.git-credentials`），
  所以本地 `git push` 走不通，本仓库是通过 GitHub 接口推送的。
  要用本地 git 管理需先配置凭据（Git Credential Manager 或 PAT）。
