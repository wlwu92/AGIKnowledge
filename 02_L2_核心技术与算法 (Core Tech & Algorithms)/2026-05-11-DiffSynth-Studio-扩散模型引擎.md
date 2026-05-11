---
source: "https://github.com/modelscope/DiffSynth-Studio/tree/main"
created: 2026-05-11
tags:
  - CV
  - 扩散模型
  - 训练框架
  - 推理优化
  - ModelScope
---

# DiffSynth-Studio: 统一扩散模型引擎

> **维护者**: ModelScope 社区
> **协议**: Apache-2.0
> **论文**: DiffSynth (ECML PKDD 2024), Diffutoon (IJCAI 2024)

## 核心定位

ModelScope 社区开发的统一扩散模型引擎，覆盖图像/视频/音频生成的训练、推理和部署。采用双项目结构：**DiffSynth-Studio**（学术前沿）+ **DiffSynth-Engine**（工业稳定部署）。

## 关键特性

| 特性 | 说明 |
|------|------|
| **VRAM 管理** | 层级磁盘卸载，根据可用显存自动控制参数加载，支持 2–10GB 显卡运行大模型 |
| **训练框架** | Split Training（两阶段）、Differential LoRA、FP8 训练 |
| **Diffusion Templates** | 可微调扩散模型的插件框架，降低可控生成门槛 |
| **模型谱系追踪** | 记录模型族谱（如 Qwen-Image → ControlNet → EliGen）|

## 支持任务

- **图像**: Text-to-Image (FLUX, Qwen-Image, SD)、图像编辑、ControlNet、Inpainting、分层控制
- **视频**: Text-to-Video / Image-to-Video (Wan, HunyuanVideo, CogVideoX)、音频驱动视频
- **音频**: Text-to-Audio (LTX-2.3)
- **加速**: Qwen-Image-Distill 约 5× 加速

## 技术栈

Python + PyTorch，支持 FP32/FP16/FP8，默认模型源 ModelScope，核心学术成果发表于 ECML PKDD / IJCAI。

## 关联知识

- [[Stable Diffusion]] — 基础扩散模型
- [[FLUX]] — 支持的模型之一

## 思考

ModelScope 在扩散模型生态中的定位类似 HuggingFace Diffusers，但更侧重中文社区和工业部署。双项目结构（Studio vs Engine）的设计值得关注。
