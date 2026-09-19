# 想法查重报告 —— GitHub 先例检索

**检索时间**：2026-09-19
**检索方式**：GitHub 公共 Search API（匿名额度）· 仓库名/描述 + 相关性排序
**检索清单来源**：本次工作区之前几轮对话中你提出过的工具/项目想法（历史会话标题回捞）

> 说明：本轮走的是**匿名公共接口**，只能检索公开仓库的名称与描述。
> 接入 GitHub 授权后，还可以做 **代码级搜索**（搜实现细节、搜 README 正文）、**Issue/Discussion 搜索**（看有没有人踩过同样的坑）、以及 clone 下来实测。

---

## 总览结论

| # | 想法 | 前人做过吗 | 成熟度 | 建议 |
|---|------|-----------|--------|------|
| A | 手写签名照片 → 矢量签名 | ⚠️ 几乎没有 | 空白 | **值得自己做**，已领先 |
| B | 截图/图片去水印去元素 | ✅ 大量 | 很成熟 | 直接选型复用 |
| C | 截图文字清晰化 / 去阴影 | 🟡 学术多、成品少 | 半空白 | 组合现成件 |
| D | 表格截图 → 可编辑表格 | ✅ 有专门库 | 成熟 | 直接用 img2table |
| E | 学习路线 / 学习计划生成 | ⚠️ 只有玩具级 | 空白 | **skill 形态是差异化点** |
| F | Agent 上下文 / 记忆管理 | ✅ 非常卷 | 红海 | 需要找差异点 |

---

## A. 手写签名照片 → 矢量签名

**结论：没人正经做过成品。** 这是你最"干净"的一个想法。

搜索 `signature vectorization` / `handwriting signature svg trace` 命中 151 条，但**没有一条**是"把签名照片处理成可插入文档的矢量签名"这件事：

- `GJNilsen/YPDrawSignatureView` ⭐308 [Swift] —— iOS 端的签名**绘制**控件，导出矢量或位图。是「在 App 里手写」，不是「处理已有的签名照片」。
- `fromtheexchange/image2svg-awesome` ⭐378 —— 位图转 SVG 的**资源集合**，不是成品方案。
- 其余命中全是无关的（区块链签名向量、RISC-V 向量指令、联合国矢量瓦片 logo 等）。

**可借鉴的**：通用位图矢量化引擎是现成的地基 —— VTracer（支持彩色、比 potrace 快）、potrace（你本地已在用）、以及 image2svg 那批在线/命令行工具。

**判断**：从「签名照片」到「能插进 Word 的透明底矢量签名」，中间那段（去格线、去背景、笔画粗细归一、孔洞方向处理）才是真正的活儿，而 GitHub 上没人做这段。你现有的 `handwriting-signature-vectorize` 脚本在这个空白区里是领先的，可以考虑整理成开源项目。

---

## B. 截图 / 图片去水印、去元素

**结论：非常成熟的红海，不要自己写。**

| 仓库 | Star | 说明 |
|------|------|------|
| `T8RIN/ImageToolbox` | ⭐14668 | Kotlin 安卓图像工具箱，功能覆盖去水印、去元素等几十项 |
| `zuruoke/watermark-removal` | ⭐5171 | 经典方案，图像修复(inpainting)思路去水印，效果好到难以分辨 |
| `allenk/GeminiWatermarkTool` | ⭐3109 | 反向 alpha 混合，专门去 Gemini 生成图的水印，离线 C++ GUI/CLI，支持批量 |
| `D-Ogi/WatermarkRemover-AI` | ⭐1954 | Florence-2 + LaMA，图片和视频都能去，含 AI 生成水印 |
| `marcbelmont/cnn-watermark-removal` | ⭐1270 | 全卷积网络去透明叠加层，老牌 |
| `braindotai/Watermark-Removal-Pytorch` | ⭐1149 | Deep Image Prior + PyTorch 的 CNN 去水印 |
| `ziweipolaris/watermark-removal` | ⭐355 | 水印减除思路去视频水印，快但不完美 |
| `vinthony/deep-blind-watermark-removal` | ⭐258 | AAAI 2021 论文实现 |
| `m3at/video-watermark-removal` | ⭐211 | 极简配置去视频水印 |

**判断**：需求明确、方案很多，按「图片 or 视频」「本地 or 在线」「要不要 GUI」三选一即可。

---

## C. 截图文字清晰化 / 文档去阴影

**结论：学术侧活跃，工程化成品极少 —— 半空白。**

搜索 `document shadow removal enhancement` 全库只命中 4 条，且都是数据集和论文复现：

- `liuyifan6613/DocBank-Document-Enhancement-Dataset` ⭐50 —— 文档图像增强数据集，覆盖**印章检测&移除、水印检测&移除**等任务，标注数据可以直接用。
- `llgnll/WSRNet-...` ⭐0 —— 小波去阴影网络，论文代码。
- `weinixuehao/Document-Scanning-Demo` ⭐0 —— 文档扫描 demo，含去阴影和外观增强。
- `johnnyhoang/smart-doc-scanner` ⭐0 —— 自托管网页版扫描器，含透视校正、页面去扭曲、去阴影。

**判断**：这块没有"开箱即用"的好东西。现实路线是 **OCR 引擎（如 docTR）+ 传统图像增强**拼装，而不是等现成方案。是你几个想法里技术难度最高、也最不容易被现成轮子替代的一个。

---

## D. 表格截图 → 可编辑表格

**结论：有专门的开源库，可以直接用。**

- `xavctn/img2table` ⭐900 [Python] —— **最贴你需求的一个**：基于 OpenCV 的表格识别与抽取库，同时支持 PDF 和图片，本地跑、可脚本化。
- `jainammm/TableNet` ⭐325 —— TableNet 论文的非官方实现，端到端表格检测 + 表格结构识别。
- `Sudhanshu1304/table-transformer` ⭐103 —— OCR + 计算机视觉组合的表格抽取工具，最接近"截图→Excel"整条链路。
- `fazlurnu/Text-Extraction-Table-Image` ⭐149 —— 表格图像文字抽取。
- `abdullahibneat/TableExtraction` ⭐59 —— 基于表格线的检测框架，输出 JSON。
- ComPDFKit 系列（`-windows` / `-mac` / `-android`）⭐~110 —— **商业 SDK**，PDF→Word/Excel/PPT/HTML，Windows 版可直接调用。适合要交付质量而不是自己调参的场景。
- 另有若干 PDF→Excel 的小工具（`Kurama-90/GUI-PDF-to-Excel` 等），Star 都在个位数。

**判断**：`img2table` 做底层，必要时叠 `table-transformer` 补结构识别，基本能覆盖你的"仿制 Excel 表格"需求。

---

## E. 学习路线 / 学习计划生成

**结论：只有玩具级项目，没有成熟品。你的 skill 形态反而是差异化点。**

| 仓库 | Star | 说明 |
|------|------|------|
| `dungnotnull/language-learning-spaced-repetition-agent-skill` | ⭐4 | 间隔重复算法生成 CEFR 对齐语言学习路线，**以 agent skill 形态存在** —— 形态上最接近你的做法 |
| `Huzaifa-X/AI-Powered-Study-Planand-Book-Summarization` | ⭐8 | 学习计划 + 书籍摘要 |
| `k0msenapati/study-buddy` | ⭐7 | AI 学习计划与建议生成 |
| `Nancyberry/ebbinghausGenerator` | ⭐5 | 艾宾浩斯遗忘曲线排学习计划，纯 Python，算法思路可借鉴 |
| `victorjatoba/aspga` | ⭐4 | 遗传算法排学习计划 |
| `AnanyaKolekar/MultiAgent_StudyPlanner` / `B3bea/AI-Study-Planner` / `Gauthami2005/Agentix` | ⭐0 | 多智能体学习计划，含 LangGraph + MCP 版本 |

**判断**：整个赛道 Star 数都在个位数，说明**没人把这件事做透**。真正缺的不是"生成一份计划表"，而是**可验证的里程碑 + 进度追踪 + 按反馈调速**。你现有的 learning-planner / study-planner 的"分阶段 + 验收标准 + 加速/降速"闭环，正好补的是这个缺口。`ebbinghausGenerator` 的复习曲线算法值得吸收进来。

---

## F. Agent 上下文 / 记忆管理

**结论：红海，同类非常多，需要找差异点。**

- `alioshr/memory-bank-mcp` ⭐922 —— MCP 远程记忆库管理，受 Cline 启发
- `GreatScottyMac/context-portal` ⭐766 —— 为项目构建专属知识图谱的记忆库 MCP
- `CheMiguel23/MemoryMesh` ⭐353 —— 知识图谱式结构化记忆持久化
- `mordang7/ContextKeep` ⭐156 —— AI Agent 的无限长期记忆
- `mkreyman/mcp-memory-keeper` ⭐135 —— 编码助手的持久上下文管理

**判断**：这个方向的 MCP Server 已经卷得很厉害了。如果 PowerContext 要做，差异化得落在具体场景上（比如"跨会话的项目交接"），而不是再做一层通用记忆库。

---

## 下一步

1. **接入 GitHub 授权** —— 之后可以做代码级搜索（现在只能搜仓库名和描述，很多实现细节搜不到）、搜 Issue 看别人的踩坑记录、clone 下来实测。
2. **补充想法清单** —— 上面 6 条是我从历史对话里回捞的。如果你脑子里还有没提过的想法，直接发给我，我按同样流程查一遍。
3. **优先深挖** —— 建议先深挖 A（签名矢量化）和 E（学习规划），这两个是真正的空白区，有做成开源项目的价值；B/D 直接选型复用即可。
