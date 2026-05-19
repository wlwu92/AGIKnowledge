---
created: 2026-05-13
note_type: survey
tags:
  - layer/l3
  - type/survey
  - domain/ai-infra
  - topic/distributed-storage
layer: l3
status: processed
---

# 3FS（Fire-Flyer File System）— AI 原生并行文件系统

## 概述

**3FS（Fire-Flyer File System）** 是 DeepSeek 开源的**高性能分布式并行文件系统**，专为 AI 训练和推理工作负载设计。它是支撑 DeepSeek V3/R1 训练推理的核心存储基础设施。

- **开源时间**：2025 年 2 月 28 日（开源周收官日）
- **许可证**：Apache 2.0 / MIT
- **GitHub**：https://github.com/deepseek-ai/3FS
- **配套工具**：Smallpond（基于 DuckDB + 3FS 的 PB 级数据处理框架）

---

## 核心架构

3FS 采用**计算与存储分离的分解式架构**，由四个核心组件组成，全部基于 RDMA 通信：

```
┌─────────────────────────────────────────────────────┐
│                   3FS Cluster                         │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  Mgmtd (集群管理服务)                          │   │
│  │  • 节点注册与心跳检测                          │   │
│  │  • 配置分发与 chain table 维护                 │   │
│  │  • Leader 选举（基于 ZooKeeper/etcd/FDB）      │   │
│  └──────────────────┬───────────────────────────┘   │
│                      │                                 │
│  ┌──────────────────▼───────────────────────────┐   │
│  │  Meta (元数据服务)     ───→  FoundationDB     │   │
│  │  • 无状态设计，可水平扩展                    │   │
│  │  • 管理 inode、目录条目                      │   │
│  │  • 支持 Serializable Snapshot Isolation      │   │
│  │  • 会话管理（客户端断连后文件同步）           │   │
│  └──────────────────┬───────────────────────────┘   │
│                      │                                 │
│  ┌──────────────────▼───────────────────────────┐   │
│  │  Storage (存储服务)      ───→ 本地 NVMe SSD  │   │
│  │  • Chunk 存储接口                            │   │
│  │  • CRAQ 链式复制协议                         │   │
│  │  • io_uring 高效异步 I/O                     │   │
│  │  • AllocateWorker / PunchHoleWorker /        │   │
│  │    AioReadWorker 分工处理                    │   │
│  └──────────────────┬───────────────────────────┘   │
│                      │                                 │
│  ┌──────────────────▼───────────────────────────┐   │
│  │  Client (客户端)                              │   │
│  │  • FUSE Client：标准 POSIX 接口               │   │
│  │  • Native Client：高性能 API，零拷贝           │   │
│  │  • 共享内存（/dev/shm）+ IoRing 机制           │   │
│  │  • Direct I/O 直通 SSD                       │   │
│  └──────────────────────────────────────────────┘   │
│                                                       │
│  全部内部通信：RDMA（InfiniBand 或 RoCE）              │
└─────────────────────────────────────────────────────┘
```

### 组件详解

#### Mgmtd（集群管理服务）
- 负责集群节点间的协调
- 维护 chain table（复制链配置表）
- 检测节点故障并触发 chain table 更新
- 使用 ZooKeeper/etcd 或 FoundationDB 实现 Leader 选举

#### Meta（元数据服务）
- **无状态设计**：元数据全部持久化在 FoundationDB 中，Meta 服务本身不存状态
- 可水平扩展，扩缩容无需数据迁移
- 文件元数据以 `INOD` + 64bit ID 为前缀存储在 FDB 中
- 目录条目以 `DENT` + 父 inode ID + 条目名为前缀存储
- 文件长度默认每 5 秒由客户端报告更新（close/fsync 时精确查询）
- Chunk 位置通过 round-robin 策略从 chain table 中选择（带随机 seed 打散）

#### Storage（存储服务）
- 管理本地 NVMe SSD 上的 Chunk 数据
- 三种 Worker 线程：
  - **AllocateWorker**：分配新的 Chunk 空间
  - **PunchHoleWorker**：回收删除的 Chunk 空间
  - **AioReadWorker**：通过 io_uring 队列实现高效异步读
- 实现 CRAQ 链式复制协议

#### Client（客户端）
- **FUSE Client**：标准 POSIX 接口，低集成门槛
- **Native Client**：高性能 API
  - 通过共享内存（/dev/shm）+ IoRing 实现用户进程与 FUSE 进程间零拷贝
  - 使用 Direct I/O，避免文件缓存，减少 CPU/内存开销

---

## CRAQ 链式复制协议

CRAQ（Chain Replication with Apportioned Queries）是 3FS 的核心一致性协议，采用 **write-all-read-any** 策略。

### 基本结构

每个数据 Chunk 属于一条复制链（Chain），链中有序排列多个 Storage Target：

```
Chain: [Head] → [Target 2] → [Target 3] → ... → [Tail]
```

### 写入流程

```
Client → Head → Target 2 → Target 3 → Tail
                                          │ 到达尾部后提交
                                          ▼
Client ← Head ← Target 2 ← Target 3 ← Tail ← ACK
```

1. Client 向 **Head** 发送写请求
2. 每个节点收到后：
   - 检查 chain version 是否匹配
   - 通过 RDMA Read 拉取数据
   - 从 Lock Manager 获取 Chunk 锁（同一 Chunk 的写请求串行化）
   - 将当前 committed version 读入内存 → apply update → 存储为 **pending version**
   - 每个 Target 最多存储两个版本：committed（v）和 pending（u = v+1）
   - 若非 Tail，则转发给后继节点
3. **Tail** 收到后，原子地将 pending 替换为 committed，然后向上游发 ACK
4. ACK 反向传播，每个节点收到后提交 pending → committed，释放 Chunk 锁

### 读取流程

- 若 Target 上只有 **committed version**，直接返回
- 若为 **pending（脏）状态**，查询 Tail 获取最新版本

### 故障处理

- Mgmtd 检测节点故障 → 更新 chain table → 广播新配置
- 写入中的节点：向前驱/后继重试，直到新 chain 生效
- 恢复流量使用 **balanced incomplete block design** 优化，避免热点饱和

### 性能权衡

| 维度 | CRAQ 特性 | AI 场景适配性 |
|------|----------|--------------|
| 写入延迟 | **较高**（需串行传播到 Tail） | 训练读远多于写，可接受 |
| 读取扩展 | **优秀**（任意副本可响应） | 数据集加载、KVCache 读密集场景理想 |
| 一致性 | **强一致** | Checkpoint 等场景需要 |

---

## 文件分布与条带化

### Chunk 分布

- 文件被分割为固定大小 Chunk（默认 **512KB**）
- 通过条带化 + 轮询方式分布到多个复制链
- 每个 Chunk 跨 3 个 Storage Target 复制（默认）

### Chain Table 示例

6 节点（A-F），每节点 1 块 SSD，5 个 Storage Target/SSD，3 副本：

| Chain | Version | Head | Target 2 | Tail |
|-------|---------|------|----------|------|
| 1 | 1 | A1 | B1 | C1 |
| 2 | 1 | D1 | E1 | F1 |
| 3 | 1 | A2 | B2 | C2 |
| ... | ... | ... | ... | ... |
| 10 | 1 | D5 | E5 | F5 |

- Version 递增：每有节点离线就更新
- 仅 **Primary Cluster Manager** 可修改 Chain Table
- 不同 workload 可使用不同的 Chain Table（节点互斥）

### 负载均衡恢复

当节点故障时，使用 **balanced incomplete block design**（整数规划求解）将恢复流量均匀分布到剩余 SSD，防止特定节点被压垮。

---

## 元数据存储

- 底层：**FoundationDB**（事务性 KV 存储）
- 隔离级别：**Serializable Snapshot Isolation（SSI）**
- Inode 键格式：`"INOD"` + 64bit ID
- 目录条目键格式：`"DENT"` + 父 inode ID + 条目名
- Chunk 位置：Chunk ID = inode ID + chunk index，从 chain table 中 round-robin 选取
- 文件长度：默认每 5 秒客户端报告更新；close/fsync 时通过查询最后一个 Chunk 精确获取

---

## 性能数据

### 官方测试结果

| 指标 | 集群配置 | 结果 |
|------|---------|------|
| **聚合读取吞吐** | 180 存储节点 + ~500 客户端节点，每节点 2×200Gbps IB | **~6.6 TiB/s**（含训练背景流量） |
| **GraySort** | 25 存储 + 50 计算节点，存储 2×400Gbps，计算 1×200Gbps | **3.66 TiB/min**（110.5 TiB / 30分14秒） |
| **KVCache 查找峰值** | 单客户端节点，200Gbps IB | **40+ GiB/s** |

### 存储节点规格

| 部件 | 规格 |
|------|------|
| NVMe SSD | 16× **14TB** |
| 每节点原始容量 | 224 TiB |
| 网络 | 2× **200Gbps InfiniBand** |
| 集群规模（性能测试） | 180 存储节点 |

---

## AI 工作负载专项优化

| 场景 | 3FS 优化方式 | 与通用系统的差异 |
|------|-------------|-----------------|
| **数据预处理** | Smallpond 框架在 3FS 上实现 PB 级排序（3.66 TiB/min） | 训练数据管道与存储深度集成 |
| **数据集加载** | 跨计算节点**随机访问**训练样本，无需预取或 shuffle | RDMA 随机读性能接近顺序读 |
| **Checkpoint 保存/加载** | CRAQ 保证强一致 + 条带化并行读写 | 大规模训练的 checkpoint 秒级完成 |
| **KVCache 推理** | SSD 作为 DRAM 的低成本替代，单节点 40+ GiB/s | **独有设计**：其他文件系统未考虑此场景 |
| **嵌入向量搜索** | 低延迟读取支持高速向量检索 | 高并发随机读 |

---

## 与主流系统对比

### 架构对比

| 维度 | **3FS** | **Lustre** | **CephFS** | **BeeGFS** |
|------|---------|-----------|-----------|-----------|
| **定位** | AI 训练推理专用 | HPC 通用 | 统一存储 | HPC + AI 通用 |
| **一致性协议** | **CRAQ** 链式复制 | 分布式锁 + 租约 | RADOS + PG 复制 | 分布式锁 |
| **元数据存储** | FoundationDB（**无状态**） | 内核态专用 MDS（有状态） | RADOS 对象存储 | ext4/XFS 本地 FS（有状态） |
| **元数据扩展** | ✅ 水平扩展（无状态） | ❌ 双 MDS（不可扩展） | ✅ 多 MDS 横向扩展 | ✅ 分布式元数据 |
| **最小 Chunk** | **512KB** | 1MB+ | 4MB（默认对象） | 可配置 |
| **客户端** | FUSE + Native（RDMA 零拷贝） | 内核模块（需 patch） | 内核 / FUSE | 内核模块（无需 patch） |
| **RDMA 原生** | ✅ **深度集成** | ✅ 支持 | ❌ 社区版不支持 | ✅ 原生支持 |
| **KVCache 支持** | ✅ **专用设计** | ❌ | ❌ | ❌ |
| **硬件假设** | **全 NVMe + RDMA IB** | HDD/SSD 混合 | HDD/SSD 混合 | HDD/SSD 混合 |
| **开源时间** | 2025.2 | 2003 | 2012 | 2007 |

### 性能量级对比

```
单客户端吞吐（GB/s）：
  CephFS      █ 1
  Lustre      ████████ 4-8
  BeeGFS      █████████ 5-10
  3FS         ████████████████████████████████████ 40+（单节点 KVCache）
  云厂商 PFS  ████████████████████████████████████████████ 50

聚合吞吐（TB/s）：
  CephFS      █ 0.07（10节点 NVMe）
  Lustre      ██████ 1+（大规模）
  BeeGFS      █████ 0.5+
  3FS         ████████████████████████████████████████ 6.6（180节点）
  云厂商 PFS  ████████████████████████████████████████████████ 2
```

> 注：3FS 是自建能达到的顶尖水平（6.6 TiB/s），云厂商 PFS 是托管上限（2 TB/s）。但 3FS 数字来自 180 节点集群，单节点吞吐不及云 PFS。

---

## 配套生态：Smallpond

Smallpond 是基于 **DuckDB** 和 **3FS** 的轻量级数据处理框架：

- 可扩展至 **PB 级数据集**
- 无需长期运行的服务
- 与 3FS 深度集成，I/O 不成为瓶颈
- GraySort 性能与 3FS 自身指标一致（3.66 TiB/min）

---

## 分析评价

### 核心优势

1. **AI 原生设计**：不是通用系统改 AI，而是从第一天起为 AI 训练推理定制
2. **KVCache 卸载**：唯一考虑推理 KVCache 缓存路径的文件系统，实用价值高
3. **CRAQ 协议**：写串行化、读并行的设计完美匹配 AI 场景（读远多于写）
4. **无状态元数据**：基于 FoundationDB 的设计让 Meta 服务扩缩容远易于 Lustre 和 Ceph
5. **软硬件协同**：io_uring、Direct I/O、零拷贝、RDMA——把现代硬件的性能压榨到极致
6. **全流程闭环**：数据预处理 → 加载 → checkpoint → KVCache 推理，一套系统覆盖

### 主要局限

1. **硬件门槛极高**：需要全 NVMe + RDMA InfiniBand，中小团队几乎无法复现
2. **AI 专用性强**：不适用于通用存储场景
3. **RoCE 适配存疑**：公开数据全部基于 InfiniBand，RoCE 网络能否达到同等性能未知
4. **生态稚嫩**：2025 年刚开源，社区规模、文档完善度远不如 Lustre/Ceph
5. **FUSE 瓶颈**：FUSE 客户端可能成为性能瓶颈，Native Client 集成门槛高
6. **缺少第三方评测**：性能数据来自 DeepSeek 自有环境，缺乏独立验证
7. **POSIX 兼容性**：FUSE 模式下的 POSIX 完整度有待社区验证

---

## 部署参考

### 硬件要求

| 硬件 | 最低要求 | 建议配置 |
|------|---------|---------|
| **存储节点 CPU** | 64 核+ | AMD EPYC / Intel Xeon |
| **存储节点内存** | 256 GB+ | 512 GB+ |
| **SSD** | 全 NVMe | 16× 14TB+ NVMe Read Intensive |
| **网络** | 100GbE RoCE | **200Gbps InfiniBand** |
| **客户端节点** | 1 网卡连接集群 | 1+ 200Gbps IB |
| **节点数** | 3+ 存储节点 | 10+ 存储节点 |

### AWS 部署

AWS 上已有基于 **SoftRCoE** 的部署方案（使用 c6a.8xlarge 实例，无需 EFA 或 InfiniBand 即可搭建测试环境）：[AWS 博客](https://aws.amazon.com/cn/blogs/china/deploy-deepseek-3fs-based-on-softrcoe/)

---

## 选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| **已拥有 InfiniBand + NVMe 的大规模 AI 集群** | **3FS** | 充分利用硬件，性能极致 |
| **使用 RoCE 网络的 AI 集群** | 需先验证 | 3FS 在 RoCE 下的性能尚无公开数据 |
| **中小规模训练（<100 GPU）** | BeeGFS / CephFS | 3FS 的硬件门槛不值得 |
| **通用存储需求** | CephFS | 3FS 不是通用系统 |
| **云端训练** | 云厂商 PFS | 托管免运维，性能也够 |

---

## 参考资料

- [3FS GitHub](https://github.com/deepseek-ai/3FS)
- [3FS Design Notes](https://git.softuniq.eu/DeepSeek/3FS/src/commit/79bd34f08d5ebe84e7ddfec050227f89efb9eeae/docs/design_notes.md)
- [DeepSeek 3FS Explained（社区源码分析）](https://github.com/zfhuang99/DeepSeek-3FS-explained)
- [AWS 部署 3FS 方案](https://aws.amazon.com/cn/blogs/china/deploy-deepseek-3fs-based-on-softrcoe/)
- [3FS vs JuiceFS 对比分析](https://cloud.tencent.cn/developer/article/2507444)
- [3FS 如何提升大模型效率](https://cloud.tencent.com.cn/developer/article/2517881)
