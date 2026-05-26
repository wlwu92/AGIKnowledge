---
source: "https://github.com/seaweedfs/seaweedfs"
created: 2026-05-26
aliases:
  - SeaweedFS
tags:
  - layer/l3
  - type/tool
  - domain/ai-infra
  - topic/distributed-storage
---

# SeaweedFS — 分布式对象与文件存储系统

## 用途

SeaweedFS 是一款 Go 语言编写的分布式存储系统，统一支持对象存储（S3 兼容）、文件系统和 Iceberg 表，专为海量小文件优化，支持数十亿文件规模。Apache 2.0 开源。

## 核心能力

- **O(1) 磁盘访问** — 中心 Master 仅管理 volume 级元数据，volume server 本地管理文件元数据，单次磁盘读取即可获取文件
- **极低元数据开销** — 每个文件仅约 40 字节元数据
- **S3 兼容 API** + 内置 **Iceberg REST Catalog**，支持 Spark、Trino、DuckDB 等数据湖仓
- **仅追加写入**（append-only）— 对 SSD 友好，避免碎片化
- **FUSE 挂载**、WebDAV、Hadoop 兼容文件系统
- **分层存储** — 热数据在本地 volume，温数据可 offload 到云存储
- **自动故障转移** — Master 高可用，无单点故障
- **卷级复制**（rack-aware 和 data-center-aware）+ 温存储纠删码
- **压缩、TTL 过期、AES256-GCM 加密**
- **Kubernetes CSI Driver 和 Operator**
- **不停机重均衡和压缩**

## 架构

- **Master Server** — 维护 volume ID → volume server 的映射，轻量可缓存
- **Volume Server** — 存储实际数据，每个 volume 32GB，内存中维护 blob 元数据（~16 bytes/个）
- **Filer（可选）** — 在 blob 存储上添加目录/POSIX 语义，后端元数据存储可选 MySQL、Postgres、Redis、Cassandra 等

写入采用仅追加模型，避免 SSD 碎片化随时间累积。

## 使用方式

- GitHub: https://github.com/seaweedfs/seaweedfs（32.5k ⭐, Apache 2.0）
- 语言：Go（83.7%）

## 适用边界

- 强项在海量小文件场景和水平扩展能力，增加容量只需启动新 volume server
- 不支持完整 POSIX 语义（除非通过 Filer），与传统文件系统用例有差距
- 追加写入模型对修改频繁的大文件不是最优选择

## 关联笔记

- [[2026-05-26-MinIO-AIStor-企业级AI数据存储|MinIO AIStor]] — 同为对象/文件存储，MinIO 侧重 S3 兼容性
- [[2026-05-26-JuiceFS-分布式POSIX文件系统|JuiceFS]] — 同为分布式存储，侧重 POSIX 兼容性
- [[topic/distributed-storage]]
