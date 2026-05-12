---
source: "https://github.com/yufu-wang/PromptHMR"
created: 2026-05-11
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - topic/3d-reconstruction
  - topic/human-mesh-recovery
  - topic/parametric-body-model
  - topic/prompting
  - method/transformer
  - entity/smpl-x
  - venue/cvpr-2025
---

# PromptHMR: Promptable Human Mesh Recovery

> **作者**: Yufu Wang, Yu Sun, Priyanka Patel, Kostas Daniilidis, Michael J. Black, Muhammed Kocabas
> **机构**: UPenn, Meshcapade, Max Planck Institute for Intelligent Systems
> **论文**: arXiv:2504.06397 | CVPR 2025
> **项目页**: [yufu-wang.github.io/phmr-page](https://yufu-wang.github.io/phmr-page)
> **代码**: [github.com/yufu-wang/PromptHMR](https://github.com/yufu-wang/PromptHMR)

## 核心贡献

提出 **Promptable（可提示的）** 3D 人体姿态与形状（HPS）估计框架，将 HPS 问题重构成通过 **空间提示** 和 **语义提示** 引导的网格恢复任务。与 crop-based 方法不同，**处理全图以保留场景上下文**。

## 方法架构

```
输入图片 ──→ Vision Transformer ──→ 图像嵌入 ──┐
                                                ├──→ SMPL-X Decoder ──→ SMPL-X 参数
空间/语义提示 ──→ Mask/Prompt Encoder ──→ 提示 Tokens ──┘
(可选) 相机内参 ──→ 内参嵌入 ──────────────┘
```

### Key Components

| 组件 | 来源 |
|------|------|
| Promptable 骨干设计 | SAM（Facebook） |
| 多人体基线 | MultiHMR & BEV |
| Video Head 设计 | **GVHMR** |
| 标注方案 | CamHMR |
| 双人交互 | BUDDI |
| 图像编码器 | DINOv2 Vision Transformer |
| 可视化 | Viser & Gloss |
| Pipeline 组件 | Detectron2, SAM2, DROID-SLAM, Metric3D, ViTPose, SPEC |

## 提示类型

### 空间提示（引导"在哪里"恢复）
- **(a) 人脸边界框** — 适用于拥挤场景，人脸框即可定位
- **(b) 局部或完整人体检测框** — 标准人体检测
- **(c) 分割掩码** — 像素级定位

### 语义提示（引导"是什么"）
- **(d) 人与人交互标签** — 用于近距离接触场景，消除歧义
- **(e) 自然语言身体形状描述** — 例如 "a muscular and tall male"，优化形状预测
- 语言和交互提示为**可选项**，但提供后可提升精度

## 视频版本（PromptHMR-video）

- 集成 **时序 Transformer 层** 实现时间连贯的运动估计
- 通过 **度量 SLAM** 融合实现**世界坐标系**重建
- Video Head 设计继承自 [[2026-05-11-GVHMR-重力视角人体运动恢复|GVHMR]]
- 训练数据：**BEDLAM1** + **BEDLAM2**（超 800 万张合成图像，增加姿态/体型变化、鞋子、发丝、多样化相机运动）
- 提供四个 checkpoint：
  - `phmr_b1.ckpt`（BEDLAM1）
  - `phmr_b2.ckpt`（BEDLAM2）
  - `phmr_b1b2.ckpt`（联合训练）
  - `bedlam2_phmr`
- 支持**静态和运动相机**两种模式
- 输出 MCS / GLB 格式，可导入 Blender

## 与 TRAM 的关系

PromptHMR（CVPR 2025）与 [[2026-05-11-TRAM-全局3D人体轨迹与运动重建|TRAM]]（arXiv 2024）来自共同一作 **Yufu Wang**，同属 UPenn Kostas Daniilidis 组的工作线。视频版本的度量 SLAM 集成方案延续了 TRAM 的 masked DROID-SLAM 思路，可视为 TRAM 的提示式进化版本。

| 维度 | TRAM | PromptHMR |
|------|------|-----------|
| 核心创新 | SLAM 集成到 4D 重建流水线 | Promptable 框架 + 多模态提示 |
| 图像编码器 | HMR2.0 骨干 | DINOv2 Vision Transformer |
| 处理方式 | crop-based | 全图处理 |
| 提示能力 | 无 | 空间 + 语义提示 |
| 身体模型 | SMPL | SMPL-X |
| 交互处理 | 无专门设计 | 跨人物交叉注意力 |
| 语言指导 | 无 | 自然语言形状描述 |
| 发表 | arXiv 2024 | CVPR 2025 |

## 评估结果

在多个基准上达到 **State-of-the-Art**：
- **EMDB** — 视频 3D 人体评估
- **3DPW** — 户外人体姿态
- **RICH** — 复杂交互场景
- **Hi4D** — 4D 人体交互
- **CHI3D** — 接触场景
- **HBW** — 野外人体

训练代码**未开源**（"due to licensing agreements"）。

## 关联笔记

- [[2026-05-11-TRAM-全局3D人体轨迹与运动重建]] — 同组工作，SLAM 集成先导
- [[2026-05-11-GVHMR-重力视角人体运动恢复]] — Video Head 设计来源
- [[2026-05-11-WHAM-世界坐标系人体运动重建]] — 类似目标的世界坐标系重建

## 思考

PromptHMR 的核心价值在于将 HPS 从"黑盒检测+重建"范式转向**交互式、可引导的提示范式**。语言提示解决"体型歧义"——这是纯视觉方法难以克服的固有问题。全图处理避免了 crop 带来的上下文丢失，在拥挤场景中尤为关键。视频版本通过传承 TRAM 的 SLAM 集成思路，实现了从单帧到时序的自然延伸。
