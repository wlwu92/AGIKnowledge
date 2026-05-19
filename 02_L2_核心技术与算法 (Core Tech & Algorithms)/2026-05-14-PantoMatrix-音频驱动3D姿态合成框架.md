---
source: "https://github.com/PantoMatrix/PantoMatrix"
created: 2026-05-14
aliases:
  - PantoMatrix
tags:
  - type/tool
  - layer/l2
  - domain/embodied-ai
  - domain/cv
  - topic/audio-driven-motion
  - entity/pantomatrix
---

# PantoMatrix — 音频驱动 3D 姿态合成框架

> **PantoMatrix: Generating Face and Body Animation from Speech**
>
> **维护**: Haiyang Liu (since 2022)
> **代码**: https://github.com/PantoMatrix/PantoMatrix

## 用途

将语音音频转换为 3D 身体和面部动画的统一框架。支持本地推理、Hugging Face Space 在线试用、API 调用和 Colab 上手。

## 核心能力

包含三个渐进模型：

| 模型 | 年份 | 输出范围 | 核心方法 |
|------|------|---------|---------|
| **DisCo** | ACMMM 2022 | 上半身 + 双手 | 节奏-内容解耦控制 |
| **CaMN** | ECCV 2022 | 上半身 + 双手 | Cross-attention Body2Hands |
| **EMAGE** | CVPR 2024 | 全身 + 面部 | 掩码音频-姿态建模 |

输出格式：SMPL-X / FLAME 参数，支持导出 BVH 和 ARKit blendshape。

## 使用方式

**最简单**：上传音频到 [HF Space](https://huggingface.co/spaces/H-Liu1997/EMAGE)

**本地推理**：
```bash
git clone https://github.com/PantoMatrix/PantoMatrix.git
cd PantoMatrix/
bash setup.sh
source py39/bin/activate
python test_emage_audio.py --audio_folder ./audio --save_folder ./output --visualization
```

**程序化调用**：引入模型类，加载 Hugging Face 预训练权重，传入音频 tensor 获取 axis-angle 运动参数。

## 安装要求

- Python 3.9+（推荐虚拟环境）
- PyTorch（CUDA 可选）
- PyTorch3D（可视化可选，可用 `--nopytorch3d` 跳过）

## 评估工具

内置指标：FGD、Beat Consistency、L1 Diversity、LVD Face、MSE Face

## 适用边界

- **优势**：最完整的开源 audio-to-motion 项目，三篇论文渐进演进
- **局限**：纯运动学生成，无物理约束；推理速度不满足实时
- **数据**：基于 BEAT2 数据集（SMPLX+FLAME）

## 关联笔记

- [[2026-05-14-EMAGE-全身共语手势生成]] — EMAGE 论文笔记
- [[2026-05-14-Audio-Driven-Robot-Motion-音频驱动机器人运动全链路]] — 全链路综述
- [[2026-05-14-GestureLSM-潜在捷径共语手势生成]] — EMAGE 一作参与的 BEAT2 新 SOTA（ICCV 2025）
