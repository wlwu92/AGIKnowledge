---
source: "https://github.com/kubernetes-sigs/kubespray"
created: 2026-05-20
aliases:
  - K8s部署工具链
tags:
  - layer/l3
  - type/survey
  - domain/ai-infra
---

# Kubernetes 部署与基础设施工具

## 覆盖范围

本综述梳理生产环境 Kubernetes 集群部署与基础设施管理生态中的三个互补工具：kubespray、KubeKey、Harbor。它们在 K8s 生命周期中各司其职：

| 工具 | 职责 | 核心能力 | 仓库 |
|------|------|----------|------|
| **kubespray** | 集群部署 | Ansible 驱动的生产级 K8s 部署，支持多种 CNI/CRI | [kubernetes-sigs/kubespray](https://github.com/kubernetes-sigs/kubespray) |
| **KubeKey** | 集群部署+扩展 | 一键安装 K8s 及云原生插件，支持 all-in-one / multi-node / HA | [kubesphere/kubekey](https://github.com/kubesphere/kubekey) |
| **Harbor** | 容器镜像仓库 | 可信云原生制品仓库，支持镜像签名、扫描、复制 | [goharbor/harbor](https://github.com/goharbor/harbor) |

## 发展脉络

### kubespray（K8s SIG 项目）

基于 Ansible 的 Kubernetes 部署工具，由 Kubernetes SIG-Cluster-Lifecycle 维护。核心特点：
- Ansible Playbook 驱动，基础设施无关（bare metal / cloud / vSphere）
- 支持多种 CNI（Calico, Flannel, Weave, Cilium）和 CRI（containerd, CRI-O, Docker）
- 高可用控制平面（stacked/ external etcd）
- 离线部署支持

项目成熟度高，社区活跃，是生产环境部署的稳妥选择。

### KubeKey（KubeSphere 生态）

KubeSphere 社区开发的部署工具，与 kubespray 的关键区别：
- **更简洁**：单一二进制文件，无需 Ansible/SSH 前置依赖
- **扩展性**：不仅是部署工具，还可管理节点扩缩容和升级
- **插件机制**：支持一键安装 KubeSphere、DevOps、Service Mesh 等云原生插件
- **模式灵活**：All-in-One（学习/测试）、Multi-Node（生产）、HA（高可用）

适合需要快速搭建完整云原生生态的场景。

### Harbor（CNCF Graduated）

云原生制品仓库，属于 CNCF 毕业项目。核心能力：
- **多格式支持**：OCI 镜像、Helm Chart、CNAB
- **安全集成**：镜像签名（Cosign/Notation）、漏洞扫描（Trivy/Clair）、CVE 策略
- **复制能力**：跨数据中心异步/同步复制，灾备和加速
- **身份集成**：LDAP/OIDC/RBAC 认证
- **清理策略**：自动清理过期/未使用制品

## 核心对比

| 维度 | kubespray | KubeKey | Harbor |
|------|-----------|---------|--------|
| 定位 | K8s 集群部署 | K8s 集群部署+生态扩展 | 制品仓库 |
| 依赖 | Ansible, Python, SSH | 二进制, SSH | Docker / containerd |
| 学习曲线 | 中（需了解 Ansible） | 低（简单命令） | 低 |
| 社区 | K8s SIG | KubeSphere | CNCF |
| 互补关系 | KubeKey 可替代 kubespray 的部署职能 | 部署后可对接 Harbor 作为镜像仓库 | 独立基础设施组件 |

## 知识地图

- **上层编排**：kubernetes 本身作为容器编排层
- **基础设施**：与 [[2026-05-19-IaC基础设施即代码工具链|IaC 工具链]] 中 Terraform + Ansible + Packer 协作
  - Terraform 创建云资源（VM、LB），kubespray/KubeKey 在其上部署 K8s
- **存储集成**：Harbor 的持久化可对接 [[cephfs-分布式文件系统调研|CephFS]] 或 [[beegfs-并行文件系统|BeeGFS]]
- **相关笔记**：[[2026-05-19-分层决策-PackerAnsibleTerraformDocker的分工与边界|IaC 工具分工与边界]]

## 关联笔记

- [[2026-05-19-分层决策-PackerAnsibleTerraformDocker的分工与边界|IaC 工具分工与边界]]
- [[2026-05-19-IaC基础设施即代码工具链|IaC 工具链]]
- [[cephfs-分布式文件系统调研|CephFS]]
- [[beegfs-并行文件系统|BeeGFS]]

## 判断与局限

- **成熟度**：三个项目均为生产级（kubespray 和 Harbor 是 CNCF/K8s SIG 项目，KubeKey 有 KubeSphere 社区支撑）
- **独立性**：Harbor 是独立基础设施组件，不与特定部署工具绑定；kubespray 和 KubeKey 在部署层面互为替代/竞品
- **演进趋势**：KubeKey 的低门槛特性更适合团队快速验证，kubespray 的 Ansible 驱动更适合已有 Ansible 基础设施的团队
- **局限**：三者均面向运维团队，非运维人员仍需编排层封装（如 GitOps + ArgoCD 工作流）
