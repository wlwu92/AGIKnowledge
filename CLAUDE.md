# AGIKnowledge Vault 使用规范

## 目录结构

```
AGIKnowledge/
├── 00_资料与素材 (Attachments & Resources)/
│   ├── Inbox/              # Web Clipper 原始剪藏（未整理）
│   └── Clippings/          # 已整理归档的原始素材
├── 01_L1_哲学与理论基石 (Philosophy & Foundation)/  # 数学、信息论、认知科学等基础理论
├── 02_L2_核心技术与算法 (Core Tech & Algorithms)/   # ML/DL/RL/CV/NLP/Robotics 算法
├── 03_L3_系统架构与路径 (Systems & Architectures)/  # Infra / AI Infra / 系统设计
├── 04_L4_应用、伦理与前沿 (Applications & Frontiers)/ # 具身智能、LLM 应用、前沿方向
└── 99_索引与地图 (Index & Maps)/   # MOC、标签索引
```

## 分类规则

| 层级 | 内容范围 |
|------|----------|
| **L1** | 数学基础、信息论、认知科学、统计学、优化理论 |
| **L2** | 模型架构、训练方法、损失函数、CV/NLP/Robotics 核心算法 |
| **L3** | 训练框架、推理优化、分布式系统、MLOps、AI Infra、编译优化 |
| **L4** | LLM 应用、具身智能、AI Agent、AI 安全、行业落地 |

## 笔记整理规则

- 正式笔记先查 `99_索引与地图 (Index & Maps)/标签体系.md`，再写 frontmatter。
- 每篇正式笔记必须包含 1 个 `layer/*` 和至少 1 个 `type/*` 标签，主类型放在最前。
- 标签使用小写英文层级格式，例如 `domain/cv`、`topic/3d-reconstruction`、`venue/cvpr-2025`。
- 新资料进入知识库前，先搜索相邻笔记和 MOC/survey，决定是新建原子笔记、更新已有综述，还是补充关联链接。
- 原始剪藏的处理状态使用 `status: processed` 等元数据，不使用临时标签。
