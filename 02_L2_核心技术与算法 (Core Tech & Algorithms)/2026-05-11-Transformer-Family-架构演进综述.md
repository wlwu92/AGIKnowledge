---
source: "https://lilianweng.github.io/posts/2020-04-07-the-transformer-family/"
created: 2026-05-11
tags:
  - layer/l2
  - type/survey
  - domain/llm
  - method/transformer
---

# The Transformer Family — 架构演进综述

> **作者**: Lilian Weng (OpenAI)
> **时间**: 2020-04（v2.0 2023）
> **来源**: Lil'Log

## 覆盖的架构变体

| 变体 | 核心创新 | 适用场景 |
|------|----------|----------|
| **Transformer-XL** | 重用隐藏状态 + 相对位置编码，解决长序列上下文断裂 | 长文本建模 |
| **Adaptive Attention Span** | 每头可学习的注意力范围掩码，低层短距/高层长距 | 效率优化 |
| **Image Transformer** | 局部注意力（1D/2D 邻域），控制像素级计算量 | 图像生成 |
| **Sparse Transformer** | 稀疏因子化注意力矩阵，支持 16K+ 序列 | 长序列建模 |
| **Reformer** | LSH 哈希注意力 O(L²)→O(L log L) + 可逆残差层 | 超大模型训练 |
| **Universal Transformer** | Transformer + RNN 式循环迭代，共享跨位置参数 | 序列推理 |
| **GTrXL** | LayerNorm 重排序 + GRU 门控残差连接 | RL 中的 Transformer |

## 关联知识

- [[Attention Is All You Need]] - 原始 Transformer
- [[Transformer-XL]] - 长序列优化
- [[Reformer]] - 高效注意力

## 思考

Lilian Weng 的经典综述。虽然 2020 年的版本没有覆盖 BERT/GPT/XLNet（这些在她 2019 年的 LM 综述里），但架构层面的变体梳理至今仍有参考价值。2023 年有 v2.0 更新，值得跟进。

[原文链接](https://lilianweng.github.io/posts/2020-04-07-the-transformer-family/)
