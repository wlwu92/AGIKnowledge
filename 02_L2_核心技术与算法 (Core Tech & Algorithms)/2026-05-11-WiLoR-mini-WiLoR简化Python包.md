---
source: "https://github.com/warmshao/WiLoR-mini"
created: 2026-05-11
aliases:
  - WiLoR-mini
tags:
  - layer/l2
  - type/tool
  - domain/cv
  - topic/3d-reconstruction
  - topic/hand-reconstruction
---

# WiLoR-mini: WiLoR 简化 Python 包

> **作者**: warmshao（社区贡献者）
> **代码**: github.com/warmshao/WiLoR-mini（简化版，专注于推理）

## 核心贡献

将 [WiLoR](https://github.com/rolpotamias/WiLoR)（CVPR 2025）简化为 **pip-installable 的 Python 包**，专注于推理流程，自动下载模型权重。

## 技术要点

- pip 安装：`pip install git+https://github.com/warmshao/WiLoR-mini`
- 自动模型下载，无需手动获取 checkpoint
- 单 API 设计：`WiLorHandPose3dEstimationPipeline` + `predict()` 方法
- 支持 CUDA 和 CPU，支持 float16
- Python 3.10+ 依赖

## 关联知识

- [[2026-05-11-WiLoR-端到端3D手部定位与重建]] — 原始 WiLoR 完整代码库

## 思考

社区维护的推理简化版，移除了训练和评估代码。适合快速集成到现有项目中使用。
