# AGIKnowledge Vault 使用规范

## 目录结构

```
AGIKnowledge/
├── 00_资料与素材 (Attachments & Resources)/
│   ├── Inbox/              # Web Clipper 原始剪藏（未整理）
│   └── Clippings/          # 已由 Claude 整理归档的原始素材
├── 01_L1_哲学与理论基石 (Philosophy & Foundation)/  # 数学、信息论、认知科学等基础理论
├── 02_L2_核心技术与算法 (Core Tech & Algorithms)/   # ML/DL/RL/CV/NLP/ Robotics 算法
├── 03_L3_系统架构与路径 (Systems & Architectures)/  # Infra / AI Infra / 系统设计
├── 04_L4_应用、伦理与前沿 (Applications & Frontiers)/ # 具身智能、LLM 应用、前沿方向
└── 99_索引与地图 (Index & Maps)/   # MOC (Map of Content)、标签索引
```

## 分类规则

新内容按以下规则归入 L1-L4：

- **L1 哲学与理论基石**: 数学基础、信息论、认知科学、统计学、优化理论
- **L2 核心技术与算法**: 模型架构、训练方法、损失函数、表示学习、强化学习、CV/NLP 核心算法
- **L3 系统架构与路径**: 训练框架、推理优化、分布式系统、MLOps、AI Infra、编译优化
- **L4 应用、伦理与前沿**: LLM 应用、具身智能、AI Agent、AI 安全、行业落地

## 整理流程

用户要求整理 Inbox 时：
1. 读取 `00_资料与素材/Inbox/` 下所有 .md 文件
2. 根据内容判断属于 L1-L4 哪个层级
3. 生成结构化笔记（摘要 + 关键点 + 关联知识 + 思考）
4. 写入对应层级目录，文件名格式：`YYYY-MM-DD-简短标题.md`
5. 原始文件从 Inbox/ 移到 Clippings/
