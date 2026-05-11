---
source: "https://github.com/princeton-vl/DROID-SLAM"
created: 2026-05-11
tags:
  - CV
  - SLAM
  - 3D视觉
  - 深度估计
  - NeurIPS2021
---

# DROID-SLAM: Deep Visual SLAM

> **作者**: Zachary Teed, Jia Deng (Princeton Vision & Learning Lab)
> **会议**: NeurIPS 2021
> **代码**: github.com/princeton-vl/DROID-SLAM（BSD-3-Clause 协议）
> **论文**: arXiv:2108.10869

## 核心贡献

基于深度学习的 **视觉 SLAM 系统**，支持单目、双目和 RGB-D 相机配置。

## 技术要点

- Frontend-backend 架构：前端处理帧，后端执行迭代优化
- 使用 **LiETorch**（PyTorch Lie 群操作）和 pytorch_scatter 做可微分优化
- 训练数据集：TartanAir（RGB + depth）
- 评测基准：TartanAir, EuRoC, TUM-RGBD, ETH3D-SLAM
- 硬件需求：推理 11GB GPU 显存，训练 24GB
- 多 GPU 支持（前端/后端可分配不同 GPU）
- 异步推理（前端/后端分离进程）

## 关联知识

- [[2026-05-11-TRAM-全局3D人体轨迹与运动重建]] — TRAM 使用 Masked DROID-SLAM 做相机估计
- [[2026-05-11-WHAM-世界坐标系人体运动重建]] — WHAM 可选使用 DROID-SLAM

## 思考

DROID-SLAM 是许多 3D 人体运动重建系统的 SLAM 骨干方案。TRAM 的 masked 变体是重要改进——通过忽略运动人体来获得更稳定的相机轨迹估计。
