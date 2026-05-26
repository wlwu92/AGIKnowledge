---
source: "https://github.com/sparkjsdev/spark"
created: 2026-05-20
aliases:
  - Spark
  - @sparkjsdev/spark
tags:
  - layer/l2
  - type/tool
  - domain/cv
  - domain/graphics
  - topic/3d-reconstruction
---

# Spark — 3D高斯溅射 THREE.js 渲染器

## 用途

Spark 是由 **World Labs** 开源的 3D Gaussian Splatting 渲染器，原生集成于 THREE.js 生态。它让开发者能在 Web 端（WebGL2）将高斯溅射场景与传统网格几何体融合渲染，目标是覆盖 "98%+ WebGL2 设备"，包括低端移动硬件。

## 核心能力

- **THREE.js 深度集成**：高斯溅射以 `SplatMesh` 对象加入场景，通过 `SparkRenderer` 渲染，与标准 THREE.js 几何体共存
- **多格式支持**：`.PLY`（含压缩变体）、`.SPZ`、`.SPLAT`、`.KSPLAT`、`.SOG`
- **动态操控**：支持 Splat 的变换、旋转、动画、实时颜色编辑、位移效果和骨骼动画
- **Shader Graph 系统**：在 GPU 端创建和编辑溅射，无需 CPU 回传
- **多视口渲染**：可同时渲染多个视角
- **正确排序**：多 Splat 对象间及与标准几何体间的深度排序

## 使用方式

```
npm install @sparkjsdev/spark
```

需要 THREE.js v0.180.0+。SplatMesh 实例像普通 THREE.js 网格一样放入场景，SparkRenderer 包装标准 WebGLRenderer 并处理高斯投影计算。

底层 Rust 组件编译为 WebAssembly，负责 Splat 文件解析、加速结构构建和每 Splat 计算等性能敏感操作；渲染管线通过自定义 GLSL Shader 完成 2D 高斯投影与 Alpha 合成。

## 适用边界

- 仅支持 **WebGL2**，尚无 WebGPU 后端
- 适用于需要在 Web 端展示或编辑高斯溅射场景的应用（产品展示、数字孪生、在线 3D 编辑）
- 不适用于需要原生性能的离线渲染或移动端原生应用场景
- 渲染质量受限于高斯溅射表示本身的近似性质（与基于网格的传统渲染相比有精度取舍）

## 关联笔记

- 无直接关联笔记（此为 vault 内首个高斯溅射相关笔记）。其核心技术源自 Kerbl et al. 的 *3D Gaussian Splatting for Real-Time Radiance Field Rendering*（SIGGRAPH 2023）。
