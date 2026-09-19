---
name: github-idea-prior-art-scan
description: 把用户的想法批量拿到 GitHub 上做「先例查重」——检索有没有人做过、做到什么程度、要不要自己造轮子。当用户说「这个想法 GitHub 上有没有人做过」「先查查有没有现成的」「别重复造轮子」「帮我看看这个方向的开源现状」，或让你评估一个工具/项目想法的可行性前，使用此技能。
agent_created: true
---

# GitHub 想法查重（Prior-Art Scan）

用户提出一个或一批想法 → 输出一份「有没有人做过 / 成熟度 / 要不要自己做」的判断报告。

**价值不在"搜到几个仓库"，而在给出选型结论**：空白区自己做、成熟区直接复用、半空白区拼装。

## 一、核心方法：三层递进

**仓库名和描述是作者自己写的，经常跟实际功能差很远或干脆没写；代码正文不会骗人。**
所以不要只搜一遍仓库就下结论。**能拿到授权/CLI 时，必须走到第二层。**

| 层 | 手段 | 回答什么 |
|----|------|---------|
| 1 仓库层 | `search_repositories` | 有没有人做过 |
| 2 **代码层** | `search_code` | 有人真的写出实现了吗（排除"占了名字没写代码"的） |
| 3 社区层 | `search_issues` | 做过的人卡在哪了 |

**第三层常常最值钱**：一个想法如果有人试过、issue 区一堆没解决的问题，说明这是硬骨头，
用户上手前必须先知道坑在哪。这比"有没有人做过"有用得多。

### 代码层的关键技巧：精确短语必须加引号

实测同一想法、同一引擎的对比：

| 检索式 | total_count | 可用性 |
|--------|------------|--------|
| `signature potrace svg` | 3520 | 泛词淹没，结果几乎全无关 |
| `"handwritten signature" svg vectorize` | **11** | 收敛到可逐个判读 |

**判断"是不是空白区"，靠的就是这个引号。** 没有引号的数字毫无意义，
不要拿 3520 去说明"这块很卷"。

其他限定符：`repo:` / `org:` / `user:` / `language:` / `path:` / `filename:` /
`extension:` / `is:archived`，以及 `OR` / `NOT`。
想看某个库的实现细节，配合读取文件接口直接读，比整库 clone 快得多。

## 二、先探测环境（不要假设）

三条路径，按可用性优先选：

1. **已有 GitHub 集成**（连接器 / MCP 工具）→ 最优先，支持代码层与社区层检索。
2. **有 `gh` CLI 且已登录** → `gh search repos` / `gh search code` / `gh search issues`，效果同上。
3. **都没有** → 走匿名 REST API（见下），只能查公开仓库的名称+描述，
   **查不到代码正文和 Issue**。这必须写进报告，否则用户会以为你已经搜过实现细节。

连通性先测 `https://api.github.com/rate_limit`。**别照搬"本机有代理会挡"之类的历史结论，实际探测。**

## 三、匿名检索的正确姿势

```python
import urllib.request, urllib.parse, json
import socket
socket.setdefaulttimeout(20)

def gh_search(q, n=6):
    u = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&per_page={n}"
    req = urllib.request.Request(u, headers={
        "User-Agent": "prior-art-scan",
        "Accept": "application/vnd.github+json",
    })
    return json.load(urllib.request.urlopen(req))["items"]
```

**三条硬约束（踩过的坑）**：

1. **额度**：匿名 core 60/小时、**search 10/分钟**。超了直接 `HTTP 403 rate limit exceeded`。
   批量检索时两次调用之间 `time.sleep(7~8)`；被 403 后先 `time.sleep(68)` 再继续。
   想一口气跑十几条查询就必须分批 + 等待，别指望一次跑完。
2. **绝对不要加 `sort=stars`**。多词查询在 readme 里近似 OR 匹配，按 star 排会让
   `awesome-python`、`awesome-selfhosted` 这类通用清单霸占全部结果位。
   **默认走相关性排序，并限定 `in:name,description`。**
3. **关键词不要堆太多**。AND 语义下 `handwriting signature svg trace` 会命中 0 条。
   用 2~3 个词，命中少就拆开换说法，**同一个想法准备 2~3 个不同检索式**。

## 四、跑法

```bash
python scripts/scan.py            # 内置示例清单
python scripts/scan.py queries.txt
```

`queries.txt` 每行一条：`标签<TAB>检索式` 或 `标签 | 检索式`，`#` 开头为注释。
脚本内置节流、403 冷却重试、噪音过滤（awesome 清单等）、按标签分组输出。

**授权后不必用这个脚本**，直接调集成工具即可，能拿到更准的三层结果。

## 五、输出规范

写一份 Markdown 报告（文件名带日期），结构：

1. **检索方式与局限**——说清是匿名仓库级还是授权代码级
2. **总览结论表**：想法 / 前人做过吗 / 成熟度 / 建议 —— 一眼能看完的表是全文最重要的部分
3. **每个想法一节**：命中仓库表格（仓库 / star / 说明）→ 剔除噪音的说明 → 一段判断
4. **下一步**：接入授权能解锁什么、哪些值得深挖、哪些直接复用

判断口径固定三档：

- ✅ **成熟**：有 500+ star 的专门项目 → 直接选型复用，别自己写
- 🟡 **半空白**：只有论文复现、数据集、0~100 star 的 demo → 拼装现成组件
- ⚠️ **空白**：检索不到任何对得上的项目 → 值得自己做（**这是最有价值的发现，要明确说出来**）

结果里出现明显跑偏的（awesome 清单、同名无关项目）要**主动剔除并在报告里说明为什么**，
别把噪音当发现。若命中结果含政治敏感内容，直接跳过，不呈现、不引用。

## 六、顺带产出（用户往往没明说但真正想要的）

检索完别停在"有没有人做过"。用户接着通常会问：

- **选型**：这几个库哪个还在维护 → 看 commit / release 节奏，**star 数最没参考价值**
- **抄作业**：读最接近那个库的源码，把关键几十行扒出来，别让他整库装进来
- **避坑**：翻 issue 看已知问题
- **开源**：如果结论是空白区，可以提议把他自己的东西发上去（**写操作，先确认**）

## 七、边界

- 建仓库、push、提 PR、发 issue 属于**写操作**，必须先跟用户说清楚并等确认；只读检索直接做。
- 结论要说明**检索深度**：只搜了仓库名/描述就不能说"绝对没人做过"，
  最多能说"仓库层面没找到"。搜过代码层和 issue 层才敢下更硬的结论。
