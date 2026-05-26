---
source: "https://docs.min.io/aistor/"
created: 2026-05-26
aliases:
  - MinIO AIStor
tags:
  - layer/l3
  - type/tool
  - domain/ai-infra
  - topic/distributed-storage
---

# MinIO AIStor — 企业级 AI 数据存储

## 用途

MinIO AIStor 是 MinIO 推出的商业企业级 AI 数据存储产品，专为 AI 数据、Agentic 计算和分析工作负载设计的 Exascale 级数据存储，提供对象存储（S3）、表格数据（Iceberg）和文件访问（SFTP）的多协议统一平台。

## 核心能力

- **多协议支持**：原生支持 S3 API（对象）、Iceberg（表）、SFTP（文件）
- **Exascale 规模**：面向 AI 工作负载的高性能大规模存储
- **企业安全**：服务端加密、FIPS 模式、TLS 网络加密、LDAP/OIDC/Keycloak/Azure AD 身份管理
- **数据管理**：对象版本控制、生命周期管理（分层/过期）、对象锁定/不可变性、存储桶复制、批处理框架
- **可观测性**：Prometheus/InfluxDB 指标、审计日志、OpenTelemetry 链路追踪、健康检查探针
- **多平台部署**：Kubernetes（含 OpenShift）、Linux（Ubuntu/RHEL）、Container（Docker/Podman）、macOS、Windows
- **附加工具**：Delta Sharing 表共享、存储桶通知（Kafka、RabbitMQ、PostgreSQL 等）、对象 Lambda 转换

## 使用方式

- 文档：https://docs.min.io/aistor/
- 基于开源 MinIO 构建，但使用 MinIO Software License（商业许可）

## 适用边界

- 适用于需要统一存储 AI 训练数据、模型工件和 Agent 数据的场景
- 与 AWS S3 API 兼容，适合作为私有化 AI 数据湖底座
- 商业产品，不适合预算有限的个人项目或小团队

## 关联笔记

- [[topic/distributed-storage]]
