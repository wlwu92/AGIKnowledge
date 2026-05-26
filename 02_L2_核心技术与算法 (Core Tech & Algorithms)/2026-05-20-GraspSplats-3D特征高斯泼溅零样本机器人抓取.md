---
source: "https://graspsplats.github.io/"
created: 2026-05-20
aliases:
  - GraspSplats
  - 3D Feature Splatting for Grasping
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - domain/robotics
  - topic/3d-reconstruction
  - topic/dexterous-grasping
  - topic/hand-object-interaction
  - venue/corl-2024
---

# GraspSplats — 3D 特征高斯泼溅零样本机器人抓取

> **GraspSplats: Efficient Manipulation with 3D Feature Splatting**
>
> **作者**: Mazeyu Ji\*, Ri-Zhao Qiu\*, Xueyan Zou, Xiaolong Wang (\* equal contribution)
> **机构**: UC San Diego
> **论文**: [arXiv 2409.02084](https://arxiv.org/abs/2409.02084)
> **项目页**: [graspsplats.github.io](https://graspsplats.github.io/)
> **代码**: 未开源
> **发表**: CoRL 2024

---

## 概述

GraspSplats 将 **3D Gaussian Splatting** 与 **语义特征** 相结合，实现零样本（zero-shot）、语言驱动的零件级（part-level）机器人抓取。核心思想：为 3D Gaussians 赋予语义和几何特征，在显式 3D 表示上直接进行抓取采样，同时通过点跟踪支持动态场景。

## 核心贡献

1. **快速场景重建**：< 60 秒内生成高质量场景表示，速度是现有 3DGS 方法的 **1/10**
2. **实时抓取采样**：利用显式 Gaussian 几何，毫秒级生成对极抓取（antipodal grasp）候选
3. **动态/铰接物体操作**：通过 2D 点跟踪器刚体更新 Gaussians，支持物体运动场景，无需重新训练
4. **开放词汇零件级抓取**：结合 MobileSAMv2 + MaskCLIP 蒸馏物体级和零件级语义特征到 Gaussians，支持自然语言指定抓取部位

## 方法机制

### 特征增强的 3D Gaussians

```
多视角 RGB-D 图像
       ↓
3DGS 重建 (深度监督加速)
       ↓
特征蒸馏: MobileSAMv2 (物体级) + MaskCLIP (零件级)
       ↓
特征增强 3D Gaussians ← 层次化特征提取 + 几何正则化稠密初始化
```

### 抓取与操作流程

1. **场景表示**：RGB-D 序列 → 带特征的高斯场（< 60s）
2. **零件级抓取**：语言查询（如"cup handle"）→ 特征匹配 → 对极抓取采样 → 执行
3. **动态跟踪**：2D 点跟踪器 → 3D 高斯刚体更新 → 跟踪物体运动 → 抓取

### 关键设计

- **层次化特征提取**：多尺度特征融合，兼顾语义理解与几何精度
- **几何正则化稠密初始化**：利用深度图先验加速收敛，提升重建质量
- **特征蒸馏**：将 2D 基础模型 (SAM, CLIP) 的知识蒸馏到 3D Gaussians

## 实验结果

在 **Franka 机器人**上，GraspSplats 在多样化任务中显著超越：
- NeRF 类方法：F3RM、LERF-TOGO
- 2D 检测类方法

支持的场景类型：
| 场景 | 说明 |
|------|------|
| 静态场景零件级抓取 | 按语言指令抓取特定部位 |
| 多物体快速连续抓取 | 逐个抓取场景中多个物体 |
| 动态物体抓取 | 跟踪运动物体（如移动中的茶壶）并抓取 |
| 物体归位 | 将位移物体放回原位 |

## 适用边界

- **优势**：重建速度快（< 60s）、支持动态场景、零样本泛化、语言驱动
- **局限**：
  - 需要 RGB-D 输入（依赖深度传感器）
  - 动态跟踪依赖 2D 跟踪器质量，快速运动可能失败
  - 未开源代码，可复现性有限
  - 在高度杂乱场景中的表现未充分验证

## 关联笔记

- [[2026-05-20-前馈式3D高斯溅射重建综述|前馈式 3DGS 重建综述]] — 3DGS 重建技术上下文
- [[2026-05-20-Dr-Robot-可微机器人渲染|Dr. Robot]] — 另一条 3DGS + 机器人路径（自表征 vs 场景表示）
- [[2026-05-20-Diff3R-可微优化前馈3D高斯溅射|Diff3R]] — 可微优化前馈 3DGS

## 判断与局限

GraspSplats 是 3DGS 在机器人操作领域的代表性工作，核心贡献在于将 3DGS 的显式几何优势与语义特征结合，实现了快速度、零样本的零件级抓取。与 Dr. Robot（机器人本体自表征）互补：Dr. Robot 建模"自己"，GraspSplats 建模"场景"。
