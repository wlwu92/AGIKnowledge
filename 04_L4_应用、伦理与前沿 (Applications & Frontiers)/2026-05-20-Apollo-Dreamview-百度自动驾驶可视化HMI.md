---
source: "https://apollo.baidu.com/docs/apollo/9.0/md_modules_2dreamview_2README.html"
created: 2026-05-20
aliases:
  - Apollo Dreamview
  - Apollo 9.0 Dreamview
tags:
  - layer/l4
  - type/tool
  - domain/robotics
---

# Apollo Dreamview — 百度自动驾驶可视化 HMI

## 用途

Dreamview 是百度 Apollo 自动驾驶开放平台（v9.0）的 HMI（Human-Machine Interface）模块，为开发者提供基于 Web 的动态 3D 可视化界面，用于实时观察自动驾驶各模块的输出。

## 核心能力

- **实时数据可视化**：在模拟世界中 3D 渲染自动驾驶模块输出的消息，包括定位、底盘状态、规划轨迹、感知障碍物、预测结果、路由响应等
- **多协议支持**：监听 protobuf 定义的多类消息——localization、chassis、planning、perception obstacles、prediction、routing response、monitor messages
- **前后端分离**：后端处理数据逻辑与消息订阅，前端提供 Web UI 渲染
- **灵活启动**：源码环境通过 `scripts/bootstrap.sh` 启动，包管理环境通过 `aem bootstrap start` 启动

## 使用方式

Dreamview 随 Apollo 9.0 整体构建。开发者可通过 Web 浏览器访问 Dreamview 界面，实时观察和调试车辆的感知、规划、决策等模块状态。

配置方面支持多套 HMI 模式配置、传感器预处理表（Camera-to-LiDAR、LiDAR-to-GNSS 映射）、数据采集表等。

## 适用边界

- 专为 Apollo 生态设计，不适用于其他自动驾驶平台
- 主要用于开发调试阶段的**可视化回放与实时监控**，不直接参与车辆控制
- 需要完整的 Apollo 后端服务支持才能正常工作；不可独立运行

## 关联笔记

- [[2026-05-20-Autoware-开源自动驾驶软件栈|Autoware]] — 另一主流开源自动驾驶软件栈
- [[2026-05-20-AVS-Uber自动驾驶可视化标准|AVS]] — Uber 的开源自动驾驶可视化标准，定位类似但跨平台
- [[2026-05-20-Hesai-ETX-禾赛800线激光雷达|Hesai ETX]] — 禾赛 L3/L4 自动驾驶激光雷达
