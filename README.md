# Agent Skills

给 AI 智能体用的技能包。技能是「说明书 + 脚本」的组合——把某个目录整个复制到 AI 工具的技能目录下即可生效。

本仓库以 **MATLAB 自动化**为主,另附一个通用的 GitHub 先例查重技能作为示例。

---

## 为什么值得沉淀技能,而不是自建一个 agent

Agent 的能力来自**模型 + 工具**。自己搭一个 agent 外壳不会让它变强,而模型迭代很快,外壳会持续腐烂。

但技能不一样:它是**纯文本资产,可迁移**。今天给某个 AI 工具写的技能,明天换任何框架都能直接搬过去用。

> 沉淀技能不是绑定某个产品,是在给未来的自己攒资产。

---

## 技能清单

### `matlab-batch-runner` —— 让智能体真的能跑 MATLAB

**解决的问题**:大多数时候 AI 只能给你一段"看起来对"的 MATLAB 代码,没人验证过。
这个技能建立闭环:**写 `.m` → 执行 → 读输出 → 修正 → 再执行**,拿回真实结果。

核心能力:
- 以 headless 方式驱动 MATLAB(`matlab -batch`),捕获 stdout,拿到真实执行结果
- 支持参数扫描时预置变量、指定工作目录、设置超时
- 论文级矢量出图(`exportgraphics` 导出 PDF)
- 自动探测 MATLAB 安装位置,支持 `MATLAB_EXE` 环境变量覆盖

**实测性能对比**(在作者的机器上验证):

| 调用方式 | 成本 |
|----------|------|
| `matlab -batch` | 冷启动约 **25s / 每次** |
| MATLAB Engine for Python(常驻) | 启动 **16s 一次**,之后 **0.14s / 每次** |

所以:**一次性批量任务**用 `run_matlab.py`;**需要反复迭代调试**(算法复现、逐步调参)
用常驻引擎——差了两个数量级。

### `github-idea-prior-art-scan` —— 先例查重

把一批想法拿到 GitHub 上检索「有没有人做过、做到什么程度、要不要自己造轮子」。

核心方法是**三层递进**:仓库层 → **代码层** → 社区层。

关键技巧:代码搜索必须用**带引号的精确短语**。
实测同一个想法不加引号命中 3520 条(全是无关结果),加引号后**只剩 11 个文件**。

---

## 使用前提

1. **Python 3.9+**(脚本本身只需要标准库)
2. **MATLAB**(仅 `matlab-batch-runner` 需要),已激活相应工具箱
3. 首次使用前,先跑探测命令确认你的 MATLAB 路径和工具箱:

```bash
python skills/matlab-batch-runner/scripts/run_matlab.py \
  --code "disp(version); v=ver; for k=1:numel(v); disp([v(k).Name ' | ' v(k).Version]); end"
```

**重要**:不同授权版本的工具箱差别很大。写 `.m` 代码前先确认工具箱是否可用,
否则会直接报 `Unrecognized function`。常见的坑:
- 没有 **Parallel Computing Toolbox** → **`parfor` 用不了**,扫参只能串行或用多进程绕
- 没有 **Symbolic Math Toolbox** → 不能 `syms`
- 没有 **Statistics / Signal Processing / Deep Learning** → 数据分析走 Python

---

## 目录结构

```
.
├── skills/
│   ├── matlab-batch-runner/
│   │   ├── SKILL.md              # 技能说明书
│   │   └── scripts/
│   │       ├── run_matlab.py     # 一次执行一个脚本/代码片段
│   │       └── verify_engine.py  # 检查常驻引擎是否可用
│   └── github-idea-prior-art-scan/
│       ├── SKILL.md
│       └── scripts/
│           └── scan.py           # 批量检索
├── docs/
│   ├── github-usage-guide.md     # GitHub 授权前后能力分层与用法
│   └── ppt-skills-summary.md     # PPT 技能汇总
└── .gitignore
```

> 仓库里是**通用版**:不含任何个人环境路径。
> 个人环境信息(具体安装位置、工具箱授权情况)记录在本地 `docs/local-environment.md`,
> 该文件已被 `.gitignore` 排除。

---

## 安装到你的 AI 工具

把 `skills/<技能名>/` 整个目录复制过去即可。常见位置:

- 用户级:`~/.workbuddy/skills/`
- 项目级:`<项目>/.workbuddy/skills/`

复制后重启会话,技能即生效。

---

## 环境备忘(Windows)

如果你在 Windows 上跑这些脚本,注意:

- **不要依赖 bash 的 `mkdir` / `cat` / `head` / `grep`**——某些打包环境里这些命令不可用。
  建目录、读文件、过滤输出都交给 Python,并且**不要接管道**。
- 写完脚本把结果 `print` 出来即可,不要 `| head`。
- MATLAB 用绝对路径调用,例如 `"C:/Program Files/MATLAB/R2026a/bin/matlab.exe"`。

---

## License

MIT
