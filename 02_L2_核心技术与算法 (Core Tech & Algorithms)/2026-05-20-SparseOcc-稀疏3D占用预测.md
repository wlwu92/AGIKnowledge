---
source: "https://zhuanlan.zhihu.com/p/709576252"
created: 2026-05-20
aliases:
  - SparseOcc
  - Fully Sparse 3D Occupancy Prediction
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - topic/3d-reconstruction
  - method/transformer
  - venue/eccv-2024
---

# SparseOcc — 稀疏3D占用预测与 RayIoU 评估指标

## 概述

SparseOcc (Fully Sparse 3D Occupancy Prediction) 由南京大学和上海 AI 实验室的 Haisong Liu、Yang Chen 等提出，发表于 ECCV 2024（arXiv: 2312.17118）。它是首个**全稀疏的 3D 语义占用预测网络**，不使用稠密体素或稠密特征，同时提出了基于射线的评估指标 **RayIoU**。

相关仓库：[[MCG-NJU/SparseOcc](https://github.com/MCG-NJU/SparseOcc)]

## 核心贡献

- **首个全稀疏占用网络**：避免稠密 3D 体积的计算开销，仅对非自由空间建模
- **Sparse Voxel Decoder**：从粗到细地重建场景几何
- **Mask Transformer**：使用稀疏语义/实例查询配合 mask-guided sparse sampling，避免全局注意力
- **RayIoU 评估指标**：基于模拟 LiDAR 射线的评价方案，解决传统体素 mIoU 沿深度方向的不一致性惩罚问题

## 方法机制

1. 2D 图像特征提取（ResNet-50 骨干）
2. Mask Transformer 以稀疏 queries 与 2D 特征通过 mask-guided 稀疏采样交互
3. Sparse Voxel Decoder 从粗到细重建稀疏体素占用
4. RayIoU 替代体素级 mIoU：每条查询射线判断预测类别和深度误差是否在阈值内

## 性能

| 设置 | RayIoU | FPS |
|------|--------|-----|
| r50, 7 history frames (v1.0) | 34.0 | 17.3 |
| r50, 15 history frames | 35.1 | — |
| r50, 8 frames, 24 epochs (v1.1) | 36.8 | 17.3 |
| r50, 8 frames, 60 epochs (v1.1) | 37.7 | 17.3 |

## 关联笔记

- [[2026-05-20-DETR-端到端目标检测变换器|DETR]] — 共享 Transformer + queries 的设计理念
- [[2026-05-20-RT-DETR-实时目标检测变换器|RT-DETR]] — Transformer 在视觉感知中的另一应用方向

## 判断与局限

- 全稀疏设计显著降低计算和内存消耗，有利于实际部署
- RayIoU 解决了传统评估在薄表面上的偏差问题，已被 CVPR 2024 自动驾驶挑战赛采用
- 目前仅基于单目/环视图像输入，与 LiDAR 方法相比在深度精度上有天然局限
