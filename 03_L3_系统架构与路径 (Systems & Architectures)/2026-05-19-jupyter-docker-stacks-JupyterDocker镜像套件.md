---
source: "https://github.com/jupyter/docker-stacks/tree/main"
created: 2026-05-19
aliases:
  - Jupyter Docker Stacks
  - Jupyter 官方 Docker 镜像
tags:
  - layer/l3
  - type/tool
  - domain/ai-infra
---

# jupyter/docker-stacks — Jupyter 官方 Docker 镜像套件

> Jupyter 官方维护的一组开箱即用的 Docker 镜像，内置 JupyterLab 及常见数据科学/深度学习工具链。

## 用途

提供标准化的 Jupyter 容器化运行环境，免去手动配置 Python、CUDA、科学计算库的重复劳动。适合快速启动交互式实验环境、团队统一开发基线、以及教学/演示场景。

## 核心能力

- **多平台支持**：同时提供 `x86_64` 和 `aarch64` 架构镜像
- **CUDA 支持**：`pytorch-notebook` 和 `tensorflow-notebook` 提供 CUDA 启用版本（仅 `x86_64`）
- **多版本覆盖**：Python 3.7–3.13 版本镜像，基于 Ubuntu 20.04/22.04/24.04
- **镜像分层**：从基础层到专业层逐步递进

| 镜像 | 内容 |
|------|------|
| `jupyter/base-notebook` | 基础镜像：JupyterLab + 最小化系统依赖 |
| `jupyter/scipy-notebook` | 科学计算：base + NumPy/SciPy/Matplotlib/pandas 等 |
| `jupyter/datascience-notebook` | 数据科学：scipy + Julia/R 内核 |
| `pytorch-notebook` | PyTorch 环境（可选 CUDA） |
| `tensorflow-notebook` | TensorFlow 环境（可选 CUDA） |

## 使用方式

```bash
# 启动 JupyterLab
docker run -p 8888:8888 quay.io/jupyter/base-notebook

# 挂载本地工作目录
docker run -p 8888:8888 -v "${PWD}":/home/jovyan/work quay.io/jupyter/scipy-notebook

# 启用 CUDA 的 PyTorch 镜像
docker run --gpus all -p 8888:8888 quay.io/jupyter/pytorch-notebook
```

> 自 2023 年 10 月起镜像仅推送至 Quay.io，Docker Hub 上旧镜像不再更新。

## 适用边界

- 适合**交互式开发**和**教学场景**，不适合生产级推理部署
- 镜像体积较大（scipy-notebook ~3GB+），建议基于 `base-notebook` 定制
- 多用户场景需配合 JupyterHub 使用
- 如需深度定制 ML 实验环境，可结合 [[容器化管理实验环境最佳实践]] 中的 DevContainer + 分层镜像策略

## 关联笔记

- [[容器化管理实验环境最佳实践]] — 容器化 ML 实验环境的完整方法论与本项目的使用上下文；其中 [[容器化管理实验环境最佳实践#6.1 实战参考：env-factory 三层架构|6.1 节]] 的 env-factory 项目展示了类似的分层镜像策略
- [[2026-05-19-IaC基础设施即代码工具链|IaC 工具链综述]] — 从更宏观的基础设施视角理解容器管理与 IaC 的关系
