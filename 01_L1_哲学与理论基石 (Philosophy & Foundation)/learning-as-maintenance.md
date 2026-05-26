---
created: 2026-05-20
tags:
  - layer/l1
  - type/article
  - domain/llm
  - domain/embodied-ai
  - method/optimization
---

# Learning as Maintenance：当"学习"变成"维护"

> 一次围绕三个方向的交叉头脑风暴记录——[[trinkle23897/learning-beyond-gradients|Learning Beyond Gradients]]、自动驾驶规则系统主导的现实、具身智能的 demo 困局。

## 三条线索的交汇

### 1. Learning Beyond Gradients（Heuristic Learning）

Trinkle23897 在 2026 年 5 月发表的长文提出了一个 provocative 的论点：**梯度不是唯一的更新机制**。当 coding agent 把"写规则"的边际成本降到足够低，启发式系统（rules + tests + replay + memory）可以在诸多任务上匹敌甚至超越端到端神经网络。他们用纯 Python 代码（未训练任何神经网络）在 Atari Breakout、MuJoCo Ant/HalfCheetah、VizDoom 上取得了与 Deep RL 相当甚至更好的结果。

核心洞察：「The object being updated is software structure rather than neural-network parameters。」

### 2. 自动驾驶：端到端口号下的规则现实

行业嘴上鼓吹端到端，实际落地绝大部分仍然是**规则 + 状态机 + safety guard**主导。原因：
- 端到端的可解释性与安全认证问题
- 长尾场景覆盖率不足
- 规则系统可以精确回滚，NN 不行

### 3. 具身智能：VLA / World Model 的 demo 期

VLA、World Model 让人兴奋但停留在 demo 阶段。核心卡点：
- 真实世界的分布偏移远超模拟器
- 数据效率极低——遥操作收集的数据覆盖不了真实交互的多样性
- NN 策略出错了难以调试

---

## 四个连接点

### 连接点 ①：规则系统≠静态系统——coding agent 让其成为学习系统

自动驾驶的"规则主导"往往意味着规则是**人写的、静态的、需要人工 review 和测试的**。但 HL 的核心贡献是证明：当 coding agent 介入后，规则系统不再是静态的，而是可自动迭代的。

> 如果有一个 coding agent 每天跑长尾场景回放、发现 corner case 就自动 patch 规则层，规则系统的维护成本曲线会像 Breakout 一样被改写。

### 连接点 ②：Residual Architecture 才是真正的落地形态

HL 文章中 Ant 的例子揭示了一个有趣的分层：

| 层级 | 方法 | 特性 |
|------|------|------|
| 底层 | CPG（Central Pattern Generator） | 纯规则/开环 |
| 中层 | MPC（Model Predictive Control） | 带模型的闭环控制 |
| 上层 | Residual action search | 在线优化 |

这不是"端到端 vs 规则"，而是**混合架构（Mixed Architecture）**。具身智能和自动驾驶的"端到端"叙事都倾向于去掉中间模块，但 HL 的证据提示：**也许应该反过来——保留可 debug、可测试的中间工程模块，让 NN 只负责 NN 擅长的部分（感知、分类）。**

### 连接点 ③：World Model 的真正用武之地在 test / replay

当前 World Model 的主流叙事是在 latent space 做 planning。但 HL 文章提供了一个更务实的用法：**把环境回放、失败视频、golden traces 当作 Heuristic System 的核心组件。** 换言之，World Model 最有价值的应用也许不是替代真实环境做 planning，而是替代真机做 regression testing：

- 每改一条规则，先在世界模型里跑 1000 个 replay
- 发现 regression 就自动回滚或提示
- 世界模型不够准没关系——它的价值在于 catch 那些**明显 broken** 的情况

### 连接点 ④：Agent 化 = 把学习问题变成维护问题 ← **重点展开**

这是讨论中最深入的方向——详见下一节。

---

## Learning = Maintenance：一个映射框架

如果把"学习"解构为软件工程中的"维护"问题，得到以下对应关系：

| 学术概念 | 维护问题等价物 |
|----------|----------------|
| Continual Learning | CI/CD pipeline + 版本管理 |
| 泛化能力 | test suite 覆盖率 |
| 灾难性遗忘 | regression bug |
| 样本效率 | 一行 hotfix vs 几万步 SGD |
| 迁移学习 | 可复用的模块 + 干净的接口抽象 |
| 过拟合 | over-engineering 了一条只对某个 case 生效的逻辑 |
| 模型压缩 | 代码重构：把 50 个 if-else 折叠成一个状态机 |
| 收敛性 | 代码复杂度管理——系统随着迭代趋于稳定还是腐烂 |

这个映射的意义在于：**"学习"的许多核心困难，在软件工程里已经有一套成熟的应对方案。** CI/CD 解决持续集成，code review 解决质量门禁，feature flag 解决灰度发布，单元测试解决回归防护。

> 一个 provocative 的问题：假如"学习 = 维护"这个等式成立，过去十年 ML 领域解决的到底是科学问题，还是工程问题？

### 推论

**a) AI 团队的技能栈会变**
关键能力不再是「设计损失函数/模型架构」，而是「构建 feedback loop、observability、rollback 机制」。团队结构从"研究员主导"转向"infra/agent/SWE 主导"。

**b) 新模型架构的边际价值在递减**
更好的规则维护工具和 agent 框架的边际收益在递增。某些方向正在从"科研问题"滑向"工程问题"。

**c) 历史在重复**
软件工程 1990s→2000s 经历过一次范式转换：「写代码最难」→「维护代码最难」（催生了 Agile、CI/CD、DevOps、测试文化）。
AI 正在经历相似的成熟过程：
- 2010s：「构建模型最难」（架构、损失函数、训练技巧）
- 2020s：「部署模型最难」（MLOps、serving、监控）
- 2025+：「维护 AI 系统最难」→ **agent 作为维护者**

---

## 框架的边界与失效条件

这个映射不能无限推广。以下场景中"学习 = 维护"等式会失效：

1. **感知任务**（ImageNet 级别的视觉）——不可能用 if-else 写一个图像分类器。这是 NN 不可替代的领地。
2. **创造性/模糊性任务**——需求本身就在变，连 test oracle 都是模糊的，何谈维护。
3. **状态空间爆炸**——规则不擅长组合泛化。50 个 flag 的组合是 2⁵⁰ 种状态，纯规则系统会坍塌。
4. **收敛性保障**——SGD 有理论保证（至少局部收敛），agent 修代码没有。你怎么知道 agent 不会越修越乱？

> "学习 = 维护"不是一个通用理论，而是一个**边界条件论断**：在那些规则/NN mixed 可行的领域里，维护视角比训练视角更经济。

---

## 回看三个方向

### 自动驾驶
最契合这个框架。安全关键系统天生需要可审计性和可测试性，维护文化正好提供这些。问题是：谁来维护规则？如果是 coding agent，经济学变了。

### 具身智能
在这个框架下，最务实的路径可能是**三层架构**：
- **底层：规则/MPC** —— 安全保障、低延迟控制
- **中层：NN 感知** —— object detection、state estimation
- **上层：coding agent 维护规则层** —— 快速修补失败案例，避免频繁 retrain

这与 HL 文章提出的 System 1 / System 2 分工在精神上一致。

### Heuristic Learning 本身
HL 最大的价值也许不是"替代 Deep RL"，而是**揭示了梯度优化的替代路径**——在 coding agent 成本足够低时，工程化的启发式系统可以成为可行的学习范式。接下来的关键问题是：HL 产生的数据分布能否稳定地回传给 NN 做周期性更新（这是一个经典 post-training 问题）。

---

## 相关笔记

- 尚无相关笔记，本文是此方向的第一篇

## 来源

- [Learning Beyond Gradients - Trinkle23897](https://trinkle23897.github.io/learning-beyond-gradients/#zh) —— HL 范式的原始论述
