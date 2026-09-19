---
name: matlab-batch-runner
description: 以 headless 方式驱动 MATLAB（matlab -batch 或 Python 常驻引擎）执行 .m 脚本或代码片段，拿回真实输出。当用户要求跑 MATLAB、复现论文算法、做参数扫描/扫参、处理 .mat 文件、批量出图、把仿真结果汇总成表、或调试跑不通的 .m 代码时使用。也用于先探测本机 MATLAB 版本与可用工具箱。
agent_created: true
---

# MATLAB headless 驱动

让模型能**真的把 MATLAB 跑起来并拿到结果**，而不是只写出一堆没人验证过的代码。
核心闭环：**写 .m → 执行 → 读输出 → 修正 → 再执行**。

## 第 0 步：先探测本机环境（必做，不要猜）

不同机器的 MATLAB 路径和**工具箱授权**差别极大。写任何 .m 代码之前先跑：

```bash
PYTHON skills/matlab-batch-runner/scripts/run_matlab.py \
  --code "disp(['VERSION: ' version]); disp(['RELEASE: ' version('-release')]); v=ver; for k=1:numel(v); disp([v(k).Name ' | ' v(k).Version]); end"
```

**工具箱清单决定了你能写什么代码。** 缺了工具箱就会直接报 `Unrecognized function`。
常见的坑：

| 缺失的工具箱 | 后果 | 替代方案 |
|------|------|---------|
| **Parallel Computing** | **没有 `parfor`**，扫参不能并行 | 串行循环，或用 Python 起多进程各跑一段区间 |
| Symbolic Math | 不能 `syms` / `dsolve` | 用 Python `sympy`，或手推 |
| Statistics / ML | 没有 `fitlm`、`fitrgp` | 数据分析走 Python |
| Signal Processing | 没有 `pwelch`、滤波器设计工具 | Python `scipy.signal` |
| Global Optimization | 只有局部优化 | `fmincon` 多起点撒 |
| Deep Learning | 不能训网络 | 训练走 Python |

**把探测结果写进技能或项目备忘**，下次不用重跑，也能避免写出用不了的代码。

## 跑法

```bash
PY="python"   # 换成你的解释器绝对路径
SK="skills/matlab-batch-runner/scripts/run_matlab.py"

# 跑代码片段
"$PY" "$SK" --code "disp(version)"

# 跑 .m 文件
"$PY" "$SK" --file analysis.m

# 跑 .m 并预置变量（扫参常用）
"$PY" "$SK" --file sweep.m --vars "gap=0.5,thick=3"

# 长时间仿真 + 结构化输出
"$PY" "$SK" --file sim.m --workdir "D:/proj" --timeout 3600 --json
```

脚本会按 `MATLAB_EXE` 环境变量 → 各盘 `Program Files/MATLAB/*` 的顺序自动定位
最新的 `matlab.exe`；也可用 `--matlab` 显式指定。**找不到时报错信息里会写明怎么覆盖。**

## 常驻引擎：需要反复迭代时用它

一次性批量任务用 `run_matlab.py` 就够了。但 **MATLAB 冷启动很贵**（实测约 25s），
需要反复交互调试时应该装 **MATLAB Engine for Python**，常驻一个进程：

```bash
python -m pip install "<MATLAB_ROOT>/extern/engines/python"
```

实测对比：

| 调用方式 | 成本 |
|----------|------|
| `matlab -batch` | 冷启动 ≈ **25s / 每次** |
| Python 引擎（常驻） | 启动 **16s 一次**，之后 **0.14s / 每次** |

**差了两个数量级。** 用法：

```python
import matlab.engine
eng = matlab.engine.start_matlab()              # 16s 一次
print(eng.version())
eng.eval("max(sin(0:0.01:2*pi))", nargout=1)    # 0.14s
nums = matlab.double([1.0, 4.0, 9.0])           # 数组直传，不用落盘
eng.sqrt(nums)
eng.workspace["a"] = 3.0                        # 工作区变量读写
eng.quit()
```

注意 MATLAB 官方只支持特定 Python 版本（如 R2026a 支持 3.9–3.13）。
装之前先看 `<MATLAB_ROOT>/extern/engines/python/setup.py` 里的 `_supported_versions`，
版本不匹配会直接报错。

用 `scripts/verify_engine.py` 可以验证引擎是否可用、并复测上述性能数字。

## 写 .m 代码的硬约束

1. **必须把结果 `disp` / `fprintf` 出来。** headless 模式看不到 workspace，
   不打印就等于没结果。复杂结构用 `jsonencode` 或 `writematrix` 落盘再让 Python 读。
2. **不要依赖 GUI。** `-batch` 模式下 `figure` 不弹窗。出图必须显式存盘：
   ```matlab
   f = figure('Visible','off');
   plot(x, y, 'LineWidth', 1.5);
   exportgraphics(f, 'out.pdf', 'ContentType', 'vector');  % 论文级矢量图
   close(f);
   ```
   用 `exportgraphics`（R2020a+），不要再用 `saveas`。
3. **错误要能被看到。** `-batch` 下未捕获异常会让 exit code 非 0，stderr 里有堆栈。
   `try/catch` + `disp(getReport(err))` 能给更可读的诊断。
4. **冷启动是固定成本。** 反复小步调试时把多步合并进一个脚本一次跑完，
   不要拆成十几次调用。
5. **`.mat` 与 Python 互操作**：Python 侧 `scipy.io.loadmat` / `savemat`。
   注意 MATLAB 默认 v7 格式（跨版本兼容性好）；`-v7.3` 是 HDF5，体积小但 scipy 读起来麻烦。

## Windows 环境注意

某些打包的 Windows 环境里 **bash 的 PATH 是坏的**：`mkdir` / `cat` / `head` / `grep`
都不存在，而且**不能接管道**（读端不存在会让 Python 首个 `print` 抛
`BrokenPipeError` 直接中断脚本）。

所以：**建目录、跑 MATLAB、过滤输出，全部交给 Python**，不要在 shell 里拼管道。
MATLAB 用绝对路径调用。

## 典型可交付场景

- **论文算法复现**：文献里的公式/伪代码 → `.m` → 跑仿真 → 出对比图
- **参数扫描**：逐点扫参 → 汇总成表和图（无 `parfor` 时用 Python 多进程绕）
- **参数辨识**：Curve Fitting / Simulink Design Optimization 从实测数据反推参数
- **控制系统设计**：电流环/速度环设计、PID 整定、Bode 图、根轨迹
- **数据后处理**：`.mat` 读取 → 批量出论文级矢量图 → 生成 LaTeX 表格
- **旧代码提速**：向量化改造，跑前后对比
