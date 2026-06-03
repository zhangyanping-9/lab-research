# 半导体研究方向采集 — 采集阶段 Prompt
# 在 Claude Code/Playwright 环境中使用

## 目标

访问以下实验室的研究页面，提取最新研究方向信息。

## 实验室列表

{labs}

## 采集密度

{mode}

## 采集步骤

1. 打开实验室的 research/publications 页面
2. 等待页面加载稳定
3. 识别页面类型 (research_list | publication_page | article_page | conference)
4. 提取候选研究论文/项目列表
5. 对每篇研究内容提取:
   - 标题
   - 摘要 (前200字)
   - 研究方向关键词
   - 发表/更新时间
   - URL
   - 作者列表
6. 保存原始HTML + 结构化JSON

## 分类标准

研究方向关键词从以下列表中匹配:

advanced_process: ["GAA", "CFET", "nanosheet", "forksheet", "BSPDN", "backside power", "EUV", "high-NA", "multi-patterning", "sub-2nm", "atomic layer"]
advanced_packaging: ["hybrid bonding", "3D stacking", "silicon interposer", "FOWLP", "FOPLP", "HBM", "micro-bump", "TCB", "chiplet", "UCIe"]
memory_technology: ["HBM", "CXL", "MRAM", "FeRAM", "PCM", "STT-MRAM", "SOT-MRAM", "3D NAND", "DRAM scaling", "computational memory"]
ai_chip_architecture: ["DSA", "neuromorphic", "in-memory computing", "analog computing", "transformer accelerator", "sparse computation", "dataflow architecture"]
eda_design_automation: ["RTL-to-GDSII", "ML-EDA", "design space exploration", "timing closure", "floorplanning", "routing optimization"]
semiconductor_materials: ["SiC", "GaN", "2D materials", "graphene", "MoS2", "wide bandgap", "ultra-wide bandgap", "ferroelectric"]
quantum_computing: ["qubit", "superconducting", "spin qubit", "silicon quantum", "quantum error correction", "quantum-classical"]
photonics: ["silicon photonics", "optical interconnect", "co-packaged optics", "integrated laser", "modulator"]
manufacturing_equipment: ["ALD", "ALE", "CVD", "PVD", "etch", "metrology", "inspection", "process control"]
reliability_test: ["TDDB", "BTI", "HCI", "NBTI", "electromigration", "thermal management"]

## 输出格式

每篇文章保存为:

artifacts/{date}/articles/{lab_id}/{article_slug}.json
```json
{
  "lab_id": "imec",
  "lab_name": "imec",
  "title": "Backside Power Delivery Network for 2nm GAA",
  "url": "https://www.imec-int.com/en/articles/...",
  "published_at": "2026-05-15",
  "summary": "本文探讨了...",
  "keywords": ["BSPDN", "GAA", "2nm"],
  "domains": ["advanced_process"],
  "lifecycle": "emerging",
  "page_type": "article_page",
  "captured_at": "2026-06-02T12:00:00Z",
  "confidence": 0.85,
  "quality_flags": {}
}
```

## 质量门禁

- 必须进入真正的文章/研究页面（非主页、非列表页）
- 无法进入时，通过 WebSearch 搜索该实验室的最新论文作为降级方案
- 每个实验室至少采集 1 篇有意义的研究内容
