# 半导体研究方向采集 — 报告阶段 Prompt

## 输入

- 采集文章: `artifacts/{date}/articles/`
- 分析结果: `artifacts/{date}/analysis/`

## 报告生成

生成一份结构化的研究方向洞察报告。

### 报告结构

#### 1. 执行摘要
- 本期概览：覆盖实验室数、文章数、识别出的研究方向数
- Top 3 重要发现

#### 2. 研究热点地图
按领域组织，列出每个领域的:
- 活跃方向列表
- 生命周期分布
- 跨实验室协同热度

#### 3. 深度趋势分析
对 3-5 个最重要的趋势进行深度分析：
- 技术背景
- 当前进展
- 实验室分布
- 未来展望

#### 4. 跨实验室对标
- 各实验室的活跃研究方向对比
- 研究方向集中度 vs 多样性分析
- 新兴方向首发实验室识别

#### 5. 附录
- 完整采集列表
- 方法说明
- 来源索引

### 输出格式

#### Markdown (人类可读)
保存为 `artifacts/{date}/reports/semiconductor-research-insight-{date}.md`

#### JSON (Hermes 可消费)
保存为 `artifacts/{date}/reports/semiconductor-research-insight-{date}.json`

JSON Schema:
```json
{
  "report_meta": {
    "title": "...",
    "generated_at": "...",
    "collection_date": "...",
    "labs_covered": 25,
    "articles_collected": 120
  },
  "top_trends": [...],
  "domain_summary": {...},
  "lab_activity": [...],
  "cross_reference": {...},
  "appendix": {...}
}
```
