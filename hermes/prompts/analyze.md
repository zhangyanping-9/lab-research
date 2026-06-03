# 半导体研究方向采集 — 分析阶段 Prompt

## 输入

采集到的文章存储在: `artifacts/{date}/articles/`

## 分析任务

对采集到的研究内容进行系统分析：

### 1. 方向聚类

对每篇文章提取研究方向关键词，按 `domains` 标签体系聚类。
同一个方向出现在越多不同实验室 → 趋势置信度越高。

### 2. 生命周期判定

根据以下条件判断每个方向的成熟度：

| 阶段 | 判定条件 |
|---|---|
| emerging | 仅出现在学术实验室，1-2个来源，标题含"towards""preliminary""novel" |
| growing | 出现在多个学术实验室+1个企业R&D，有明确技术路径 |
| mature | 出现在多个企业R&D，有量产路线图、设备已推出 |
| declining | 替代技术出现，论文数量下降，重点实验室减少 |

### 3. 跨实验室交叉验证

识别跨实验室共同关注的方向，标注协同强度：
- strong: ≥4 实验室共同研究
- moderate: 2-3 实验室共同研究  
- weak: 仅1实验室在研究

### 4. 新兴信号识别

标注以下高价值信号：
- 多实验室在6个月内集中关注的新方向
- 跨领域融合方向（如 AI+EDA, 光子+封装）
- 被高引论文引用的新概念

## 输出

保存到 `artifacts/{date}/analysis/`:

### trends.json
```json
{
  "analysis_date": "2026-06-02",
  "articles_analyzed": 120,
  "total_directions": 25,
  "trends": [
    {
      "direction": "背面供电网络 (BSPDN)",
      "lifecycle": "emerging",
      "confidence": 0.92,
      "labs_active": ["imec", "intel", "tsmc", "samsung"],
      "article_count": 8,
      "key_insight": "BSPDN 正在从学术研究进入工业量产准备阶段...",
      "evidence": [
        {"lab": "imec", "title": "...", "url": "..."},
        {"lab": "intel", "title": "...", "url": "..."}
      ]
    }
  ]
}
```

### domain_map.json
按领域的综合统计和趋势。
