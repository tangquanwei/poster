
**简历项目经历**

**语音热词检索系统 / 声学-文本跨模态对齐**
技术栈：`PyTorch`、`DeepSpeed`、`Paraformer`、`BERT`、`CIF`、`Contrastive Learning`

- 面向语音热词检索任务，构建不依赖完整 ASR 转写的声学-文本跨模态检索框架，用于判断候选热词是否在输入语音中出现，降低 ASR 转写错误对热词召回的影响。
- 基于 Paraformer 声学编码器和 BERT 文本编码器搭建双塔检索模型，引入 CIF 将帧级语音表示压缩为 acoustic tokens，并通过 quantity loss 约束声学 token 与文本 token 的长度一致性。
- 设计局部热词匹配流程，根据候选热词 token 长度在 acoustic token 序列上滑动窗口，并使用 token-level MaxSim 计算局部相关性，使模型能够在长语音中定位并检索短热词片段。
- 实现 Stage1 CIF 预训练与 Stage2 联合检索训练，结合 local contrastive loss、CIF loss 和 token-level 辅助对齐目标，并处理 batch 内热词冲突导致的 false negative 问题。
- 搭建 DeepSpeed 分布式训练、离线评估和诊断链路，支持 Top-K、阈值 Precision/Recall/F1、分支消融、seen/unseen 分桶和 bad case 分析；针对多候选热词检索实现 batched GEMM diagonal 打分优化，提升局部匹配推理效率。
- 实现中文AISHELL测试集F1 96+%, 英文测试集 F1 85+%
- 跑通 数据处理、模型训练、量化部署、评估测试 全流程。实现30s语音，2k热词 检索延迟<200ms。

**更短版**

如果简历空间紧，可以压缩成这样：

- 构建基于 Paraformer + BERT 的语音热词检索系统，通过 CIF 将帧级语音表示压缩为 acoustic tokens，并使用局部滑窗 MaxSim 实现声学片段与候选热词的细粒度匹配。
- 实现 Stage1 CIF 预训练与 Stage2 联合检索训练，结合对比学习、CIF quantity loss 和 false-negative 过滤，提升短热词在长语音中的检索稳定性。
- 搭建 DeepSpeed 分布式训练与离线评估链路，支持 Top-K、PRF、分支消融和 bad case 诊断，并通过 batched GEMM diagonal 优化多候选热词打分效率。

**面试讲述版本**

这个项目做的是语音热词检索。传统方案一般先做 ASR，再在转写文本里匹配热词，但人名、地名、专有名词容易被 ASR 识别错，错误会直接传递到热词检索。所以这个项目直接在语音表示和候选热词文本表示之间做跨模态检索。

模型结构上，我用了 Paraformer 提取帧级声学表示，用 BERT 编码候选热词文本。核心是引入 CIF，把连续语音帧压缩成接近文本 token 粒度的 acoustic tokens，再根据热词长度在 acoustic token 序列上做滑动窗口匹配，用 MaxSim 计算局部相关性。这样模型不是只看整句语音的全局表示，而是能在长语音里找到和短热词最相关的局部片段。

训练上分两阶段：第一阶段训练 CIF 的数量预测，让 acoustic token 数量和文本 token 数量尽量对齐；第二阶段做联合检索训练，主要优化 local contrastive loss，同时保留 CIF 约束和 token-level 辅助对齐。工程上我也做了 DeepSpeed 分布式训练、离线评估、消融分析和 bad case 诊断，并针对多候选热词打分实现了 batched GEMM diagonal 优化，减少局部匹配的推理开销。

**面试可补充指标**

如果面试官追问结果，可以说：

- 在 Test-Aishell1-NE 离线评估集上，最佳阈值 F1 约 95%，Top1 命中率约 99%。
- local 分支是主要有效信号，global pooled embedding 单独效果明显较弱。
- batched GEMM diagonal 后端在保持指标基本一致的情况下，显著降低 local scoring 耗时。