---
source: "https://arxiv.org/abs/2603.12533"
created: 2026-05-11
aliases:
  - EgoPointVQA
  - HINT
tags:
  - CV
  - 多模态
  - 手部重建
  - 手势理解
  - 第一人称视角
  - CVPR2026
  - LLM应用
---

# EgoPointVQA / HINT: 手势引导的第一人称视频问答

> **Do You See What I Am Pointing At? Gesture-Based Egocentric Video Question Answering**
>
> **作者**: Yura Choi, Roy Miles, Rolandos Alexandros Potamias, Ismail Elezi, Jiankang Deng, Stefanos Zafeiriou (Imperial College London)
> **会议**: CVPR 2026
> **论文**: [arXiv 2603.12533](https://arxiv.org/abs/2603.12533)
> **项目页**: [https://yuuraa.github.io/papers/choi2026egovqa](https://yuuraa.github.io/papers/choi2026egovqa)

## 核心贡献

将 [[2026-05-11-HaWoR-世界坐标系手部运动重建|HaWoR]]/[[2026-05-11-WiLoR-端到端3D手部定位与重建|WiLoR]] 的 3D 手部重建能力用于**第一人称视频中的手势意图理解**——当用户戴着智能眼镜指着一个物体问"What is that?"，模型需要理解"指"这个手势指向的目标。

## 方法：Hand Intent Tokens (HINT)

双流架构：

```
视频帧 → Vision Encoder → visual tokens ─┐
                                          ├→ LLM → 答案
帧 + 手部关键点 → WiLoR → Keypoint Adapter → HINT tokens ─┘
```

- **视觉流**：标准视觉编码器 → 视觉 token
- **手势意图流**：[[2026-05-11-WiLoR-端到端3D手部定位与重建|WiLoR]] 每帧提取 21 个 3D 手部关键点 → **Keypoint Adapter**（两层 MLP + GeLU）→ **HINT token**
- HINT token 与视觉 token 交错输入 LLM
- 手部检测置信度 < 0.5 时跳过插入
- 额外推理开销极小：2.58s → 2.84s，HINT token 占比 < 1% LLM 输入

## 数据集：EgoPointVQA

首个针对**指向性手势问答**的 egocentric 视频数据集：

| 拆分 | 视频数 | QA 对数 |
|------|--------|---------|
| 合成训练 | 4,000 | 18,745 |
| 真实训练 | 100 | 640 |
| 真实测试 | 300 | 672 |

**6 类任务**：Reference（指向识别）、Counting（计数）、Spatial（空间关系）、Temporal（时序）、Attribute（属性）、Feedback（反馈）

**数据采集**：合成视频由 AI2-THOR 仿真器 + MIXAMO 动画生成；真实视频由 20 名参与者佩戴 Meta Ray-Ban 智能眼镜采集。

## 主要结果

| 模型 | 平均准确率 |
|------|-----------|
| **HINT-14B** | **68.1%** |
| Qwen3-VL-32B | 67.5% |
| GPT-5 | 62.6% |
| InternVL3-14B | 62.7% |
| 人类 | 95.9% |

在 Reference 任务上，HINT-8B 从 66.1% 提升至 **75.0%**（+8.9pp）。

## 关联笔记

- [[2026-05-11-HaWoR-世界坐标系手部运动重建|HaWoR]] — 世界坐标系手部重建（CVPR 2025 Highlight），本工作的底层手部重建能力来源
- [[2026-05-11-WiLoR-端到端3D手部定位与重建|WiLoR]] — 单图 3D 手部检测+重建 backbone，HINT 直接使用其关键点输出
- [[2026-05-11-Dyn-HaMR-动态相机下双手4D运动重建|Dyn-HaMR]] — 平行互补的双手全局运动重建

## 思考

这是 [[2026-05-11-HaWoR-世界坐标系手部运动重建|HaWoR]] 的"手部重建能力→高层语义理解"的**直接应用延伸**。说明 3D 手部重建不是终点，而是具身 AI 助手的感知基础设施。Meta Ray-Ban 智能眼镜作为采集设备也暗示了 AR 眼镜作为未来人机交互平台的技术路径。
