---
name: semiconductor-research-direction-collect
description: >-
  全球半导体实验室研究方向采集与洞察系统。
  定期收集全球100+半导体实验室/研究机构/企业R&D中心的最新研究方向，
  进行趋势分析并生成结构化洞察报告，供Hermes智能体消费。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch
---

# Semiconductor Research Direction Collect Skill

## Mission

本 Skill 的核心使命是：**系统化追踪全球半导体实验室的研究方向，识别新兴趋势，生成结构化洞察**。

与传统的半导体新闻采集不同，本系统聚焦于 **研究前沿（Research Frontier）** 而非产业动态（Industry News），关注的是「未来 2-5 年的技术方向」而非「本周的财报与订单」。

## 信息源策略（100+ 实验室）

系统覆盖 6 类信息源，按采集优先级排序：

### Tier 1: 世界级研究机构（每周采集）
| 机构 | 重点领域 |
|---|---|
| imec (比利时) | 先进制程、EUV、GAA、CFET、2D材料、先进封装 |
| CEA-Leti (法国) | FD-SOI、3D集成、硅光子、AI芯片 |
| Fraunhofer IISB/ISIT (德国) | 功率半导体、SiC、先进封装 |
| 斯坦福 Nanofabrication Facility | 纳米制造、新型器件 |
| MIT MTL | 微系统、新型计算架构 |
| UC Berkeley EECS | 电路设计、EDA、新型器件 |
| IMECAS (中科院微电子所) | 先进制程、存储器、化合物半导体 |
| Peking University | 新型器件、AI芯片 |
| Tsinghua University | 存储器、新型计算 |

### Tier 2: 企业R&D中心（每周采集）
| 企业 | 重点领域 |
|---|---|
| Intel Labs | 先进制程、封装、量子计算 |
| TSMC Research | 先进工艺、3D IC、器件物理 |
| Samsung SAIT | 存储器、先进封装、新材料 |
| IBM Research | AI芯片、量子计算、先进封装 |
| NVIDIA Research | AI架构、芯片设计 |
| Google Research | AI芯片、TPU架构 |
| Meta AI Research | AI芯片、网络芯片 |
| Microsoft Research (Silicon) | AI加速器、FPGA |

### Tier 3: 核心学术会议（会期采集）
| 会议 | 领域 |
|---|---|
| IEDM | 器件、工艺技术 |
| ISSCC | 芯片设计、电路 |
| VLSI Symposium | VLSI技术 |
| ASP-DAC | EDA、设计自动化 |
| DAC | 设计自动化 |

### Tier 4: 研究机构联盟（双周采集）
| 机构 | 重点领域 |
|---|---|
| SEMI Research | 行业数据、路线图 |
| SIA | 产业政策、统计 |
| Yole Group | 封装、化合物半导体 |
| TechInsights | 工艺分析、反向工程 |
| TrendForce | 存储器、Foundry |

### Tier 5: 高质量技术博客/个人研究者（双周采集）
| 博客 | 领域 |
|---|---|
| SemiAnalysis | AI芯片、HBM、先进封装深度分析 |
| Fabricated Knowledge | 技术+商业交叉分析 |
| Asianometry | 半导体历史与机制解释 |
| The Chip Letter | 芯片架构历史 |
| ChipsandCheese | 处理器微架构评测 |

### Tier 6: 官方新闻（月度深度采集）
- 各实验室官网 Research/Publication 页面
- arXiv（半导体相关论文预印本）
- IEEE Xplore / ACM DL 公开内容
- Google Scholar 高引论文追踪

## 管道（Pipeline）定义

每次采集运行分为 3 个阶段：

### Phase 1: 采集（Collect）
- 根据指定实验列表和采集密度，访问各实验室研究信息页面
- 提取最新论文标题、摘要、研究方向关键词
- 保存原始 HTML + 结构化 JSON
- 输出到 `artifacts/{date}/articles/`

### Phase 2: 分析（Analyze） 
- 对采集到的研究内容进行方向聚类
- 跨实验室交叉验证趋势（同一方向出现在多家实验室 → 置信度提升）
- 标注研究方向生命周期阶段: `emerging | growing | mature | declining`
- 输出到 `artifacts/{date}/analysis/`

### Phase 3: 报告（Report）
- 生成结构化的研究方向洞察报告
- 包含: 趋势总结、方向地图、技术成熟度评估、跨机构对标
- 双格式输出: Markdown（人类可读）+ JSON（Hermes 可消费）

## 研究标签体系

每个研究方向使用以下标签体系标注：

```yaml
direction:
  name: "背面供电网络 (BSPDN)"
  lifecycle: "emerging"        # emerging | growing | mature | declining
  domain: "advanced_process"   # 所属领域
  labs: ["imec", "intel-labs", "tsmc-research"]
  evidence:
    - paper_title: "..."
      lab: "imec"
      url: "https://..."
      published_at: "2026-05"
    - paper_title: "..."
      lab: "intel-labs"
      url: "https://..."
      published_at: "2026-04"
  confidence: 0.85             # 0.0 - 1.0
  summary: "背面供电网络通过将供电网络移至晶圆背面，释放正面信号路由资源..."

domains:
  - advanced_process           # 先进制程 (GAA, CFET, BSPDN, EUV)
  - advanced_packaging         # 先进封装 (Hybrid Bonding, 3D-stacking)
  - memory_technology          # 存储器技术 (HBM, CXL, MRAM, FeRAM)
  - ai_chip_architecture       # AI芯片架构 (DSA, Neuromorphic, In-memory)
  - eda_design_automation      # EDA设计自动化
  - semiconductor_materials    # 半导体材料 (SiC, GaN, 2D Materials)
  - quantum_computing          # 量子计算
  - chiplet_interconnect       # Chiplet与互联 (UCIe, BoW)
  - photonics                  # 硅光子学
  - manufacturing_equipment    # 制造装备与工艺
  - reliability_test           # 可靠性与测试
  - security                   # 硬件安全
```

## 核心工具接口

以下 4 个工具对外暴露，供 Hermes 智能体调用：

### tool-collect
采集指定实验室的最新研究方向：
```json
{
  "tool": "collect_research_directions",
  "args": {
    "labs": ["imec", "intel-labs", "mit-mtl"],
    "mode": "weekly",
    "max_per_lab": 10
  }
}
```

### tool-analyze
分析已采集的研究数据，识别趋势：
```json
{
  "tool": "analyze_research_trends",
  "args": {
    "date": "2026-06-02",
    "min_confidence": 0.6,
    "domains": ["advanced_process", "ai_chip_architecture"]
  }
}
```

### tool-report
生成研究方向洞察报告：
```json
{
  "tool": "generate_insight_report",
  "args": {
    "date": "2026-06-02",
    "format": "both",
    "focus": "AI芯片架构",
    "include_labs": ["imec", "intel-labs", "nvidia-research"]
  }
}
```

### tool-collect-and-report
端到端：采集 + 分析 + 报告一步完成：
```json
{
  "tool": "collect_and_report",
  "args": {
    "labs": ["imec", "stanford-nanolab", "tsmc-research", "ibm-research"],
    "mode": "weekly",
    "focus": "先进制程与封装"
  }
}
```

## 输出 Schema (Hermes 消费格式)

每份洞察报告使用以下 JSON Schema：

```json
{
  "report_meta": {
    "title": "2026年6月第1周半导体研究方向洞察",
    "generated_at": "2026-06-02T12:00:00Z",
    "collection_date": "2026-06-02",
    "labs_covered": 25,
    "articles_collected": 120
  },
  "top_trends": [
    {
      "direction": "背面供电网络 (BSPDN)",
      "lifecycle": "emerging",
      "score": 0.92,
      "labs_active": ["imec", "intel", "tsmc", "samsung"],
      "key_insight": "BSPDN 正在从学术研究进入工业量产准备阶段...",
      "evidence": [...]
    }
  ],
  "domain_summary": {
    "advanced_process": {"total": 12, "emerging": 3, "growing": 5},
    "advanced_packaging": {"total": 8, "emerging": 2, "growing": 4}
  },
  "lab_activity": [
    {"lab": "imec", "article_count": 15, "top_direction": "CFET"},
    {"lab": "intel-labs", "article_count": 8, "top_direction": "BSPDN"}
  ],
  "cross_reference": {
    "notes": "以下方向在多实验室之间出现交叉研究...",
    "convergences": [
      {"direction": "Hybrid Bonding", "labs": ["imec", "tsmc", "intel", "samsung"], "strength": "strong"}
    ]
  }
}
```

## 拒绝列表（不采集的内容）

以下内容类型不予采集：
- 企业财报/营收数据
- 股票/投资分析
- 招聘信息
- 会展通知
- 产品促销/白皮书营销页面
- 付费墙后的完整文章（仅采集公开摘要）

## 质量门禁

一次成功的采集运行必须通过以下检查：

1. **采集门**: 每个目标实验室至少找到 1 篇真实研究内容（非首页/列表页）
2. **结构化门**: 每篇文章必须包含标题、摘要、研究方向标签
3. **分析门**: 至少识别出 3 个明确的研究方向聚类
4. **报告门**: 同时输出 JSON 和 Markdown 格式报告
5. **引用门**: 每个趋势判断必须有 ≥2 个独立来源交叉验证

## 失败升级路径

- **目标页无法访问**: 降级到 WebSearch → 提取公开摘要
- **找不到研究内容**: 尝试实验室 Google Scholar 页面
- **付费墙**: 仅提取公开标题和摘要，标记 paywalled=true
- **研究方向无法分类**: 归入 "uncategorized"，由分析阶段处理
