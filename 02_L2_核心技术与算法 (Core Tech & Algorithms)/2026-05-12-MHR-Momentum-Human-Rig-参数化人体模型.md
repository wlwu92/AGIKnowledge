---
source: https://github.com/facebookresearch/MHR
created: 2026-05-12
tags:
  - layer/l2
  - type/paper
  - domain/cv
  - domain/graphics
  - topic/human-mesh-recovery
  - topic/parametric-body-model
  - entity/mhr
  - entity/meta
---

# MHR (Momentum Human Rig) — 解剖学启发参数化人体模型

## 概述

Meta 开发的开源、解剖学启发的参数化 3D 人体模型，同时服务计算机图形学 (CG) 和计算机视觉 (CV) 社区。

**论文**: arXiv 2511.15586
**License**: Apache-2.0

## 参数化

- **身份参数**: 45 个参数（身体 20 + 头部 20 + 手部 5），范围 -3 ~ +3
- **全身姿态**: 204 个参数编码关节角度和缩放
- **面部表情**: 72 个参数，范围 -1 ~ +1

## 技术特点

- **7 级细节层次 (LOD 0-6)**: 平衡质量与计算开销
- **非线性姿态矫正**: 基于 MLP 稀疏激活的神经网络
- **PyTorch 集成**: GPU 加速推理
- **TorchScript**: 无需完整代码库即可使用
- **SMPL/SMPL-X 转换工具**: 与其他模型互操作

## 相关项目

MHR 是 [[02_L2_核心技术与算法 (Core Tech & Algorithms)/2026-05-12-SAM-3D-Body-单图全身3D网格恢复.md|SAM 3D Body]] 的基础网格表示。支持 PyMomentum 框架。

## 前向运动学性能分析

### 问题：串行 FK 计算

MHR 的 127 个关节构成一棵骨骼树，前向运动学（FK）存在**父子依赖**——每个关节的世界变换必须等其父关节计算完成：

$$T_{\text{world}}[j] = T_{\text{world}}[\text{parent}(j)] \times T_{\text{local}}[j]$$

这种依赖导致 FK 无法在 GPU 上完全并行——每层关节必须等父关节算完。

### 当前实现：倍增算法（Prefix Multiplication）

MHR 使用 **倍增（binary lifting / parallel prefix scan）** 技术将串行步数从 O(D) 降低到 O(log D)。

**索引生成**（`pymomentum/backend/utils.py` → `calc_fk_prefix_multiplication_indices`）：

对每个关节构建从根到该关节的运动链，按二进制位拆分：

```
例：链状 root(0)→1→2→3→4→5→6→7
joint 7 的 kc = [0,1,2,3,4,5,6,7], idx=7 (二进制 111)
Level 0: state[7] *= state[6]  (2^0=1 步)
Level 1: state[7] *= state[5]  (2^1=2 步)
Level 2: state[7] *= state[3]  (2^2=4 步)
```

数学本质：关节索引二进制分解 $j = \sum 2^k$，每次跳跃 $2^k$ 步。

**核心循环**（`pymomentum/backend/skel_state_backend.py` → `global_skel_state_from_local_skel_state_impl`）：

```python
@th.jit.script
def global_skel_state_from_local_skel_state_impl(
    local_skel_state, prefix_mul_indices
):
    global_skel_state = local_skel_state.clone().double()  # float64!
    for prefix_mul_index in prefix_mul_indices:  # O(log N) 次串行
        source = prefix_mul_index[0]
        target = prefix_mul_index[1]
        state1 = global_skel_state.index_select(-2, target)
        state2 = global_skel_state.index_select(-2, source)
        # world_child = world_parent * local_child
        result = skel_state.multiply(state1, state2)
        global_skel_state.index_copy_(-2, source, result)
    return global_skel_state
```

每 Level 内部的对之间**无数据依赖**（可 batch 并行），但 Level 之间**必须串行**。

### 复杂度对比

| 方案 | 顺序步数 | 总计算量 | 冗余 |
|-----|---------|---------|------|
| 朴素顺序 | O(D) ≈ 30 | O(N) ≈ 127 | 无 |
| **倍增（当前）** | **O(log D) ≈ 5-7** | **O(N log D) ≈ 635-889** | **有** |
| BFS 波前 | O(D) ≈ 30 | O(N) ≈ 127 | 无 |

倍增用更多总计算量换串行步数降低。

### 实际性能瓶颈

```
当前瓶颈（按影响排序）：
1. Python for 循环下 5-7 次独立的 CUDA kernel launch    ← 最大开销 (~10µs/次)
2. 每次 Level 间 index_select → multiply → index_copy_  ← 显存往返
3. 使用 float64 精度                                    ← 数据搬运翻倍
```

### 优化方向

#### 方案 A：CUDA Kernel 融合（推荐）

将整个倍增 FK 写成一个 CUDA kernel，在 **shared memory** 内完成全部 Level：

```cuda
__global__ void fused_fk_kernel(...) {
    __shared__ float state[127 * 8];  // ~4KB，轻松放入 shared memory
    // 一次加载 → 7 层 shared memory 内运算 → 一次写回
    // 仅需 __syncthreads() barrier，零显存往返
}
```

**预估加速比**：3-8×。

#### 方案 B：降精度

当前 `.double()`（float64）改 float32——数据搬运直接减半。

### 代码对应关系

| 层次 | 文件 | 关键函数 |
|------|------|---------|
| SAM 触发点 | `sam_3d_body/models/heads/mhr_head.py` | `MHRHead.mhr_forward()` → `self.mhr(...)` |
| MHR 转发 | `mhr/mhr.py` | `forward()` → `joint_parameters_to_skeleton_state()` |
| FK 调度 | `pymomentum/torch/character.py:173-176` | `local_skeleton_state_to_skeleton_state()` |
| **FK 核心循环** | **`pymomentum/backend/skel_state_backend.py:20-46`** | **`global_skel_state_from_local_skel_state_impl()`** |
| 倍增表生成 | `pymomentum/backend/utils.py:33-70` | `calc_fk_prefix_multiplication_indices()` |
| C++ 参考 | `momentum/character/skeleton_state.cpp` | `SkeletonStateT::set()` 朴素顺序 FK |
