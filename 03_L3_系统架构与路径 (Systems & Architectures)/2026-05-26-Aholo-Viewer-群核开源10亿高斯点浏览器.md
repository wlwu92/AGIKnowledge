---
source: "https://mp.weixin.qq.com/s/5qK1eSsewt86hFrNrbkY5w"
created: 2026-05-26
aliases:
  - Aholo Viewer
  - 群核 Aholo
tags:
  - layer/l3
  - type/tool
  - domain/cv
  - domain/ai-infra
  - topic/3d-reconstruction
  - method/inference-optimization
  - entity/modelscope
---

# Aholo Viewer — 群核开源 10 亿级高斯点 Web 渲染引擎

## 用途

Aholo Viewer 是群核科技（Manycore Tech）开源的 Web 端 3D Gaussian Splatting 高性能渲染引擎，支持在浏览器中流畅加载和渲染 **10 亿级**高斯点，同时提供完整的空间智能平台能力。

## 核心能力

- **10 亿高斯点渲染**：性能超越李飞飞团队的 Spark 2.0（最大 1 亿点），内存占用减少 50%，加载速度快 1 倍，渲染速度快 3 倍
- **Chunk-based LOD Tree**：与 Spark 2.0 的 Splat-based LOD 不同，将 3DGS 数据切分为数据块（chunk），为每个 chunk 生成不同 LOD 层级，内存调度更高效、扩展性更强
- **多精度数据结构**降低显存占用
- **Morton Sort + detail culling** 优化数据访问
- 兼容主流 3DGS 格式，提供数据格式转换、碰撞体生成等工具

## 空间智能平台

群核同步开放了完整的空间智能平台 API：
- **空间重建**：视频拍摄即可 1:1 复刻物理世界
- **云端渲染**：支持光线追踪、3DGS + Mesh 混合渲染、视频流传输
- **3D AI 模型生成**：图生 3D / 文生 3D
- **3D 数据集**：InteriorGS 等机器人/智能体训练用语义数据集

## 使用方式

- 主页：https://aholojs.dev/zh-CN/
- GitHub：https://github.com/manycoretech/aholo-viewer

## 适用边界

- 适用于需要浏览器端消费大场景 3DGS 数据的场景（如数字孪生、3D 互联网、空间智能展示）
- 不适用于需要原生性能的离线渲染或游戏引擎内嵌场景
- Chunk-based LOD 对不规则稀疏场景的适配性有待验证

## 关联笔记

- [[topic/3d-reconstruction]]
