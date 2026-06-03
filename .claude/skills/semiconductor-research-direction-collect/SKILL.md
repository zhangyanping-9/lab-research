---
name: semiconductor-research-direction-collect
description: >-
  全球半导体实验室研究方向采集与洞察系统。
  覆盖169+信源（53所美国大学+40家企业R&D+33家研究机构），
  支持基础方向统计和深度项目详情两种采集模式，
  生成结构化洞察报告并输出Hermes可消费JSON。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch
---

# Semiconductor Research Direction Collect Skill

## Mission

本 Skill 的核心使命是：**系统化追踪全球半导体实验室的研究方向，识别新兴趋势，生成结构化洞察**。

以美国半导体研究信源为重点（129北美来源），聚焦于 **研究前沿（Research Frontier）** 而非产业动态，关注「未来 2-5 年的技术方向」。

## 两种采集模式

### 基础模式 (basic) — 方向统计
轻量级采集，适合周采/双周采：
- 从实验室研究页提取文章列表
- 关键词自动分类到 12 个 research domains
- 生成统计型趋势报告（方向聚类、生命周期分布）

### 深度模式 (detailed) — 项目详情
重量级采集，适合月采/深度采，每个项目提取：
- 📋 项目概述 (500-2000字)
- 🎯 研究目标列表
- 🔬 技术路线/方法
- 💡 关键创新点
- 👥 研究团队/PI
- 💰 资金来源与规模
- 📅 里程碑时间线
- 📊 技术指标 (node, power, frequency...)
- 📚 相关论文/专利

## 信息源覆盖（169+ 信源）

| 层级 | 类型 | 采集频率 | 数量 | 代表性新增信源 |
|---|---|---|---|---|
| Tier 1 | 大学/研究机构 | 每周 | ~76 | Purdue(SMART USA), Cornell(CNF/SUPREME), UT Austin(TIE/NGMM) |
| Tier 2 | 企业R&D | 每周 | ~40 | Micron, TI, GF Labs, Broadcom, Cerebras, Lightmatter |
| Tier 3 | 学术会议 | 会期 | ~9 | IEDM, ISSCC, VLSI Symposium, DAC |
| Tier 4 | 政府/联盟 | 双周 | ~30 | DARPA ERI, NY CREATES, DOE MSRC, NSTC, SRC JUMP 2.0 |
| Tier 5 | 技术博客 | 双周 | ~10 | SemiAnalysis, ChipsAndCheese, SemiEngineering |
| Tier 6 | 出版物/arXiv | 月度 | ~4 | IEEE Xplore, Google Scholar, arXiv |

### 美国重点信源

**美国大学 (53所)**: MIT MTL, Stanford Nanolab, UC Berkeley, CMU, Georgia Tech, Purdue(Birck/SMART USA $1B+), UIUC(HMNTL), Michigan(LNF), Cornell(CNF/SUPREME), UT Austin(TIE/NGMM $840M), Penn State(CHIMES), ASU(SWAP Hub), UCSB, Caltech(KNI), Harvard(CNS), Princeton(MNFC), Columbia(CUBiC), UCSD(PRISM), Notre Dame, Wisconsin, Maryland, NC State(CLAWS), Duke, USC(CA DREAMS), Northwestern, JHU/APL, Ohio State, RPI, SUNY Poly(Albany NanoTech), Binghamton, Virginia Tech, Washington(WNF), Minnesota(MNC), Florida, RIT, Arizona, UC Davis, NYU Tandon, Colorado(NQN), Utah, Northeastern, UMass, Texas A&M, Iowa State, Arkansas(MUSiC SiC), Yale, Brown, Vanderbilt, Case Western, Lehigh, Stony Brook, Oregon State

**美国企业R&D (40家)**: Intel Labs, IBM Research, NVIDIA Research, Google Silicon, Microsoft Silicon, Meta AI, Apple Silicon, AMD Research, Qualcomm Research, Micron, TI, ADI, GF Labs, Broadcom, Marvell, Amazon Annapurna, Wolfspeed, onsemi, KLA, Lam Research, Applied Materials, Teradyne, Synopsys, Cadence, Arm US, Rambus, Entegris, DuPont, Brewer Science, Microchip, SkyWater, Qorvo, Cerebras, d-Matrix, Tenstorrent, Lightmatter, Celestial AI, Ayar Labs, SambaNova

**美国政府/研究机构 (29个)**: DARPA ERI 2.0, AFRL, NRL, ARL, ORNL, ANL, LBNL, LANL, LLNL, Sandia, PNNL, BNL/CFN, NREL, SLAC, Fermilab(SQMS), NY CREATES/Albany NanoTech ($25B+), MIT Lincoln Lab, Natcast/NSTC ($6.3B), SRC(JUMP 2.0), DoD Microelectronics Commons (8 Hubs), NIST, SIA, IMAPS, IEEE EPS

## 管道（Pipeline）定义

### Phase 1: 采集（Collect）
- 基础模式: HTTP爬取研究页面 → 提取文章列表 → 领域关键词分类
- 深度模式: 发现项目页面 → 结构化提取项目详情 → 团队/资金/里程碑解析
- 输出到 `artifacts/{date}/articles/` 或 `artifacts/{date}/projects/`

### Phase 2: 分析（Analyze）
- 基础模式: 方向聚类 → 生命周期判定 → 跨实验室交叉验证
- 深度模式: 项目组合分析 → 技术路线图 → 资金分布 → 实验室对标
- 输出到 `artifacts/{date}/analysis/`

### Phase 3: 报告（Report）
- 基础模式: JSON趋势报告 + Markdown洞察报告
- 深度模式: 每个项目的详细Markdown Profile + 项目组合概览 + 技术路线图
- 输出到 `artifacts/{date}/reports/`

## 研究标签体系

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
  confidence: 0.85
  summary: "..."

domains:
  - advanced_process           # GAA, CFET, BSPDN, EUV, High-NA
  - advanced_packaging         # Hybrid Bonding, 3D-stacking, FOWLP
  - memory_technology          # HBM, CXL, MRAM, FeRAM, 3D NAND
  - ai_chip_architecture       # DSA, Neuromorphic, In-memory, TPU
  - eda_design_automation      # ML-EDA, DTCO, Physical Design
  - semiconductor_materials    # SiC, GaN, 2D Materials, Wide Bandgap
  - quantum_computing          # Superconducting, Spin, Silicon Qubit
  - chiplet_interconnect       # UCIe, BoW, Die-to-Die
  - photonics                  # Silicon Photonics, CPO
  - manufacturing_equipment    # ALD, ALE, Etch, Metrology
  - reliability_test           # TDDB, BTI, HCI, EM
  - security                   # Hardware Security, PUF, Trojan
```

## 核心工具接口（8个）

### 基础采集
```json
{
  "tool": "collect_research_directions",
  "args": { "labs": ["imec", "intel-labs", "mit-mtl"], "mode": "weekly" }
}
```

### 基础分析
```json
{
  "tool": "analyze_research_trends",
  "args": { "date": "2026-06-03", "min_confidence": 0.6 }
}
```

### 基础报告
```json
{
  "tool": "generate_insight_report",
  "args": { "date": "2026-06-03", "format": "both" }
}
```

### 基础端到端
```json
{
  "tool": "collect_and_report",
  "args": { "labs": ["imec", "stanford-nanolab", "tsmc-research"], "mode": "weekly" }
}
```

### 深度项目采集（新增）
```json
{
  "tool": "collect_project_details",
  "args": { "labs": ["purdue-birck", "cornell-cnf"], "max_projects_per_lab": 5 }
}
```

### 深度项目报告（新增）
```json
{
  "tool": "generate_project_reports",
  "args": { "date": "2026-06-03", "lab_ids": ["purdue-birck"] }
}
```

### 深度端到端（新增）
```json
{
  "tool": "collect_and_report_deep",
  "args": { "labs": ["purdue-birck", "cornell-cnf", "utaustin-mrc"], "mode": "deep" }
}
```

### 列出信源
```json
{
  "tool": "list_available_labs",
  "args": { "region": "north_america", "category": "university_lab" }
}
```

## 输出 Schema (Hermes 消费格式)

### 基础报告 (JSON)
```json
{
  "report_meta": { "title": "...", "labs_covered": 25, "trends_identified": 30 },
  "top_trends": [{ "direction": "BSPDN", "lifecycle": "emerging", "confidence": 0.92 }],
  "domain_summary": {},
  "lab_activity": [],
  "cross_reference": { "convergences": [] }
}
```

### 项目详情报告 (Markdown)
每个研究项目生成独立章节，包含：
- 项目概述（详细描述）
- 研究目标（编号列表）
- 技术路线
- 关键创新
- 研究团队（PI姓名）
- 资金信息（来源+规模+周期）
- 里程碑时间线（带状态标记）
- 技术指标
- 相关发表

## CLI 使用

```bash
# 列出所有美国大学
python scripts/collect_and_report.py --list-labs --region north_america --category university_lab

# 列出AI芯片领域信源
python scripts/collect_and_report.py --list-labs --domain ai_chip_architecture

# 基础采集
python scripts/collect_and_report.py --labs imec,intel-labs --mode weekly

# 深度项目采集（含详细项目介绍）
python scripts/collect_and_report.py --labs purdue-birck,cornell-cnf --mode deep --project-mode

# 仅生成项目报告（从已有数据）
python scripts/collect_and_report.py --date 2026-06-03 --project-mode --report-only
```

## 质量门禁

1. **采集门**: 每个目标实验室至少找到 1 篇真实研究内容（非首页/列表页）
2. **结构化门**: 每篇文章/项目必须包含标题、摘要/描述、研究方向标签
3. **分析门**: 至少识别出 3 个明确的研究方向聚类
4. **报告门**: 同时输出 JSON 和 Markdown 格式报告
5. **引用门**: 每个趋势判断必须有 ≥2 个独立来源交叉验证

## 失败升级路径

- **目标页无法访问**: 降级到 WebSearch → 提取公开摘要
- **找不到研究内容**: 尝试实验室 Google Scholar 页面
- **付费墙**: 仅提取公开标题和摘要，标记 paywalled=true
- **研究方向无法分类**: 归入 "uncategorized"，由分析阶段处理
