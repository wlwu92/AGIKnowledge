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

# CephFS 分布式文件系统调研

## 概述

**CephFS** 是 Ceph 分布式存储系统提供的 **POSIX 兼容文件系统**，构建在底层 **RADOS**（Reliable Autonomic Distributed Object Store）之上。Ceph 是一套统一存储平台，同时提供对象存储（S3/Swift）、块存储（RBD）和文件存储（CephFS）三种接口。

---

## 核心架构

CephFS 最关键的架构决策是 **元数据与数据分离**：

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client 1   │     │   Client 2   │     │   Client 3   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ├────────────────────┼────────────────────┤
       │     MDS Cluster    │                    │
       │  (Active/Standby)  │                    │
       └─────────┬──────────┘                    │
                 │   metadata I/O               │   data I/O
                 ▼                               ▼
       ┌─────────────────────────────────────────────┐
       │              RADOS Cluster                   │
       │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │
       │  │ OSD │ │ OSD │ │ OSD │ │ OSD │ │ OSD │  │
       │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘  │
       └─────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 作用 |
|------|------|
| **MDS（Metadata Server）** | 管理目录结构、文件名、权限、时间戳等 POSIX 元数据；支持多活横向扩展 |
| **OSD（Object Storage Daemon）** | 实际存储文件数据（切分为对象），负责复制、恢复、回填 |
| **MON（Monitor）** | 维护集群状态视图（OSD 存活、CRUSH Map、PG 状态） |
| **MGR（Manager）** | 提供监控指标、负载均衡、集群管理接口 |
| **Client** | 通过 **内核客户端（kclient）** 或 **FUSE** 挂载访问 |

### CRUSH 算法

CephFS 没有中心化的数据寻址表。客户端通过 **CRUSH（Controlled Replication Under Scalable Hashing）** 算法直接计算出数据存放位置：

- **文件 → 对象**：文件按条带大小（默认 4MB）切分为对象
- **对象 → PG**：通过哈希映射到 Placement Group
- **PG → OSD**：通过 CRUSH Map + 确定性哈希选出目标 OSD 列表
- **故障域感知**：支持分层拓扑（host/rack/row/room/zone），天然感知故障域

**PG 数量估算**：`PGs ≈ (OSDs × 100) / 副本数`，取最近的 2 的幂。

---

## 关键特性

### 1. 元数据水平扩展

- 支持 **多 MDS Active/Active**，使用 **动态子树分区（Dynamic Subtree Partitioning）**
- 当某个目录的访问压力增大时，MDS 自动将其元数据迁移到其他节点
- 实测：100K 文件/秒写入时，多 MDS 部署下 CPU 稳定在 30% 以下

### 2. 数据分布与冗余

- 支持 **多副本**（默认 3 副本）和 **纠删码（Erasure Coding）**
- 节点故障时 **自动迁移数据、重新复制**，无需人工干预
- 支持分层存储（NVMe / SSD / HDD 混合池）

### 3. 一致性

- **POSIX 强一致性**，跨主机缓存一致性行为与单机相同
- 客户端间共享文件修改立即可见

### 4. 其他特性

| 特性 | 说明 |
|------|------|
| 快照 | 支持文件系统级 point-in-time 快照 |
| POSIX ACL | 默认启用（内核客户端） |
| 配额 | 按字节数或文件数限制目录 |
| 条带化布局 | 每文件/目录可自定义条带大小和池映射 |
| 多文件系统 | 同一集群运行多个 CephFS 实例 |

---

## 与竞品对比

### 主流分布式/并行文件系统全景对比

| 维度 | **CephFS** | **GlusterFS** | **Lustre** | **3FS** |
|:---|:---|:---|:---|:---|
| **类型** | DFS | DFS | PFS | **PFS（AI 原生）** |
| **定位** | 统一存储（对象+块+文件） | 去中心化 NAS | HPC 通用并行文件系统 | **AI 训练推理全流程专用** |
| **元数据服务** | ✅ 多 MDS 横向扩展 | ✅ 无独立元数据服务器 | ❌ 双 MDS 不可扩展 | ✅ 无状态（FoundationDB） |
| **一致性协议** | RADOS 副本 + PG | DHT + 卷内复制 | 分布式锁 + 租约 | **CRAQ 链式复制** |
| **小文件** | 较好 | 一般 | 弱 | 一般（最小 512KB chunk） |
| **大文件吞吐** | 良好 | 良好 | **极优** | **极优（6.6 TiB/s）** |
| **部署难度** | 较高 | **简单** | 复杂 | **高（全 NVMe+RDMA）** |
| **自动恢复** | ✅ 自动 | ✅ 自动 | ❌ 需手动 | ✅ 自动（chain table 更新） |
| **云原生** | 强（Rook operator） | 一般 | 弱（有托管服务） | 弱（硬件要求苛刻） |
| **RDMA 原生** | ❌ 社区版不支持 | ❌ | ✅ 支持 | **✅ 深度原生集成** |

### vs 并行文件系统（PFS）

CephFS 本质是 **分布式文件系统（DFS）**，与云厂商的 **并行文件系统（PFS）** 在架构和性能上有本质差异：

| 对比维度 | **CephFS（DFS）** | **云厂商 PFS（CPFS/vePFS/CFS Turbo）** |
|---------|-----------------|-----------------------------------|
| **数据访问方式** | 数据分块顺序读写 | **并发并行读写**，多节点同时传输 |
| **单客户端吞吐** | ~1 GB/s | 25-50 GB/s |
| **延迟** | 毫秒级 | **亚毫秒级**（0.2-0.8ms） |
| **集群总吞吐** | 数 GB/s ~ 数十 GB/s | 最高 2 TB/s |
| **多协议** | 对象+块+文件统一 | 主要为文件（配合对象存储） |
| **运维** | 自建自运维 | **全托管** |

---

## 云厂商对标产品

以下云厂商的托管文件存储产品在功能定位上与自建 CephFS 类似（POSIX 共享文件系统），但性能远超 CephFS 社区版：

### 阿里云 — CPFS（Cloud Parallel File System）

| 类型 | 最大吞吐 | 最大 IOPS | 延迟 |
|------|---------|----------|------|
| **CPFS 通用版** | 100 GB/s | 10,000,000 | 0.4-0.6ms |
| **CPFS 智算版** | **2 TB/s** | **30,000,000** | **0.25ms**（RDMA） |

- 支持 POSIX + NFS v3 协议
- 智算版单客户端吞吐 **25 GB/s**（利用 SmartNIC + RDMA 零拷贝）
- 与 OSS 对象存储互通
- 适合 AI 训练、HPC、自动驾驶、EDA 仿真

### 火山引擎 — vePFS（Volcengine Parallel File System）

| 类型 | 最大容量 | 最大读吞吐 |
|------|---------|-----------|
| **性能版** | 960 TiB | 230,000 MB/s |
| **智算版** | 19,760 TiB | **3,000,000 MB/s**（RDMA） |

- 支持 vePFS Client、FSX、NFSv3、SMB 协议
- 亚毫秒级延迟
- 支持 Fileset 细粒度权限管理、目录配额、目录 QoS
- 与 TOS 对象存储互通

### 腾讯云 — CFS Turbo

| 类型 | 最大吞吐 | 最大 IOPS | 延迟 |
|------|---------|----------|------|
| **Turbo 标准型** | 2 TiB/s | 200 万 | 读 0.2ms / 写 3ms |
| **Turbo 性能型** | **2 TiB/s** | **1,000 万** | **读 0.2ms / 写 0.8ms（部分≤60μs）** |

- 全 NVMe（性能型）/ HDD+SSD（标准型）
- 单客户端吞吐 **50 GB/s**
- 千亿级文件管理，1 秒检索 1000 万文件
- 自研 Histor 并行文件存储引擎

### 华为云 — SFS Turbo

| 规格 | 带宽 | IOPS | 延迟 |
|------|------|------|------|
| 标准 | 384 GB/s（缓存 768 GB/s） | 百万 ~ 千万 | **亚毫秒级**（1-3ms 平均） |

- 支持 NFS + SMB 双协议
- 容量最大 6-16 PB
- 全模块架构冗余设计，无单点故障
- 与 OBS 对象存储互通

---

## CephFS 硬件配置建议

### 通用生产配置

#### 配置 A：全 NVMe（性能优先）

| 组件 | 推荐规格 |
|------|---------|
| **机箱** | 2U，24× 2.5" NVMe 槽位 |
| **CPU** | AMD EPYC 9334（32C/64T）或 Intel Xeon Gold 6438M+ |
| **内存** | **256-512 GB** DDR5（建议 8 GB/OSD × 2 余量） |
| **系统盘** | 2× 480GB-1.92TB NVMe 镜像（BOSS 或 M.2） |
| **OSD 盘** | 10-12× **7.68TB NVMe Read Intensive**（1 DWPD） |
| **网络** | 2× **25GbE** bonded |
| **节点数** | 最小 3 节点，推荐 **4+ 节点** |
| 目标性能 | ~250K+ IOPS/节点，亚毫秒延迟 |

#### 配置 B：混合 SSD+HDD（成本均衡）

| 组件 | 推荐规格 |
|------|---------|
| **CPU** | AMD EPYC 9254（24C）或 Intel Xeon Gold 5418Y |
| **内存** | 256 GB DDR5 |
| **系统盘** | 2× 480GB SSD 镜像 |
| **WAL+DB 盘** | 2× **1.92TB NVMe** Read Intensive |
| **数据 OSD** | 12× **16TB+ HDD**（JBOD，不做 RAID） |
| **网络** | 2× 25GbE bonded |

### 高效 AI 训练配置

AI 训练对存储同时要求 **高吞吐**（大文件数据集读取）和 **低延迟元数据**（小文件、checkpoint 写入），需要专门调优：

| 维度 | 推荐配置 | 说明 |
|------|---------|------|
| **OSD 布局** | **2 OSDs/NVMe 盘** | 将 99 百分位尾延迟降低 50%，对多客户端并发访问至关重要 |
| **OSD 内存** | `osd_memory_target = 8G`（建议 16G+） | NVMe OSD 需要更大内存缓存 |
| **元数据池** | 专用 **企业级 NVMe**（1+ DWPD） | 元数据性能决定训练启动速度和 checkpoint 效率 |
| **数据池** | NVMe 或高性能 SSD | 训练数据集读取和 checkpoint 写入 |
| **MDS 数量** | **2-4 个 active ranks** + 目录 pinning | 将热点目录绑定到指定 MDS |
| **MDS 缓存** | `mds_cache_memory_limit = 16-32G` | 默认 4G，AI 场景需要大幅提升 |
| **MDS CPU** | **高主频**（3.5+ GHz） | MDS 单线程密集，主频比核数重要 |
| **网络** | **100GbE**（推荐）或至少 25GbE | 单 NVMe OSD 可饱和 10GbE |

#### 系统级调优

```bash
# BIOS 禁用 CPU C-States（减少微秒级唤醒延迟）
intel_idle.max_cstate=0 processor.max_cstate=0

# 禁用 IOMMU（减少 I/O 翻译开销）
intel_iommu=off    # Intel
amd_iommu=off      # AMD

# 启用 Jumbo Frames
ip link set dev <interface> mtu 9000

# NVMe IO 调度器设为 none
echo none > /sys/block/nvme0n1/queue/scheduler

# 客户端挂载选项
mount -t ceph <mon>:6789:/ /mnt/cephfs \
  -o rsize=4194304,wsize=4194304, \
     readdir_max_bytes=4194304,nocrc
```

#### 关键 Ceph 配置参数

```ini
[osd]
osd_memory_target = 8G
osd_memory_target_autotune = true
bluestore_cache_size = 4G
bluestore_throttle_bytes = 0          # NVMe 下关闭限流
bluestore_throttle_deferred_bytes = 0

[mds]
mds_cache_memory_limit = 16G
mds_cache_reservation = 0.10
```

#### 参考性能（10 节点全 NVMe Ceph Reef 实测）

| 指标 | 性能 |
|------|------|
| 4K 随机读 IOPS | ~440 万 |
| 4K 随机写 IOPS | ~80 万 |
| 大文件读吞吐 | ~71 GB/s |
| 大文件写吞吐 | ~25 GB/s |
| 平均写延迟（4K sync） | < 0.5ms |

---

## 典型使用场景

1. **云原生 / K8s** — 通过 Rook operator 或 CephFS CSI 驱动提供 PersistentVolume
2. **AI/ML 训练** — 多 GPU 节点共享数据集和 checkpoint
3. **OpenStack** — 作为 Manila 后端提供共享文件系统
4. **统一存储** — 一套集群同时提供对象、块、文件三种接口
5. **企业共享目录** — 替代传统 NAS（NFS），无单点故障
6. **私有云 / 边缘** — 多云/混合云架构避免厂商锁定

---

## 开源并行文件系统方案

除了自建 CephFS（DFS），还有以下成熟的**开源并行文件系统（PFS）**可供选择：

| 系统           | 许可证              | 架构特点                                     | 适用规模                     | 运维难度    | 硬件前提                 | 2025-2026 动态                             |
| ------------ | ---------------- | ---------------------------------------- | ------------------------ | ------- | -------------------- | ---------------------------------------- |
| **Lustre**   | GPLv2            | 独立 MDS/OSS 组件，需 patched kernel           | **Exabyte 级**，10000+ 客户端 | ★★★ 高   | HDD/SSD 混合           | 2.17.0 发布；Google Cloud 托管 Lustre（1 TB/s） |
| **BeeGFS**   | 开源核心 + 商业扩展      | **用户态服务端**，分布式元数据，无需 patch 内核            | **PB 级**，1000+ 客户端       | ★★ 中低   | HDD/SSD 混合           | v8.2 发布，IPv6 + 后台 Rebalance              |
| **OrangeFS** | **LGPL（完全开源）**   | 统一服务器设计（元数据+数据合一），内核已原生支持                | 中小规模                     | ★★ 中    | HDD/SSD 混合           | 2.10.1 发布，适配最新内核                         |
| **DAOS**     | Apache 2.0       | **全用户态 OS-bypass**，K-V 对象存储，NVMe 原生      | 超算级                      | ★★★★ 极高 | **全 NVMe + RDMA**    | Aurora IO500 第一，v3.0 预计 2026             |
| **3FS**      | Apache 2.0 / MIT | **分解式架构**，FoundationDB 元数据，CRAQ 复制，AI 原生 | 超大规模 AI                  | ★★★ 高   | **全 NVMe + RDMA IB** | 2025.2 开源，6.6 TiB/s 实测                   |

### Lustre — HPC 领域的事实标准

- 全球 **Top500 超算** 中最广泛部署的并行文件系统
- 独立 MDS（元数据服务器）+ OSS（对象存储服务器）架构
- 极端规模：支持 Exabyte 级容量、100,000+ 客户端
- 弱点：MDS 单点瓶颈（不可横向扩展）、内核模块需 patched 后编译、小文件性能差
- 现已可通过 Google Cloud Managed Lustre（2025 GA）和 AWS FSx for Lustre 在云端使用

### BeeGFS — 性能与易用性的最佳平衡

- **用户态服务端**：部署和升级远比 Lustre 简单（无需重新编译内核）
- **分布式元数据**：支持多个元数据服务器线性扩展，解决了 Lustre 的 MDS 瓶颈
- 实测案例：某中国 AI 公司从 Lustre 迁移到 BeeGFS + Ceph OSS，解决了数十亿小文件场景的元数据瓶颈
- 企业特性（HA、Quota、ACL）需商业许可

### DeepSeek 3FS（Fire-Flyer File System）— AI 原生并行文件系统

2025年2月28日，DeepSeek 在开源周最后一天开源了 **3FS**，这是支撑 DeepSeek V3/R1 训练推理的核心存储基础设施。

#### 架构概览

3FS 采用**计算与存储分离的分解式架构**，四大组件：

```
┌──────────────┐
│  Mgmtd       │  集群管理：节点注册、心跳检测、配置分发、chain table维护
│  (集群管理)   │
└──────┬───────┘
       │
┌──────▼───────┐       ┌─────────────────────┐
│  Meta        │ ───→  │ FoundationDB        │
│  (元数据服务) │       │ (事务性 KV 存储)     │
└──────┬───────┘       └─────────────────────┘
       │
┌──────▼───────┐
│  Storage     │  本地 SSD 管理，CRAQ 链式复制
│  (存储服务)   │
└──────┬───────┘
       │
┌──────▼───────┐
│  Client     │  FUSE Client（POSIX）或 Native Client（高性能 API）
└──────────────┘
         全部通信基于 RDMA（InfiniBand 或 RoCE）
```

#### CRAQ 链式复制协议

3FS 采用 **CRAQ（Chain Replication with Apportioned Queries）** 作为核心数据一致性协议：

```
写入路径（串行传播）：
Client → Head → Target 1 → Target 2 → Tail（提交）→ ACK 反向传播 → Head → Client

读取路径（任意节点均可）：
Client → 任意 Target（若版本为"干净"直接返回；若为"脏"则查 Tail 获取最新版本）
```

- **写入**：从链头串行传播到链尾，到达尾部才提交，以写入延迟换取强一致性
- **读取**：任意副本可响应，读带宽随副本数线性扩展
- **故障处理**：节点故障时 Mgmtd 检测并更新 chain table，写入自动切换到后继节点

#### 文件分布与条带化

- 文件分割为固定大小 Chunk（默认 512KB）
- 条带化 + 轮询方式分布到多个复制链
- 使用 **balanced incomplete block design** 优化节点故障后的恢复流量，避免热点饱和

#### 元数据存储

- 基于 **FoundationDB** 的事务性 KV 存储，支持 Serializable Snapshot Isolation（SSI）
- 元数据服务**无状态**，简化扩缩容
- 文件长度默认每 5 秒由客户端报告更新（close/fsync 时精确查询）

#### 性能数据

| 指标 | 集群配置 | 性能 |
|------|---------|------|
| 聚合读取吞吐 | 180 存储节点 + ~500 客户端节点，2×200Gbps IB | **~6.6 TiB/s**（含训练背景流量） |
| GraySort 排序 | 25 存储 + 50 计算，2×400Gbps + 1×200Gbps | **3.66 TiB/min**（110.5 TiB / 30分14秒） |
| KVCache 查找峰值 | 单客户端，200Gbps IB | **40+ GiB/s** |

#### 存储节点配置

每节点 **16× 14TB NVMe SSD**，224 TiB/节点原始容量，2×200Gbps InfiniBand。

#### 对 AI 工作负载的专项优化

| 场景 | 优化方式 |
|------|---------|
| **训练数据加载** | 跨节点随机访问，无需预取或 shuffle，充分利用 RDMA 随机读性能 |
| **Checkpoint 保存/加载** | CRAQ 保证强一致，条带化并行读写打通多节点带宽 |
| **KVCache 推理** | 将 KVCache 部分卸载到 SSD，作为 DRAM 的低成本替代，单节点 40+ GiB/s |
| **数据预处理** | 配合 Smallpond（DuckDB 之上）实现 PB 级数据处理 |

#### 与同类系统的核心差异

| 维度 | 3FS | Lustre | CephFS |
|------|-----|--------|--------|
| **设计目标** | **AI 全流程专用**（训练+推理） | 通用 HPC | 通用统一存储 |
| **一致性协议** | CRAQ 链式复制 | 分布式锁 + 租约 | RADOS + PG |
| **元数据存储** | FoundationDB（事务 KV） | 内核态专用元数据服务 | RADOS 对象存储 |
| **客户端** | FUSE + Native（RDMA 零拷贝） | 内核模块（需 patched） | 内核模块 / FUSE |
| **最小 chunk** | 512KB | 1MB+（可配置） | 4MB（默认对象大小） |
| **RDMA 原生** | ✅ **深度原生集成** | ✅ 支持 | ❌ 社区版无原生 RDMA |
| **KVCache 支持** | ✅ 专用设计 | ❌ | ❌ |
| **硬件事先假设** | **全 NVMe + RDMA** | HDD/SSD 混合 | HDD/SSD 混合 |
| **开源时间** | 2025.2 | 2003 | 2012 |

#### 分析评价

**优势：**
1. **AI 原生设计**：不是通用系统改 AI，而是从第一天起为 AI 训练推理定制，KVCache 支持是独有亮点
2. **极致性能**：6.6 TiB/s 聚合吞吐（180 节点）远超 Lustre 同类规模典型值
3. **CRAQ 协议**：写串行化、读并行的设计完美匹配 AI 场景（读远多于写）
4. **无状态元数据**：基于 FoundationDB，扩缩容远易于 Lustre 的有状态 MDS
5. **真正开源**：Apache 2.0 / MIT 许可证

**局限：**
1. **硬件门槛极高**：全 NVMe + RDMA InfiniBand，小团队难以复现
2. **AI 专用性太强**：不适合通用存储场景
3. **生态稚嫩**：2025 年才开源，社区和文档远不如 Lustre/Ceph
4. **单机 FUSE 性能瓶颈**：目前 FUSE 客户端可能成为瓶颈，Native Client 集成门槛高
5. **未与 Ceph/Lustre 同条件对比**：性能数据来自 DeepSeek 自有环境，缺乏第三方独立评测

**一句话定位**：3FS 是**AI 存储的"专用芯片"**——针对 AI 场景做到极致，但通用性差；Lustre/Ceph 是**"通用 CPU"**——场景广泛但单项不如专用方案。

### OrangeFS — 完全开源的轻量选择

- 前身是 PVFS（Parallel Virtual File System）
- 唯一**内核原生支持**的并行文件系统（自 Linux 4.6）
- 同一节点同时处理元数据和数据（简化部署）
- 支持 POSIX、MPI-IO、FUSE、Windows、S3、Hadoop JNI 多种接口
- 社区规模较小，极端规模验证不足

### DAOS — 下一代性能标杆

- Intel 发起、面向**百亿亿次（Exascale）**的存储系统
- **全用户态 + OS-bypass**：完全绕过 Linux 内核，无上下文切换开销
- 原生 NVMe，不支持 HDD，要求 RDMA 网络
- IO500 实测：**单节点性能是 Lustre 的 ~3 倍**
- Aurora 超算（Argonne）：1,024 节点，230 PB，~25 TB/s 带宽
- 现状：生态尚小，无原生 POSIX 支持（需 Lustre 兼容层），NVIDIA GPUDirect 不支持

### 选型参考

| 需求 | 推荐 |
|------|------|
| 极大规模超算 / 最大生态 | **Lustre** |
| 性能 + 易用的折中 | **BeeGFS** |
| 完全开源无商业依赖 | **OrangeFS** |
| **AI 训练极致性能 / 新建 AI 集群** | **3FS**（AI 全流程专用） |
| 极致性能 / 前沿探索 | **DAOS**（生态尚小） |

---

## PFS vs DFS：核心技术差异分析

### 为什么 PFS 和 DFS 性能差距如此之大？

核心原因在于**数据路径和元数据架构的本质差异**。以下从几个关键维度拆解。

### 1. 数据路径（Data Path）—— 最关键的差异

```
DFS（CephFS）数据流：
┌─────────┐    ① 查元数据    ┌──────────┐
│ Client  │ ──────────────→  │  MDS     │
│         │                  │ (元数据)  │
│         │ ←── ② 返回位置 ─ │          │
│         │                  └──────────┘
│         │    ③ 读 OSD      ┌──────────┐
│         │ ──────────────→  │  OSD 1   │ ← 一次只能读一个 OSD
│         │                  └──────────┘
│         │       或
│         │    ③ 读另一个    ┌──────────┐
│         │ ──────────────→  │  OSD 2   │
└─────────┘                  └──────────┘
  数据要经过 3 步，且一次只与一个 OSD 通信

PFS（Lustre/BeeGFS）数据流：
┌─────────┐    ① 获取 layout  ┌──────────┐
│ Client  │ ────────────────→  │  MDS     │
│         │                    │ (元数据)  │
│         │ ←── ② 返回布局 ── │          │
│         │                    └──────────┘
│         │    ③ 直接并行读    ┌──────────┐
│         │ ──┼─────────────→  │  OSS 1   │ ← 同时与多个
│         │ ──┼─────────────→  │  OSS 2   │    OSS 通信
│         │ ──┼─────────────→  │  OSS 3   │
│         │ ──┼─────────────→  │  OSS 4   │ ← 带宽 N 倍
└─────────┘                  └──────────┘
  元数据服务器返回布局后即退出数据路径，客户端直接并行访问所有存储节点
```

| 维度 | DFS | PFS |
|------|-----|-----|
| **数据流经** | 客户端逐个与存储节点通信（串联） | 客户端同时与所有存储节点通信（并联） |
| **网络跳数** | 2+ 跳（client → server → storage） | 1 跳（client → storage 直连） |
| **瓶颈** | 控制器/OSD 成为固定瓶颈 | 无中介节点，带宽随节点数线性扩展 |
| **并发度** | 单 OSD 串行 | **全 OSD 并行** |

**一句话总结**：
- **DFS** = 客户端找中间人去挨个取数据
- **PFS** = 元数据服务器告诉客户端"数据在哪"，客户端直接找所有存储节点**同时取**

### 2. 元数据架构（Metadata Architecture）

| 维度 | DFS | PFS |
|------|-----|-----|
| **元数据位置** | 元数据服务器**在数据路径内**或数据路径经过控制器 | **元数据与数据路径分离**（out-of-band） |
| **查询方式** | 每次 I/O 都可能查询元数据 | 客户端获取一次 layout 后**缓存到本地**，后续直接访问 |
| **扩展性** | 元数据可能成为瓶颈（即使多 MDS，仍经过 RADOS） | 元数据可分布式部署（BeeGFS）或分离到专用设备 |
| **典型延迟** | 毫秒级（CephFS 小文件创建 ~8ms） | 亚毫秒级（PFS layout 获取后无需二次查询） |

**PFS 最关键的设计决策**：**将元服务器从数据路径中移除**。MDS 只告诉客户端 "文件块分布在哪些 OSS 上、条带大小是多少"，此后客户端完全绕过 MDS，直接同时从所有 OSS 读取数据。

### 3. 条带化与并发访问

两者都会把文件分片，但**读取方式不同**：

```
文件 "training_data.bin"（1GB）

DFS（CephFS）：
┌────────┬────────┬────────┬────────┐
│对象 0  │对象 1  │对象 2  │对象 3  │   ← 分布在 4 个 OSD
└───┬────┴───┬────┴───┬────┴───┬────┘
    │        │        │        │
    └── 依次读取 ──────┘        │
         Client ◄────── 一次读一个对象
    吞吐 = 1 × OSD 带宽

PFS（Lustre/BeeGFS）：
┌────────┬────────┬────────┬────────┐
│条带 0  │条带 1  │条带 2  │条带 3  │   ← 分布在 4 个 OSS
└───┬────┴───┬────┴───┬────┴───┬────┘
    │        │        │        │
    ├────────┼────────┼────────┤
    └────── 同时读取 ──────────┘
              Client
    吞吐 = 4 × OSS 带宽
```

DFS 将一个文件的对象分布在多个 OSD 上，但**客户端一次只请求一个对象**。PFS 将一个文件条带化到多个 OSS 上，**客户端发出一个请求、多个 OSS 同时响应**。

### 4. 关键差异总结

| 维度 | DFS（CephFS） | PFS（Lustre/BeeGFS） |
|------|-------------|---------------------|
| **数据路径** | 控制器中介，串行 | 客户端直连存储，**并行** |
| **元数据位置** | 在数据路径内或经过中介 | **元数据与数据路径分离** |
| **Layout 获取** | 可能每次都需要查询 MDS | 获取后客户端缓存，后续零查询 |
| **带宽扩展** | 受限于单个 OSD/控制器吞吐 | **线性扩展**，节点翻倍带宽翻倍 |
| **网络需求** | 标准以太网 | 高速互联（InfiniBand/RDMA/100GbE） |
| **单客户端吞吐** | ~1 GB/s | **25-50 GB/s**（云 PFS）/ 数 GB/s（自建） |
| **延迟** | 毫秒级 | 亚毫秒级 |
| **小文件** | 较好（元数据在 RADOS 中分布） | 较差（条带化开销） |
| **一致性** | 强一致（自动处理） | 强一致（需客户端租约/锁） |

### 5. 为什么云厂商 PFS 能到 TB/s？

云厂商 PFS（CPFS/vePFS/CFS Turbo）在开源 PFS 基础之上又加了**三重加速**：

1. **全 NVMe 硬件**：开源 PFS 还需兼顾 HDD 混合部署，云 PFS 性能型全是 NVMe
2. **自研用户态协议栈 + RDMA**：完全绕过内核 TCP/IP 栈，**零拷贝**传输（SmartNIC offload）
3. **内核态并行客户端**：在客户端内核中植入驱动程序，数据直通 GPU/NIC，无需用户态缓冲区拷贝

> 开源 PFS（Lustre/BeeGFS）的极限大约在单客户端 **4-8 GB/s**，云厂商 PFS 通过硬件加速和自研协议栈把这个数字推到了 **25-50 GB/s**，差距主要在**专用硬件（RDMA/SmartNIC）和私有协议的优化深度**上。

---

## CephFS 核心技术深度解析

### 1. CRUSH 算法深度解析

CRUSH（Controlled Replication Under Scalable Hashing）是 Ceph 无中心寻址的基石，客户端**无需查询任何中心化节点**即可计算出数据位置。

#### 完整映射链路

```
对象 (Object)                    文件被切分为对象（默认 4MB）
    │
    ▼  hash(object_name) % num_pg
PG (Placement Group)             中间逻辑层，屏蔽 OSD 变化
    │
    ▼  CRUSH(pg_id, cluster_map, rule)
OSD Acting Set                   有序列表 [primary, replica1, replica2]
```

#### Straw2 选型算法

CRUSH 使用 **Straw2** 算法从 Bucket 中选出目标 OSD。核心逻辑：

```
for each item in bucket:
    x = hash(pg_id, r)            # r 为副本序号（0=primary, 1=replica...）
    x = ln(x/65536) / weight      # weight 为 OSD 权重
    if x > max_x:
        max_x = x
        max_item = item
```

- **ln 函数**使得 Straw2 的分布趋近于 **权重比例**，而非简单余数哈希
- **hash 输入包含 r 值**，同一 PG 的不同副本选到不同 OSD（故障域隔离）

#### 层次化 CRUSH Map

```
root default
├── rack rack-a
│   ├── host host-a1
│   │   ├── osd.0 (weight 1.0)
│   │   └── osd.1 (weight 1.0)
│   └── host host-a2
│       ├── osd.2 (weight 1.0)
│       └── osd.3 (weight 1.0)
└── rack rack-b
    ├── host host-b1
    │   ├── osd.4 (weight 1.0)
    │   └── osd.5 (weight 1.0)
    └── host host-b2
        ├── osd.6 (weight 1.0)
        └── osd.7 (weight 1.0)
```

**规则示例**："3 副本，distinct rack"
```
rule replicated_3rack {
    id 0
    type replicated
    min_size 1
    max_size 10
    step take root               # 从 root 开始
    step chooseleaf firstn 3 type rack  # 选 3 个不同 rack，每个 rack 内自动选 host→osd
    step emit
}
```

#### CRUSH 的关键特性

| 特性 | 含义 |
|------|------|
| **确定性** | 相同输入（pg_id + cluster_map）永远返回相同 OSD 列表 |
| **稳定性** | 增减 OSD 时，只有少量 PG 需要迁移（概率性重分布） |
| **权重感知** | OSD 按 weight 比例承担 PG，支持弹性扩缩 |
| **故障域感知** | 通过层次化 Map 和 placement rule 实现故障隔离 |
| **无中心化** | 客户端本地计算，无需访问元数据服务器 |

#### PG 与 OSD 的 N:M 关系

- 一个 PG 对应一组 OSD（acting set），一个 OSD 服务大量 PG
- PG 数量估算：`PGs ≈ (OSDs × 100) / 副本数`，取 2 的幂
  - 10 OSD × 3 副本 → 约 333 → **512 PG**
  - 100 OSD × 3 副本 → 约 3333 → **4096 PG**
- PG 过少：分布不均匀，单 OSD 故障影响范围大
- PG 过多：内存开销大（每个 PG 约 1-2 KB 元数据）

---

### 2. RADOS 数据读写路径

#### 写入路径（Primary Log-Based Replication）

```
Client ──→ Primary OSD（CRUSH 计算得到）
                │
                ├── 1. 创建 OpContext & PGTransaction
                ├── 2. 写入本地 BlueStore（本地持久化）
                ├── 3. 并发发送给所有 Replica OSD
                │
Replica OSD 1 ◄─┘   Replica OSD 2 ◄─┘
    │                    │
    └── 本地 BlueStore ──┘
                │
                ▼ 所有副本确认
Client ◄── Primary 返回 ACK
```

**关键规则**：
> 任何 PG 的写入操作在**所有 acting set 成员持久化完成前**不会向客户端确认。

写入的 6 个步骤：
1. Client 通过 CRUSH 找到 Primary OSD，发送写请求
2. Primary 创建 `OpContext` 结构，做校验检查
3. Primary 生成 `PGTransaction`（转换为存储后端可理解的操作）
4. Primary 调用 `queue_transactions` 写入本地 BlueStore
5. Primary **并发**将写请求发送给所有 Replica OSD
6. 等待所有 Replica 写入完毕并确认后，向 Client 返回 ACK

#### 读取路径

```
Client ──→ Primary OSD（CRUSH 计算得到）
                │
                └── 本地 BlueStore 同步读取（副本池）
                        │
                        ▼ 直接返回
Client ◄── Primary 返回数据
```

- **副本池（Replicated Pool）**：Primary 本地可满足所有读请求，无需访问 Replica
- **纠删码池（EC Pool）**：Primary 可能需要从多个 Replica 拉取 shard 来重构对象（需要 k+m 中的至少 k 个 shard）

---

### 3. PG Peering 全过程

Peering 是 Ceph 最复杂但最关键的机制——让 PG 的所有 OSD 对对象状态达成一致。

#### 关键概念

| 术语 | 定义 |
|------|------|
| **Acting Set** | 当前 epoch 负责 PG 的 OSD 有序列表 |
| **Up Set** | CRUSH 算出的 OSD 列表（通常与 Acting Set 一致） |
| **Primary** | Acting Set 的第一个成员，协调 peering 和写入 |
| **Stray** | 已不在 acting set 但尚未被告知删除的 OSD |
| **PG Log** | 该 PG 最近更新操作的日志 |
| **Missing Set** | 需要更新的对象列表（日志中有记录但数据还不全） |
| **Authoritative History** | 完整的、有序的操作集合，足以让任何副本恢复到最新状态 |

#### Peering 12 步

1. **获取 OSD Map** — Primary 获取最新的 OSD Map，确认自己的 Primary 身份
2. **生成 Past Intervals** — 自 `last_epoch_started` 以来所有区间变化列表
3. **联络 Peer OSD** — 联系每个 past interval 中的至少一个 OSD，获取它们的 PG Info
4. **同步 PG Log** — 如果发现 peer 有 Primary 不存在的操作，拉取并合并日志
5. **查询当前 Acting Set** — 获取所有成员的 PG Log 和 Missing Set
6. **建立 Authoritative History** — 整合所有信息，得到一个一致的、完整的历史
7. **更新 up_thru** — 如果 Primary 的 up_thru 不足，向 Monitor 请求更新
8. **分发 Log 更新** — 向 acting set 各成员发送日志更新（可能删除冲突对象）
9. **等待确认** — 等待所有成员持久化 PG Log 条目
10. **开始接受写入** — 所有 OSD 对元数据状态达成一致
11. **更新 last_epoch_started** — 更新本地 PG Info，通知其他成员更新
12. **恢复阶段** — 从 past interval 的 OSD pull 数据，Primary push 到 Replica。全部就绪后更新 `last_epoch_clean`，释放 Stray

#### Peering 的意义

Peering 完成后：
- Primary 可以**立即开始接受写入**
- 数据恢复在**后台渐进进行**（先响应用户请求，再补齐数据）
- 客户端无感知 OSD 故障切换

#### 区间变化与 PG Temp

当 CRUSH 算出的新 Acting Set 中有空 OSD（无数据）：

```
OSD 故障:
    原：osd.{1, 2, 3}  →  新 CRUSH：osd.{3, 1, 2}（3 是空盘）

PG Temp 机制:
    Monitor 设置临时 Acting Set：osd.{1, 2, 3}
    1 继续服务读写，3 后台 backfill
    backfill 完成后 → 丢弃 PG Temp → 3 成为真正 Primary
```

这保证了 OSD 增删期间**服务不中断**。

---

### 4. MDS 动态子树分区内部机制

CephFS 通过动态子树分区实现多 MDS 横向扩展，整体流程分为四步循环：

#### 四步均衡循环

```
① 负载收集 ──→ ② 导出/导入节点划分 ──→ ③ 子树选择 ──→ ④ 子树迁移
    ↑                                                        │
    └────────────────────── 循环 ────────────────────────────┘
```

##### ① 负载收集

每个 MDS 收集以下指标：
- 请求速率（ops/s）
- 缓存命中率
- 管理 inode 数量
- CPU 负载

通过 **all-to-all 集体通信** 广播给集群中所有 MDS，判断是否需要触发 rebalance。

##### ② 导出/导入节点划分

集群将所有 MDS 分为 **exporter（过载）** 和 **importer（低载）**，计算需要迁移的负载量。

##### ③ 子树选择 — Popularity Counter

CephFS 使用 **流行度计数器（Popularity Counter）**，反映元数据访问的**时间局部性**：

- 每次元数据操作递增目标 inode 及其**所有祖先直到 root** 的计数器
- 计数器值**指数衰减**（无访问时逐渐降低）
- 每个 rebalance epoch 汇总 MDS 管理的所有子树计数器作为当前负载
- 选择计数器最高的子树作为迁移候选

##### ④ 子树迁移 — 两阶段提交

迁移使用**标准两阶段提交协议**确保一致性：
```
Exporter MDS                     Importer MDS
    │                                │
    ├── 准备迁移子树 ──────────────→  准备接收
    │                                │
    │◄── 准备好 ────────────────────  确认
    │                                │
    ├── 冻结子树（停止服务） ──────→  
    ├── 序列化元数据 ──────────────→  反序列化
    ├── 释放子树全局锁 ────────────→  获取锁
    │                                │
    │◄── 完成 ──────────────────────  确认
    │
    子树从 Exporter 移除
```

#### `bal_rank_mask` — 选择性均衡

```
ceph fs set <fs_name> bal_rank_mask 0x3   # 只在 rank 0 和 1 上运行 balancer
ceph fs set <fs_name> bal_rank_mask -1     # 全部（默认）
ceph fs set <fs_name> bal_rank_mask 0x0    # 关闭 balancer
```

某些子卷使用**静态 pinning**（性能敏感），其他子卷使用**动态 balancing**。

#### Directory Pinning

将特定目录 pin 到指定 MDS rank：

```
# 将 /training/dataset 固定到 MDS rank 2
ceph fs subvolume pin <fs_name> /training/dataset mds 2
```

适用于 AI 训练场景：将活跃数据集目录 pin 到独立 MDS，避免被其他目录的访问干扰。

#### 已知限制

默认 balancer **默认关闭**，原因：

- 效率低、速度慢
- 不精确的失衡预测（对无害失衡过度反应）
- 忽视工作负载特征（不考虑访问模式）
- 不必要的迁移活动反而降低性能

> "The balancer is sometimes inefficient or slow, so by default it is turned off." — Ceph 官方文档

#### 学术前沿：Lunule / Lunule+（ACM TOS 2025）

2025 年发表的新方案（中国科大 + 休斯顿大学）：

| 方法 | 改进 | 效果 |
|------|------|------|
| **Lunule** | 基于变异系数（CV）的失衡因子模型 | 精确判断何时触发 rebalance |
| **Lunule+** | 引入**紧急度参数**区分安全/有害失衡 | 避免无效迁移 |
| | 将元数据访问建模为**矩阵** | 大幅提升负载预测准确度 |

结果：元数据吞吐提升 **最高 315.8%**，尾任务完成时间缩短 **最高 64.6%**。

---

### 5. CephFS 完整 I/O 路径串联

以客户端读取文件 `training_data.bin` 为例：

```
Step 1: Client 向 MDS 发送 lookup/open 请求
    MDS 查询元数据（从 RADOS 元数据池读取 inode + 文件布局信息）
    MDS 返回：文件对象分布列表 + CAP 权限

Step 2: Client 解析布局
    文件位于 pool "cephfs_data"
    对象条带大小 4MB
    文件由 N 个对象组成：ino.0, ino.1, ino.2, ...

Step 3: Client 计算每个对象的位置
    for each object:
        pg_id = hash(object_name) % num_pg
        [primary, replica...] = CRUSH(pg_id)
    结果：每个对象有一个 Primary OSD

Step 4: Client 向 Primary OSD 发送读请求
    OSD Primary 从 BlueStore 读取数据
    校验数据完整性
    返回数据给 Client

Step 5: Client 读完一个对象 → 继续读取下一个对象
    （注意：这里是关键——一次只读一个对象）
```

**性能瓶颈点**：
- MDS 查询元数据的延迟和吞吐受 MDS 缓存和元数据池性能限制
- Step 4-5 是串行的——即使文件分布在 100 个 OSD 上，Client **一次仍然只读一个对象**
- 这是 DFS 与 PFS 的根本性能差距：**数据路径不可并行化**

---

## 近期版本动态

- **Reef（R）**（2024）：MDS 稳定性大幅提升，多 MDS 动态子树分区改进
- **Squid（S）**（2025）：CephFS 性能优化，更好的快照支持
- **Umbrella（U）**（2026，进行中）：聚焦灾难恢复改进、MDS 性能指标与调优、用户数据保护与备份增强、自动化运维

---

## 选型建议

| 场景 | 推荐方案 |
|------|---------|
| 需要极致性能 + 免运维 | 云厂商 PFS（CPFS / vePFS / CFS Turbo） |
| 统一存储（对象+块+文件） | **CephFS** |
| 多云/混合云，避免锁定 | **CephFS** |
| 中小规模，成本敏感 | **CephFS**（自建） |
| 云原生 / K8s 存储后端 | CephFS + Rook |
| HPC / 超算大文件 | Lustre |
| 简单 NAS 替代 | GlusterFS |

---

## 参考资料

- [Ceph 官方文档 - CephFS](https://docs.ceph.com/en/latest/cephfs/)
- [Ceph Hardware Recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/)
- [FOSDEM 2026 - Smoother CephFS Experience With Umbrella Release](https://fosdem.org/2026/schedule/event/MUXBDR-smoother-cephfs-experience-with-umbrella-release/)
- [Design and Implementation of Ceph: A Scalable Distributed File System](https://digital.library.unt.edu/oai/?verb=GetRecord&metadataPrefix=oai_dc&identifier=info:ark/67531/metadc888555)
- [阿里云 CPFS 产品简介](https://www.alibabacloud.com/help/zh/cpfs/cpfs-product-introduction)
- [火山引擎 vePFS 文档](https://www.volcengine.com/docs/6459/145549)
- [腾讯云 CFS Turbo](https://cloud.tencent.com.cn/developer/article/2660347)
- [华为云 SFS Turbo](https://support.huaweicloud.com/intl/zh-cn/productdesc-sfsturbo/sfsturbo_01_0360.html)
