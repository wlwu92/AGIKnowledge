---
source: https://github.com/facebookresearch/MHR
created: 2026-05-12
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - domain/graphics
  - topic/human-mesh-recovery
  - topic/parametric-body-model
  - entity/mhr
  - entity/meta
---

# MHR (Momentum Human Rig) — 解剖学启发参数化人体模型

## 概述

Meta 开发的开源、解剖学启发的参数化 3D 人体模型，同时服务计算机图形学 (CG) 和计算机视觉 (CV) 社区。

**论文**: arXiv 2511.15586
**License**: Apache-2.0

## 参数化

- **身份参数**: 45 个参数（身体 20 + 头部 20 + 手部 5），范围 -3 ~ +3
- **全身姿态**: 204 个参数编码关节角度和缩放
- **面部表情**: 72 个参数，范围 -1 ~ +1

## 技术特点

- **7 级细节层次 (LOD 0-6)**: 平衡质量与计算开销
- **非线性姿态矫正**: 基于 MLP 稀疏激活的神经网络
- **PyTorch 集成**: GPU 加速推理
- **TorchScript**: 无需完整代码库即可使用
- **SMPL/SMPL-X 转换工具**: 与其他模型互操作

## 相关项目

MHR 是 SAM 3D Body 的基础网格表示。支持 PyMomentum 框架。
