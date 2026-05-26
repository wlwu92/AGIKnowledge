---
source: https://nvlabs.github.io/motionbricks/
created: 2026-05-23
aliases:
  - MotionBricks
  - Scalable Real-Time Motions with Modular Latent Generative Model
  - Smart Primitives
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - domain/graphics
  - topic/video-generation
  - entity/nvidia
  - venue/siggraph-2026
---

# MotionBricks — Scalable Real-Time Motions with Modular Latent Generative Model and Smart Primitives

**ACM Trans. Graphics, SIGGRAPH 2026** | arXiv: [2604.24833](https://arxiv.org/abs/2604.24833) | Project: [nvlabs.github.io/motionbricks/](https://nvlabs.github.io/motionbricks/)

## 概述

NVIDIA 提出的实时人体运动生成框架，以 **15,000 FPS** 的速度从超大规模运动库（350,000+ 运动技能）合成高质量运动。核心思想是将运动生成分解为**模块化潜空间生成模型 + 智能原语（Smart Primitives）**，零样本适配新下游任务——"像搭积木一样（stacking bricks）组合运动技能，无需动画专家知识"。

MotionBricks 是 NVIDIA [[2026-05-23-GR00T-人形机器人全身控制平台.md|GR00T-WholeBodyControl]] 平台的子组件之一，与 **GEAR-SONIC**（行为基础模型）、**Kimodo**（离线运动生成）共同构成 NVIDIA 运动生成技术栈。

## 核心贡献

- **极速性能**：15,000 FPS 生成 + 仅 2ms 延迟，单神经网络实时推理
- **超大规模**：单神经网络覆盖 350,000+ 运动技能，使用 BONES-SEED 数据集（生产级 Mocap 数据）
- **Smart Locomotion**：统一可插拔导航接口，支持任意速度、方向、风格指令的鲁棒组合
  - **单一风格零样本生成**：zombie、injured-leg、injured-torso、skipping、strafing、crouch strafing 等
  - **风格混合与连续过渡**：运行时实时切换（idle → walk → jog → run），速度/方向/步态连续可控
- **Smart Objects**：通过代理关键帧（proxy keyframes）指定场景/物体交互意图，模型自动填充接近（approach）、接触（contact）和跟随（follow-through）三个阶段，每次运行自然变化
  - 演示场景包括：拾剑、倒地、跃过长凳、坐姿、交互式编排
- **零样本迁移**：无需微调或逐任务标注即可适配新下游任务；各应用像"搭积木"一样即插即用
- **UE5 原生集成**：完整 2:40 分钟无剪辑 UE5 演示，所有运动由神经网络生成——**无 foot-locking、无 blend、无碰撞检测、无手写过渡**
- **Kimodo**：NVIDIA 的互补离线运动生成项目，与 MotionBricks 的实时运行形成离线/在线协同

## 技术架构

### 模块化潜空间生成模型

MotionBricks 的核心是一个大规模实时生成式框架，基于**模块化潜空间生成骨干网络**（modular latent generative backbone）。单一模型同时覆盖 350,000+ 运动技能，实现 15,000 FPS 推理。

| 组件 | 详情 |
|------|------|
| 模型架构 | 模块化潜空间生成模型（Modular Latent Generative Model） |
| 推理速度 | 15,000 FPS 生成，端到端延迟 2ms |
| 训练数据 | BONES-SEED 数据集（350,000+ 生产级 Mocap 片段，真人演员录制） |
| 数据重定向 | 通过 SOMA Retargeter（Newton 求解器）将 SOMA 捕获数据重定向到 Unitree G1 人形机器人骨架 |
| 训练管线 | 自包含合成训练管线（预发布版随附），完整版本约 1 个月后随 GR00T Whole-Body Control 发布 |
| 模型覆盖 | 3.5×10⁵ 个可区分的运动技能（motion skills），远超此前方法 |

### Smart Primitives — 智能运动原语

**Smart Locomotion**：统一可插拔导航接口，接收速度、方向和风格指令的高维向量输入，模型在潜空间中完成风格混合与平滑过渡。无需为每种风格组合单独训练，推理时通过指令向量零样本生成。

**Smart Objects**：用户提供稀疏的代理关键帧（如"手到达位置 X"、"在时间 T 接触物体"），模型自动补全三个相位：
1. **Approach（接近）**：从当前姿态移动到交互起始位置
2. **Contact（接触）**：按关键帧约束执行交互动作
3. **Follow-through（跟随）**：交互完成后的自然回位或过渡动作

### 与基线对比

与 6 种最先进的 in-betweening 基线进行了并排比较。在实时性、技能覆盖范围和自然度方面均达到当时最优水平。

## 与 GR00T 生态的关系

```
GR00T-WholeBodyControl
├── GEAR-SONIC        — 人形行为基础模型（运动跟踪）
├── Decoupled WBC     — 下肢RL + 上肢IK
├── MotionBricks      — 实时模块化运动生成（本笔记，15,000 FPS）
└── Kimodo            — 离线运动生成（与 MotionBricks 互补）
```

## 关联笔记

- [[2026-05-23-GR00T-人形机器人全身控制平台.md|GR00T-WholeBodyControl — 人形机器人全身控制平台]]（所属生态，MotionBricks 是其子组件）
- [[2026-05-23-GEM-统一人体运动估计与生成模型.md|GEM]]（同为 NVIDIA 人体运动方向的工作，但聚焦估计+生成统一）
- [[2026-05-23-GEM-X-全身SOMA人体姿态估计.md|GEM-X]]（SOMA Retargeter 的完整管线，MotionBricks 数据重定向依赖此工具链）
- [[2026-05-12-SOMA-X-统一参数化人体模型.md|SOMA-X]]（MotionBricks 使用的重定向工具基础）

## 判断与局限

- 15,000 FPS 和 350K 技能规模在实时运动生成领域处于领先水平，相比传统的 foot-locking / blend / collision detection 管线有质的飞跃
- "无 foot-locking、无 blend、无碰撞检测、无手写过渡"的 UE5 管线表明运动完全由神经网络驱动，工程化程度极高
- **Smart Primitives 设计理念**——将复杂运动分解为可组合积木块——是 MotionBricks 的核心创新，零样本迁移能力使其角色从"动画工具"升级为"运动生成平台"
- 作为 GR00T 生态的子组件，与 Isaac Lab 和 Unitree 硬件绑定较深，复现门槛高（64+ GPU 训练）
- **Kimodo** 作为离线互补项目，覆盖 MotionBricks 无法处理的非实时场景
- 论文为 SIGGRAPH 2026，代码尚未完全开源（预计1个月后随 GR00T Whole-Body Control 完整训练管线发布）
- BONES-SEED 数据集 350K+ 技能规模为闭源生产级数据，外部研究者难以在同等数据规模下对比
