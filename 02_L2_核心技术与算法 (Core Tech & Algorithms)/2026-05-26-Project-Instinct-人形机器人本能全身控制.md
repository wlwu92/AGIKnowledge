---
source: "https://project-instinct.github.io/"
created: 2026-05-26
aliases:
  - Project Instinct
  - InstinctLab
tags:
  - layer/l2
  - type/paper
  - type/tool
  - domain/robotics
  - topic/humanoid-robot
  - topic/cross-embodiment-retargeting
  - method/optimization
  - entity/nvidia
---

# Project Instinct — 人形机器人本能级全身控制

## 概述

Project Instinct 是清华大学 IIIS（交叉信息研究院）和上海期智研究院联合提出的统一框架，涵盖算法、环境、数据集构建和部署，追求人形机器人的"本能级"全身控制（instinct-level whole-body control）。核心成果包括三篇论文和开源工具链。

## 核心贡献

1. **Embrace Collisions**（CoRL 2025）— 碰撞容忍的运动策略，使机器人不再避让所有碰撞而是合理利用接触
2. **Deep Whole-Body Parkour**（投稿中）— 全身跑酷运动生成
3. **Hiking in the Wild**（投稿中）— 野外远足地形自适应
4. 开源工具生态：InstinctLab（仿真环境）、Instinct_RL（训练框架）、Instinct Onboard（真机部署）、Robot Motion Editor

## 使用方式

### InstinctLab

GitHub: https://github.com/project-instinct/InstinctLab

InstinctLab 是基于 NVIDIA Isaac Sim / Isaac Lab 的强化学习仿真环境，用于训练人形机器人全身控制策略：

- 与核心 Isaac Lab 仓库解耦，独立开发维护
- 可作为 Omniverse 扩展运行
- 支持 ONNX 导出，通过 Instinct Onboard 直接部署到真机
- 实验以时间戳为唯一标识，每个实验为独立结构文件夹

## 适用边界

- 专注于足式/人形机器人全身控制，不适用于轮式或固定基座机器人
- 基于 Isaac Sim 生态，需要 NVIDIA GPU 和 Omniverse 环境
- 使用 CC BY-NC 4.0 许可证，不开放商业使用

## 关联笔记

- [[2026-05-26-Any2Track-任意干扰下运动跟踪|Any2Track]] — 同实验室（清华 + 期智）的运动跟踪框架
- [[topic/humanoid-robot]]
- [[topic/cross-embodiment-retargeting]]
