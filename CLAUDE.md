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

## 消费 Chrome 书签 Inbox

这是核心流程。用户在任何电脑上将感兴趣的内容收藏到 Chrome 的 **Inbox** 文件夹（书签栏层级），回到个人电脑后一次性消费。注意 Chrome 同步时会 strip emoji，所以文件夹名用纯英文 "Inbox"。

### 执行流程

1. **确保 Chrome 已启动（数据可读）**
   - 检查 Chrome 进程是否在运行
   - 若未运行，用 `open -a "Google Chrome" --background` 启动
   - 启动后等待 3 秒确保书签文件同步到磁盘

2. **读取 Chrome 书签**
   - 文件位置：`~/Library/Application Support/Google/Chrome/Default/Bookmarks`
   - 定位 `bookmark_bar` 下的 **Inbox** 文件夹（兼容 "📥 Inbox"）
   - 若 Inbox 不存在则自动创建（纯英文名 "Inbox"）

3. **逐条消费**
   - 对每条书签，用 WebFetch 获取页面内容
   - 根据内容分类到 L1-L4
   - 写入结构化笔记，包含：摘要、关键点、关联知识、思考
   - 笔记文件格式：`YYYY-MM-DD-简短英文标题.md`

4. **清理**
   - 用 AppleScript 删除已消费的 Inbox 条目（直接操作 Chrome 内存态，比改 JSON 文件可靠）：
     ```
     tell application "Google Chrome"
         delete every bookmark item of bookmark folder "Inbox" of bookmarks bar
     end tell
     ```
   - 不需要记录 processed_bookmarks（Inbox 消费即删）

### 消费要求

- 第一条失败不影响后续处理
- 不需要先跟用户确认，直接执行全部消费
- 消费完成后输出汇总：条目、归属层级、处理结果
- 如果 Chrome 是本次自动启动的，处理完后不需要关闭它（用户可能在其他地方使用）

## 整理 Web Clipper 素材（备用）

Web Clipper 剪藏到 `00_资料与素材/Inbox/` 的内容，按同样规则分类写入 L1-L4，原始文件移到 Clippings/。
