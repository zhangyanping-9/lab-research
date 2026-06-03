# Semi Research Direction Collect

> 全球半导体实验室研究方向采集与洞察系统

**目标**: 定期收集全球 100+ 半导体实验室/研究机构/企业 R&D 中心的最新研究方向，通过结构化分析和洞察提炼，生成可供 Hermes 智能体消费的研究报告。

与传统的半导体新闻聚合（如 [semi-research](https://github.com/pty819/semi-research.git)）不同，本系统聚焦于 **研究前沿（Research Frontier）** ，追踪的是「未来 2-5 年的技术方向」，而非「本周的财报与订单」。

## 系统架构

```
Hermes Agent ──► semi-research-direction-collect (Skill)
                      │
                      ├── 1. collect_research_directions()
                      ├── 2. analyze_research_trends()
                      ├── 3. generate_insight_report()
                      └── 4. collect_and_report()  ← 端到端
```

## 快速开始

### 安装

```bash
uv sync  # 或 pip install -r requirements.txt
```

### Hermes 智能体调用

```python
from src.hermes_bridge import HermesBridge

bridge = HermesBridge()

# 端到端：采集 + 分析 + 报告
result = bridge.collect_and_report(
    labs=["imec", "intel-labs", "mit-mtl", "tsmc-research"],
    mode="weekly",
    focus="先进制程与封装",
    format="both"
)

print(result["report"]["file_paths"])
```

### CLI 使用

```bash
# 端到端
python scripts/collect_and_report.py --labs imec,intel-labs --mode weekly

# 仅采集
python scripts/collect_and_report.py --labs imec,cea-leti --mode weekly --skip-analysis

# 列出可用实验室
python scripts/collect_and_report.py --list-labs

# Hermes JSON 输出
python scripts/collect_and_report.py --labs imec --hermes-output

# 指定领域过滤
python scripts/collect_and_report.py --list-labs --domain ai_chip_architecture
```

## Skill 定义

本仓库提供 Claude Code Skill，路径：

```
.claude/skills/semiconductor-research-direction-collect/SKILL.md
```

在 Claude Code 中可以加载该 Skill 来操作。在 Hermes 智能体环境中，工具定义位于：

```
hermes/tools.json        # Hermes 工具定义 (JSON Schema)
hermes/agent_config.yaml  # Hermes 智能体配置
hermes/prompts/           # 分阶段 Prompt 模板
```

## 信息源覆盖

系统注册表包含 **120+ 信息源**，分为 6 个采集层级：

| 层级 | 类型 | 采集频率 | 数量 | 示例 |
|---|---|---|---|---|
| Tier 1 | 世界级研究机构 | 每周 | ~25 | imec, CEA-Leti, MIT MTL, 北大微电子 |
| Tier 2 | 企业 R&D 中心 | 每周 | ~20 | Intel Labs, TSMC Research, NVIDIA Research |
| Tier 3 | 学术会议 | 会期 | ~10 | IEDM, ISSCC, VLSI Symposium, DAC |
| Tier 4 | 研究机构/联盟 | 双周 | ~15 | SEMI Research, Yole, TrendForce |
| Tier 5 | 技术博客/独立分析 | 双周 | ~15 | SemiAnalysis, Asianometry, ChipsAndCheese |
| Tier 6 | 出版物/arXiv | 月度 | ~5 | arXiv, IEEE Xplore, Google Scholar |

## 产出物

每次采集运行在 `artifacts/{date}/` 下生成：

```
artifacts/{date}/
├── articles/            # 原始采集数据 (JSON)
│   ├── imec/
│   │   ├── article-1.json
│   │   ├── article-2.json
│   │   └── _all.json
│   └── intel-labs/
├── analysis/            # 分析结果
│   ├── trends.json
│   ├── domain_map.json
│   ├── lab_activity.json
│   └── cross_reference.json
└── reports/             # 洞察报告
    ├── semiconductor-research-insight-{date}.json   # Hermes 可消费
    └── semiconductor-research-insight-{date}.md     # 人类可读
```

## 研究方向标签体系

每个研究方向使用以下维度标注：

- **生命周期**: `emerging` → `growing` → `mature` → `declining`
- **置信度**: 0.0 ~ 1.0 (跨实验室来源越多，置信度越高)
- **领域**: advanced_process, advanced_packaging, memory_technology, ai_chip_architecture, eda_design_automation, semiconductor_materials, quantum_computing, photonics, manufacturing_equipment, reliability_test, security, chiplet_interconnect

## Hermes 工具接口

| 工具 | 描述 | 必需参数 |
|---|---|---|
| `collect_research_directions` | 采集指定实验室研究方向 | labs |
| `analyze_research_trends` | 分析趋势 | (可选 date) |
| `generate_insight_report` | 生成洞察报告 | (可选 date) |
| `collect_and_report` | 端到端一体化 | labs |
| `list_available_labs` | 列出可用实验室 | (可选 filters) |

## 示例输出（JSON 报告）

```json
{
  "report_meta": {
    "title": "半导体研究方向洞察报告 2026-06-02",
    "labs_covered": 25,
    "trends_identified": 30
  },
  "top_trends": [
    {
      "direction": "Backside Power Delivery Network (BSPDN)",
      "lifecycle": "emerging",
      "confidence": 0.92,
      "labs_active": ["imec", "intel-labs", "tsmc-research", "samsung-sait"],
      "evidence": [...]
    }
  ],
  "domain_summary": {...},
  "lab_activity": [...],
  "cross_reference": {...}
}
```

## 与 semi-research 的区别

| 维度 | semi-research (参考项目) | 本系统 |
|---|---|---|
| **焦点** | 产业新闻 (财报、订单、市场) | 研究前沿 (论文、技术路线、实验室方向) |
| **信息源** | 80+ 新闻/媒体源 | 120+ 实验室/研究机构/会议 |
| **分析维度** | 重要性排名、分类 | 研究方向聚类、生命周期、跨实验室交叉验证 |
| **输出** | HTML/PDF 双语周报 | JSON (Hermes) + Markdown 洞察报告 |
| **Agent 接口** | Playwright MCP Skill | Hermes 工具定义 + JSON Schema |
