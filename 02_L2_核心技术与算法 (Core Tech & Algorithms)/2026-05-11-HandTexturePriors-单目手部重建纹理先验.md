---
source: "https://gkarv.github.io/hand-texture-module/"
created: 2026-05-11
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - topic/3d-reconstruction
  - topic/hand-reconstruction
  - venue/wacv-2026
---

# Enhancing Monocular 3D Hand Reconstruction with Learned Texture Priors

> **作者**: Giorgos Karvounas (ICS-FORTH, Univ. of Crete) 等
> **会议**: WACV 2026
> **代码**: github.com/gkarv/Hand-Texture-Module
> **论文**: arXiv:2508.09629

## 核心贡献

将 **纹理作为密集空间线索** 改进单目 3D 手部重建，通过可微渲染实现像素级对齐监督，无需真实纹理或多视角摄影棚数据。

## 技术要点

三步流水线：
1. **Sparse UV-RGB 采样** — 将可见手部像素投影到网格表面，获得 UV 坐标+颜色对
2. **Transformer Encoder + Conv Decoder** — 编码不规则像素 token，上采样为完整 UV 纹理图
3. **可微渲染光度监督** — 将纹理网格渲染回输入视图，计算像素级 loss，梯度回传优化纹理和几何

关键特性：
- 首个无需真实纹理的全手纹理学习框架
- 与 HaMeR plug-and-play 集成
- 对部分遮挡、自遮挡、运动模糊帧改进最明显
- 改善 MPJPE (3D 关节点误差) 和 MPVPE (顶点误差)

## 关联知识

- [[2026-05-11-HaMeR-3D手部重建]] — 本方法基于 HaMeR 构建纹理模块
- [[2026-05-11-MANO-手部参数化模型]] — 网格拓扑基于 MANO

## 思考

WACV 2026 工作，通过纹理先验为手部重建提供额外的光度监督信号。在部分遮挡场景下效果提升明显——当几何信息不足时，纹理线索可以补偿。
