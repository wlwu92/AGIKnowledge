---
source: https://github.com/mbotsch/GarmentMeasurements
created: 2026-05-12
tags:
  - layer/l2
  - type/tool
  - domain/graphics
  - topic/garment-measurement
  - topic/parametric-body-model
  - entity/cgal
  - entity/garmentcode
---

# GarmentMeasurements — 3D 服装形状采样与测量生成

## 概述

面向研究用途的 C++ 实现，处理 GarmentCodeData 数据集中的形状采样和测量提取部分。生成 3D 量体定制服装及缝纫图案。

**License**: GPL-3.0

## 核心功能

- **形状生成**: 基于 PCA 参数生成 3D 服装网格
- **测量提取**: 从生成网格提取结构化的 YAML 格式测量数据
- **蒙皮管线**: 输出 `.obj` 格式网格
- 与 **GarmentCode** 拟合工具配套使用

## 使用

```bash
cmake -S . -B build
cmake --build build
./generate_shapes        # 生成服装网格
./measurements output.obj measurements.yaml  # 提取测量
```

**依赖**: CGAL (Homebrew 安装) + FBX SDK 2020.3 (手动下载)
