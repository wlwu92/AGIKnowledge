---
source: "https://arxiv.org/abs/2604.21681"
created: 2026-05-11
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - topic/human-mesh-recovery
  - topic/pose-estimation
  - method/transformer
  - venue/iclr-2026
---

# Sapiens2: High-Resolution Human-Centric Vision Transformers

> **作者**: Rawal Khirodkar, He Wen, Julieta Martinez 等 (Facebook Research)
> **会议**: ICLR 2026
> **代码**: github.com/facebookresearch/sapiens2（Custom License）
> **模型规模**: 0.1B–5B 参数（6 个规格）

## 核心贡献

Sapiens 第二代，基于 10 亿张高质量人体图像预训练的统一人体视觉模型族，支持 1K–4K 原生分辨率。

## 技术要点

- **统一预训练目标**: 掩码图像重建 + 自蒸馏对比学习，兼顾低级细节与高级语义
- **数据规模**: 10 亿张精选人体图像，改进任务标注质量和多样性
- **架构改进**: 融合前沿模型进展，4K 变体使用 windowed attention 处理长空间上下文
- **新增能力**: pointmap 和 albedo 估计（相比第一代）
- **backbone 模块可独立使用**: 单文件无依赖，仅需 torch + safetensors

## 模型规格

| 模型 | 参数量 | FLOPs | Embed Dim | Layers | Heads |
|------|--------|-------|-----------|--------|-------|
| Sapiens2-0.1B | 0.114B | 0.342T | 768 | 12 | 12 |
| Sapiens2-0.4B | 0.398B | 1.260T | 1024 | 24 | 16 |
| Sapiens2-0.8B | 0.818B | 2.592T | 1280 | 32 | 16 |
| Sapiens2-1B | 1.462B | 4.715T | 1536 | 40 | 24 |
| Sapiens2-1B (4K) | 1.607B | — | 1536 | 40 | 24 |
| Sapiens2-5B | 5.071B | 15.722T | 2432 | 56 | 32 |

> 所有模型 patch size 16，训练分辨率 1024×768，需 Python ≥3.12 和 PyTorch ≥2.7。checkpoint 在 Hugging Face 发布。

## 主要结果

| 任务 | 提升 vs Sapiens Gen 1 |
|------|----------------------|
| Pose 估计 | +4 mAP |
| Body-part 分割 | +24.3 mIoU |
| Normal 估计 | 45.6% 更低角度误差 |

## 关联知识

- [[4DHumans]] — 同一团队人体重建工作
- [[Sapiens]] — 第一代模型

## 思考

10 亿张人体图像预训练 + 统一架构覆盖多个人体视觉任务，方向上和 SAM 的"统一视觉基础模型"思路一致，但聚焦在人体领域。4K 分辨率的 windowed attention 处理高精度人体理解是实用方向。
