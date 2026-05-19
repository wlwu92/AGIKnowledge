---
source: "https://andypinxinliu.github.io/GestureLSM/"
created: 2026-05-14
aliases:
  - GestureLSM
tags:
  - layer/l2
  - type/paper
  - domain/embodied-ai
  - domain/cv
  - topic/audio-driven-motion
  - method/transformer
  - venue/iccv-2025
  - entity/pantomatrix
---

# GestureLSM — 潜在捷径共语手势生成

> **GestureLSM: Latent Shortcut based Co-Speech Gesture Generation with Spatial-Temporal Modeling**
>
> **作者**: Pinxin Liu (Rochester), Luchuan Song (Rochester), Junhua Huang (Rochester), **Haiyang Liu** (Tokyo), Chenliang Xu (Rochester)
> **会议**: ICCV 2025
> **项目页**: https://andypinxinliu.github.io/GestureLSM/
> **论文**: https://arxiv.org/abs/2501.18898
> **代码**: https://github.com/andypinxinliu/GestureLSM

## 概述

GestureLSM 是 EMAGE 之后在 **BEAT2** 数据集上实现新 SOTA 的全身共语手势生成工作。由 EMAGE 一作 Haiyang Liu 参与，核心思路从 **masked modeling** 转向 **flow matching**，并引入空间-时间注意力机制显式建模身体各区域（身体、双手、腿）之间的协调关系，同时大幅降低推理延迟。

## 核心贡献

1. **空间-时间建模**（Spatial-Temporal Attention）：通过空间注意力（body region cross-interaction）和时序注意力（motion progression）显式建模不同身体分区之间的交互，而非简单拼接
2. **Flow Matching 框架**：替代自回归/扩散生成范式，建模潜在速度场（latent velocity space），实现更高效的采样
3. **Latent Shortcut Learning + Beta Distribution Time Stamp Sampling**：解决标准 flow matching 在手势生成中效果欠佳的问题，提升合成质量并加速推理

## 方法机制

- 音频 + 文本特征拼接，通过 cross-attention 融合为条件特征
- 条件特征输入 **Spatial-Temporal Decoder**，输出手势 latent
- 使用 **Flow Matching** 作为训练目标，建模 latent 空间的概率路径
- 手势 latent 来自预训练的 **RVQ (Residual Vector Quantization)** 模型
- Spatial-Temporal Attention 模块集成位置编码，学习身体区域的时空交互

## 评估结果

### 质量对比 (BEAT2 Full Body FGD ↓)

| GestureLSM | EMAGE |
|-----------|-------|
| **0.4040** | 0.5512 |

### 推理速度对比 (AIST, 每句, NVIDIA A100 ↓)

| 方法 | 时间 | 相对 EMAGE |
|------|------|-----------|
| **GestureLSM** | **0.039s** (含面部 0.042s) | **快 4.5×** |
| EMAGE | 0.174s | 基准 |
| DiffSHEG | 0.112s | — |
| MambaTalk | 0.134s | — |

默认 8 步采样，1 步可压到 0.015s（但 FGD 退化为 6.235）。

- 生成动作被描述为 "coherent and smooth"
- 相比竞品无 "temporal jittering, abnormal body parts movements, and disjointed gestures" 问题
- 论文图 2 显示 GestureLSM 处于 **FGD × 速度象限的左上角**（质量最好 + 速度最快）

## 关联笔记

- [[2026-05-14-EMAGE-全身共语手势生成]] — 前代 SOTA，GestureLSM 的直接前身
- [[2026-05-14-PantoMatrix-音频驱动3D姿态合成框架]] — PantoMatrix 生态（EMAGE 一作参与 GestureLSM）
- [[2026-05-14-Audio-Driven-Robot-Motion-音频驱动机器人运动全链路]] — 全链路综述

## 判断与局限

- Flow matching 替代 masked modeling 是重要的方法转向，推理效率提升显著
- EMAGE 一作参与但非全职转到该团队，PantoMatrix 框架尚未集成 GestureLSM
- 目前缺少关于物理合理性、手部细节（手指运动）的专项评估
- 可视为 EMAGE 的**精神续作**，在 BEAT2 benchmark 上取得实质性进步
