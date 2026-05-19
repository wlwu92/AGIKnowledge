---
created: 2026-05-19
aliases:
  - IaC 工具分工边界
  - 分层决策
tags:
  - layer/l3
  - type/survey
  - domain/ai-infra
---

# 分层决策：Packer、Ansible、Terraform、Docker 的分工与边界

> 四个工具功能有大量重叠，但定位不同层。理解"什么放哪层更好"比"哪个工具能做什么"更重要。

## 核心框架：三维决策空间

每个运维操作都可以从三个维度定位，决定了把它放在哪个工具中：

```
  变更频率（最关键的维度）
       │
 慢 ←──┼──→ 快
       │
       └────── 抽象层级
              物理机 …… VM …… 容器 …… 应用
```

加上部署阶段：

```
构建镜像 ──→ 创建资源 ──→ 配置运行时 ──→ 部署应用
Packer      Terraform    Ansible         Docker/CI
```

### 按变更频率定位

| 层 | 变更频率 | 典型内容 | 首选工具 |
|----|---------|---------|---------|
| 慢变层 | 季度/月度 | OS 内核、NVIDIA 驱动、CUDA Toolkit、监控 agent | **Packer**（固化到 AMI） |
| 中间层 | 周级/月级 | Docker daemon 配置、NCCL 参数、用户权限、日志轮转 | **Ansible**（模板+handler） |
| 快变层 | 每次部署 | 容器镜像 tag、环境变量、feature flag、密钥轮换 | **Docker / Ansible / CI/CD** |

### 关键原则

**让操作尽量靠左移动**（固化到更低层）是追求效率，**让操作尽量靠右移动**（延迟到更高层）是追求灵活性。同一个操作放不同层，解决不同的问题：

```
固化到 Packer（慢但一致）→ 所有实例相同，启动即就绪
放在 Ansible（灵活但慢） → 每台机器独立，可动态调整
放在 Docker/CI（最快）   → 每次部署可变，最灵活
```

---

## 六个重叠区域详解

下面逐一拆解最常见的"左右为难"场景，每个都给出两种做法的对比和推荐。

### 重叠一：NVIDIA 驱动 + CUDA Toolkit

| 做法 | 放 Packer AMI | 放 Ansible playbook |
|------|-------------|-------------------|
| 操作 | 在 Packer HCL 中用 `provisioner "shell"` 安装驱动 | 实例启动后 Ansible 通过 `apt` 安装 |
| 耗时 | 构建阶段 5-10 分钟（一次性） | 每台实例启动后等 3-5 分钟 |
| 重启 | 构建时重启，AMI 已包含驱动 | 运行时重启，必须设计回滚策略 |
| 版本变更 | 改 AMI 名字 → 新 tag → 新实例 | 改 playbook 变量 → 重新 apply |
| 规模启动 | 100 台实例同时启动，2 分钟就绪 | 100 台同时跑 apt install，NVIDIA repo 可能限流 |

```yaml
# ❌ 放在 Ansible（不推荐但可行）
- name: 安装 NVIDIA 驱动
  apt:
    name: nvidia-driver-550
    state: present
  notify: reboot host     # ← 需要重启，设计复杂

# ✅ 放在 Packer（推荐）
# packer provisioner "shell" 中执行：
# apt-get install -y nvidia-driver-550 && reboot
# AMI 创建完成后，驱动已生效
```

**推荐**：放 Packer。驱动安装慢 + 需要重启 + 极少变更，完美匹配"慢变层"。

**例外**：裸机服务器（没有 Packer 概念）→ 只能放 Ansible。

### 重叠二：Docker daemon 配置

| 做法 | 放 Packer AMI | 放 Ansible |
|------|-------------|-----------|
| 配置文件 | `COPY daemon.json /etc/docker/` 固化到 AMI | `template` 模块写入，支持变量 |
| 变更代价 | 重建 AMI → 新实例才生效 | 直接改配置 → handler 重启 Docker |
| 灵活性 | 所有实例用同一份配置 | 可按 `group_vars` 区分 GPU/CPU 节点 |
| 运行时信息 | 构建时不知 EFS 地址、registry 认证 | 实例运行时通过变量注入 |

```yaml
# ❌ 放 Packer（不灵活）
# daemon.json 被固化：
#   - 所有实例配置相同
#   - 改配置要重建 AMI
#   - 无法在构建时知道 runtime 信息

# ✅ 放 Ansible（推荐）
- name: 写入 Docker daemon 配置
  template:
    src: daemon.json.j2
    dest: /etc/docker/daemon.json
  vars:
    default_runtime: "{{ 'nvidia' if gpu_enabled else 'runc' }}"
    registry_mirror: "{{ lookup('env', 'REGISTRY_MIRROR') }}"
  notify: restart docker
```

**推荐**：放 Ansible。Daemon 配置是"中间层"——变更频率不高，但需要运行时信息。

### 重叠三：NCCL 环境变量

三个工具都能做这件事：

| 做法 | 放哪里 | 效果 |
|------|--------|------|
| `/etc/environment` 写死到 AMI | Packer | 所有实例相同，改一次重建 AMI |
| `lineinfile` / etc 模板 | Ansible | 按实例/组区别配置，随时调整 |
| Dockerfile `ENV` | Docker 镜像 | 只影响该容器，不同训练任务用不同参数 |

```dockerfile
# ✅ NCCL 参数放 Docker 层（推荐）
# Dockerfile
ENV NCCL_DEBUG=WARN
ENV NCCL_IB_DISABLE=0
ENV NCCL_NET_GDR_LEVEL=5
```

```yaml
# ⚠️ 放 Ansible 也可以（如果需要宿主机级配置）
- name: 写入 NCCL 环境变量
  lineinfile:
    path: /etc/environment
    line: "{{ item.key }}={{ item.value }}"
  loop: "{{ nccl_env_vars }}"
```

```hcl
# ❌ 放 Packer 没必要——NCCL 参数调整频繁，固化到 AMI 不划算
```

**推荐**：优先放 **Docker 层**（容器级，每个训练任务独立配置）。只在需要穿透到所有容器的场景下放 Ansible（宿主机级）。**不建议**放 Packer。

### 重叠四：用户与 SSH 配置

```yaml
# ❌ 放 Packer（不推荐）
# AMI 中固定用户列表，新员工入职要重建 AMI

# ✅ 放 Ansible（推荐）
- name: 创建训练用户
  user:
    name: "{{ item.username }}"
    uid: "{{ item.uid }}"
    groups: docker
    shell: /bin/bash
  loop: "{{ training_users }}"
  when: item.enabled | default(true)

- name: 同步 SSH 公钥
  authorized_key:
    user: "{{ item.username }}"
    key: "{{ item.ssh_key }}"
  loop: "{{ training_users }}"
```

**推荐**：放 Ansible。用户管理是典型的"快变层"——人员变动频繁，必须灵活管理。

**例外**：如果使用 LDAP/AD 统一认证，则用户管理完全不由这些工具处理。

### 重叠五：云资源编排 — Terraform vs Ansible

两个工具都能创建 VPC/子网/EC2：

```hcl
# ✅ Terraform（推荐）
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "gpu-cluster" }
}

resource "aws_instance" "gpu" {
  ami           = data.aws_ami.gpu.id
  instance_type = "p4d.24xlarge"
}
```

```yaml
# ⚠️ Ansible 也能做（不推荐）
- name: 创建 VPC
  amazon.aws.ec2_vpc_net:
    name: "gpu-cluster"
    cidr_block: "10.0.0.0/16"
```

| 维度 | Terraform | Ansible (cloud modules) |
|------|-----------|------------------------|
| **状态管理** | `tfstate` 记录精确状态，`plan` 预览变更 | 无状态，每次从头执行 |
| **资源图** | 自动解析依赖顺序（DAG） | 按 playbook 顺序执行 |
| **漂移检测** | `terraform plan` 对比真实状态 vs 代码 | 需要额外 `--diff` |
| **删除资源** | `terraform destroy` 可清理全部 | 需要手动逐一处理 |

**推荐**：创建云资源用 **Terraform**。它存在的理由就是资源编排，更精准、更安全。

**Ansible 云模块的用途**：Terraform 之外的"补充操作"——比如动态注册/注销 ALB 目标、给已有资源打标签、查询资源信息。

### 重叠六：应用部署 — Ansible vs Docker Compose vs K8s

```yaml
# ❌ 用 Ansible 部署容器（能做，不推荐）
- name: 拉取镜像
  docker_image:
    name: "{{ image }}"
    source: pull

- name: 启动容器
  docker_container:
    name: training
    image: "{{ image }}"
    state: started
```

```yaml
# ✅ 用 Docker Compose（推荐）
# docker-compose.yml
services:
  training:
    image: "{{ image }}"
    deploy:
      replicas: 8
    environment:
      - NCCL_DEBUG=WARN
```

| 做法 | 适用场景 |
|------|---------|
| **Ansible docker_container** | 单台机器上管理少数容器，适合小规模 |
| **Docker Compose** | 单机多容器，依赖编排，最适合实验环境 |
| **Kubernetes** | 多机大规模，自动调度/伸缩，生产级 |
| **Ansible** | Ansible 的角色是**安装 Docker**、**写 compose 文件**、**保证服务在跑**，而不是模块去管理容器生命周期 |

**推荐**：Ansible 负责**宿主机层的准备**（装 Docker、写 docker-compose.yml、创建网络），容器本身的管理交给 Docker Compose 或 K8s。

---

## 综合实战示例

### 场景 A：100 台 GPU 实例的云端集群

生产环境，弹性伸缩，竞价实例随时回收重建。

```
决策逻辑：
  - 实例随时重建 → Packer AMI 是必须的，不能在启动后等配置
  - 100 台同时启动 → 启动时间要短，Ansible 只在最后做微调
  - 不同项目共用集群 → NCCL 参数和用户管理要灵活
```

| 层 | 工具 | 包含内容 | 变更频率 |
|----|------|---------|---------|
| **L0 机器镜像** | Packer | Ubuntu + NVIDIA 驱动 550 + Docker + Container Toolkit + daemon.json + cloudwatch agent | 季度（驱动升级时） |
| **L1 资源编排** | Terraform | VPC、子网、安全组、ASG、EFS、S3 挂载点 | 月级（扩地域时） |
| **L2 基础配置** | Ansible | EFS 挂载、用户同步、SSH 配置、Docker 登录 registry | 周级（人员变动） |
| **L3 应用部署** | Docker Compose / K8s | 训练容器、NCCL 参数、环境变量、数据挂载 | 每次训练 |

**为什么这么分：**

- Packer 之所以负责 daemon.json，是因为所有 GPU 实例的 Docker 基础配置一样（开 NVIDIA runtime、开 buildkit），这些永远不会按实例变化
- Ansible **不**重装驱动而是在实例启动后挂载 EFS，因为 EFS 的 DNS 地址是 Terraform 创建的运行时才知道
- NCCL 参数放 Docker 层而非宿主机层，因为不同训练任务可能需要不同参数

### 场景 B：实验室 4 台裸机 GPU 服务器

小规模，物理机，长生命周期。

```
决策逻辑：
  - 没有虚拟化，没有 AMI → Packer 用不上
  - 4 台机器，手工管理不费劲 → Ansible 足够了
  - 配置变化频繁（研究环境） → 集中在 Ansible 一处管理
```

| 层 | 工具 | 包含内容 |
|----|------|---------|
| **L1 操作系统** | (手装) | Ubuntu Server |
| **L2 全部配置** | **Ansible 全覆盖** | NVIDIA 驱动、Docker、用户、NCCL、共享存储挂载 |
| **L3 应用** | Docker Compose | 训练容器 |

**Ansible playbook 覆盖全部：**

```yaml
- name: 实验室 GPU 服务器初始化
  hosts: lab_gpus
  tasks:
    # 所有操作全在 Ansible 中，没有 Packer 参与
    - name: 安装 NVIDIA 驱动
      apt: name=nvidia-driver-550

    - name: 安装 Docker + Container Toolkit
      apt: name={{ item }}
      loop: [docker.io, nvidia-container-toolkit]

    - name: 创建训练用户
      user: name={{ item }} groups=docker

    - name: 挂载 NAS
      mount: src={{ nas_dns }}:/data path=/data fstype=nfs

    - name: 写入 docker-compose
      copy: src=docker-compose.yml dest=/opt/training/
```

**和场景 A 的对比**：同样的 NVIDIA 驱动安装，在场景 A 中放 Packer（因为要弹性伸缩），在场景 B 中放 Ansible（因为没有 Packer、只有 4 台机器）。不是谁对谁错，而是**上下文决定了最优分层**。

### 场景 C：研发团队 20 台开发机（macOS + Linux）

```
决策逻辑：
  - 开发机不是 VM，没有 Packer
  - 没有云端资源，没有 Terraform
  - 工具链版本经常更新，需要灵活管理
```

→ **只用 Ansible + `ansible-pull`**

```bash
# 开发机自行拉取配置
ansible-pull -U https://github.com/team/dev-env.git plays/init.yml
```

| 工具 | 在本场景中的角色 |
|------|----------------|
| Ansible | 全部：从 Homebrew 包到 dotfiles 到 VS Code 扩展 |
| Packer | 不需要——开发机不是 VM，没有镜像概念 |
| Terraform | 不需要——没有云资源 |
| Docker | 开发工具之一（Ansible 负责安装） |

---

## 决策树

```
启动这个新任务，先问：

1. 这是构建镜像还是管理运行中的机器？
   → 构建镜像 → Packer
   → 管理机器 → 去 2

2. 这个操作变更频率是？
   → 每季度一次（OS、驱动、Docker daemon 基础配置） → 考虑能否放入 Packer
   → 每周/每月（用户、权限、中间件配置） → Ansible
   → 每次部署（应用版本、特性开关） → 考虑放到 Docker 层或 CI/CD

3. 这个操作需要运行时信息吗？
   → 是（EFS 地址、registry 认证、实例 IP） → 必须 Ansible
   → 否（所有实例都一样） → 可以放 Packer

4. 这个操作跟「云资源存在与否」有关吗？
   → 创建/删除云资源 → Terraform
   → 只是查询或打标签 → Ansible 云模块够用

5. 操作的对象是容器还是宿主机？
   → 容器内部环境 → Dockerfile
   → 宿主机的容器运行时 → Ansible（装 Docker 配 daemon）
   → 容器编排（多机多容器） → K8s 或 Docker Compose
```

### 常见误判案例

| 误判 | 原因 | 正确做法 |
|------|------|---------|
| "NCCL 参数用 Ansible 写进 /etc/environment" | 宿主机级配置，所有容器共享 | 改为写进 Docker 镜像的 ENV 或 docker-compose 的 environment，不同训练独立 |
| "Docker daemon 配置放到 AMI 里" | 这些基础配置不变 | 但 registry 地址、代理配置会变，放 Ansible 更灵活 |
| "用户管理放到 Packer AMI 里" | 人员相对固定 | 员工入职/离职不改 AMI？放 Ansible |
| "用 Ansible 的 cloud 模块替代 Terraform" | Ansible 也能创建 AWS 资源 | 但 Terraform 有状态管理和 preview，更适合资源编排 |
| "用 docker_container 模块替代 Docker Compose" | Ansible 能管理容器 | 复杂多容器场景该用 Compose 或 K8s，Ansible 只做"装 Docker + 写配置文件" |

## 关联笔记

- [[2026-05-19-ansible-自动化运维平台|Ansible 自动化运维平台]] — 快变层管理的具体 pattern
- [[2026-05-19-IaC基础设施即代码工具链|IaC 工具链综述]] — Terraform/Packer/Ansible 三大工具的对比表格
- [[容器化管理实验环境最佳实践]] — Docker 容器化在 AI Infra 中的完整实践
- [[2026-05-19-jupyter-docker-stacks-JupyterDocker镜像套件|Jupyter Docker Stacks]] — 容器化 Jupyter 环境的实际工具
