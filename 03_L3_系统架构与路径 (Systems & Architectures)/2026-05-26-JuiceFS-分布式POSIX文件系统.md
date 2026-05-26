---
source: "https://juicefs.com/docs/zh/community/introduction/"
created: 2026-05-26
aliases:
  - JuiceFS
tags:
  - layer/l3
  - type/tool
  - domain/ai-infra
  - topic/distributed-storage
---

# JuiceFS — 云原生分布式 POSIX 文件系统

## 用途

JuiceFS 是一款高性能分布式文件系统，采用"数据与元数据分离"架构（数据存对象存储、元数据存独立数据库），提供完整的 POSIX 兼容性，适用于大数据分析、机器学习、Kubernetes 存储和共享工作空间等场景。Apache 2.0 开源。

## 核心能力

- **完整 POSIX 兼容** — 通过全部 8,813 个 pjdfstest 测试，可像本地磁盘一样挂载使用
- **HDFS 兼容** — 提供 Java SDK，兼容 Hadoop 2.x/3.x 生态
- **S3 Gateway** — 提供 S3 协议访问接口
- **Kubernetes CSI Driver** — 容器化环境原生支持
- **强一致性** — 修改操作即时对所有挂载点可见
- **数据加密** — 支持传输中和静态加密
- **全局文件锁** — BSD locks (flock) 和 POSIX record locks (fcntl)
- **数据压缩** — LZ4 / Zstandard 算法
- **元数据引擎可选** — Redis、MySQL、SQLite、TiKV

## 架构

- **JuiceFS Client** — 协调对象存储和元数据引擎，暴露 POSIX/Hadoop/Kubernetes/S3 Gateway 接口
- **Data Storage** — 本地磁盘、公有/私有云对象存储、HDFS
- **Metadata Engine** — 存储文件元数据（名称、大小、权限、目录结构）

文件被分为固定大小 Chunk（默认 64 MiB），每个 Chunk 由若干 Slice 组成，再切分为固定大小 Block（默认 4 MiB）存储于对象存储。

## 使用方式

- GitHub: https://github.com/juicedata/juicefs（13.6k ⭐, Apache 2.0）
- 文档: https://juicefs.com/docs/zh/community/introduction/
- 三种版本：Community Edition（开源免费）、Cloud Service、Enterprise Edition

## 适用边界

- 强项在云原生环境下的弹性共享存储，延迟取决于底层对象存储性能
- 不适合需要极低延迟本地盘性能的场景
- 有性能开销（FUSE 挂载引入的用户态开销以及元数据引擎的查询延迟）

## 关联笔记

- [[2026-05-26-MinIO-AIStor-企业级AI数据存储|MinIO AIStor]] — 同为 AI 数据存储方案，侧重对象存储
- [[2026-05-26-SeaweedFS-分布式存储系统|SeaweedFS]] — 同为分布式存储，架构思路不同
- [[topic/distributed-storage]]
