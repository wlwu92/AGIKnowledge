---
source: "https://h-liu1997.github.io/Video-Motion-Graphs/"
created: 2026-05-11
tags: [video-generation, frame-interpolation, diffusion-models, CV, motion-graphs]
---

# Video Motion Graphs — 视频运动图插帧

> 东京大学 & Adobe Research 合作项目。提出基于运动感知的视频插帧框架 HMInterp，生成平滑真实的中间帧。

## 核心方法

- **Motion Guidance Interpolation**: 相较 Linear Blending 更接近真实运动轨迹
- **Improved Reference Decoder**: 对比 Vanilla (SD)、Consistency (DALLE)、DualRef (ToonCrafter)、Temporal (SVD)、DupRef ToonCrafter 等基线
- 与 FILM、VFIFormer、DCInterp、ACInterp 等商业/开源模型对比

## 应用

- Music-to-Dance 视频检索与生成

## 状态

- 模型权重和代码待法律审查后发布
