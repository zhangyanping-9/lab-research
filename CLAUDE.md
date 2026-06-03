# 半导体研究方向收集系统 (Semi Research Direction Collect)

> 本系统定期收集全球半导体实验室、研究机构、企业R&D中心的最新研究方向，通过结构化分析和洞察提炼，生成可供 Hermes 智能体消费的研究报告。

## 架构

```
┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  Hermes Agent    │◄──►│   Collector     │◄──►│  Lab Registry    │
│  (控制/调度层)     │    │   (采集层)       │    │  (100+ 实验室)    │
└──────────────────┘    └────────┬────────┘    └──────────────────┘
                                 │
                          ┌──────▼──────┐
                          │  Extractor  │──► artifacts/{date}/articles/
                          │  (提取层)    │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  Analyzer   │──► artifacts/{date}/analysis/
                          │  (分析层)    │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  Reporter   │──► artifacts/{date}/reports/
                          │  (报告层)    │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │ HermesBridge│──► 结构化洞察 (JSON/MD)
                          │  (适配层)    │
                          └─────────────┘
```

## 目录结构

```
semi-research-direction-collect/
├── CLAUDE.md                # 本文件 - 项目指令
├── README.md                # 完整文档
├── pyproject.toml           # Python 依赖
├── src/
│   ├── __init__.py
│   ├── config.py            # 全局配置
│   ├── registry.py          # 实验室注册表加载与管理
│   ├── collector.py         # 采集编排
│   ├── extractor.py         # 内容提取
│   ├── analyzer.py          # 研究方向分析 & 趋势识别
│   ├── reporter.py          # 报告生成
│   └── hermes_bridge.py     # Hermes 智能体适配
├── data/
│   ├── lab_registry.yaml    # 实验室注册表（100+ 来源）
│   └── collection_config.yaml
├── hermes/
│   ├── tools.json           # Hermes 工具定义
│   ├── agent_config.yaml    # Hermes 智能体配置
│   └── prompts/
│       ├── collect.md       # 采集阶段 prompt
│       ├── analyze.md       # 分析阶段 prompt
│       └── report.md        # 报告阶段 prompt
├── scripts/
│   └── collect_and_report.py # 统一采集入口
└── artifacts/               # 产出物
    └── {date}/
        ├── articles/
        ├── analysis/
        └── reports/
```

## Agent Team

大规模任务时可协作的子智能体：
- `coordinator` — 整体调度
- `collector` — 采集执行
- `analyzer` — 研究方向分析
- `reporter` — 报告撰写
- `quality-assurance` — 质量审核

## 使用方式

### 方式1: Hermes 智能体直接调用
```python
from src.hermes_bridge import HermesBridge
bridge = HermesBridge()
report = bridge.collect_and_report(labs=["imec", "intel-labs", "mit-mtl"])
```

### 方式2: 手动触发采集
```bash
cd scripts && python collect_and_report.py --labs imec,intel-labs --mode weekly
```

### 方式3: 通过 Playwright MCP + Claude Agent
使用 `hermes/prompts/` 下的 prompt 模板，在 Claude Code 中半自动执行。

## Required Behavior

- 优先使用确定性脚本进行规模化采集，Agent 用于分析和判断
- 每个研究方向的洞察必须有来源引用
- 趋势判定需要跨实验室交叉验证
- 保存原始 HTML 和结构化提取结果
- 产出物必须对 Hermes 智能体可消费（JSON Schema + Markdown 双格式）
- 不要将主页/列表页视为采集成功 — 必须提取到具体研究内容页
- 研究方向需要标注: emerging | growing | mature | declining
