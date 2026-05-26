---
source: "https://research.nvidia.com/labs/dair/dream-lift-animate/"
created: 2026-05-26
aliases:
  - DLA
  - Dream, Lift, Animate
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - topic/3d-reconstruction
  - topic/human-mesh-recovery
  - method/diffusion-model
  - method/transformer
  - entity/nvidia
  - entity/smpl-x
  - venue/3dv-2026
---

# DLA — 单图可动画化高斯虚拟人像

## 概述

DLA（Dream, Lift, Animate）是 NVIDIA 联合 ETH Zurich 提出的框架，从单张照片即可创建可动画化的 3D 人体高斯虚拟人像（animatable Gaussian avatar），无需任何后处理即可实时渲染。论文发表于 3DV 2026。

## 核心贡献

1. 完整的单图→可动画化实时渲染虚拟人像 pipeline，无需后处理
2. 将无结构 3D 高斯表示与结构化 UV 空间高斯编码结合，桥接生成式扩散与可动画化表示
3. 在 ActorsHQ 和 4D-Dress 数据集上达到 SOTA，在感知质量和光度精度上超越 IDOL、DreamGaussian、SiTH、SIFU
4. 支持虚拟人像编辑和跨主体插值
5. 建模 pose 依赖效果（反射、几何校正）和 view 依赖效果

## 方法机制

三阶段 pipeline：

1. **Dream**：使用视频扩散模型从单张输入图像生成 plausible 的多视角图像，"想象"出人物未见角度
2. **Lift**：将多视角图像重建为无结构 3D 高斯，通过 Transformer 编码器将其映射到 SMPL-X 体模型的 UV 空间结构化潜码中
3. **Animate**：基于法线、相对顶点位置和相机参数（Plücker rays）条件，解码出 pose 和视角感知的高斯参数，实现可动画化实时渲染

## 关联笔记

- [[2026-05-26-CARI4D-类别无关4D人机交互重建|CARI4D]] — NVIDIA 同一研究组的 4D 人机交互重建
- [[topic/3d-reconstruction]]
- [[topic/human-mesh-recovery]]

## 判断与局限

- 三阶段设计清晰解耦，但依赖视频扩散模型生成的多视角质量，可能存在视角覆盖盲区
- 目前仅针对人体，未扩展到更广泛的物体类别
- SMPL-X UV 空间映射带来了结构化优势，但也受限于 SMPL-X 模型的表达能力
