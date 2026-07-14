



## 一、先从读者视角提炼结果

假设表中的“zh+en”和“zh”分别表示**中英双语训练**与**仅中文训练**，这组结果最有价值的叙事不是：

> TLDR 在所有指标上都比基线高。

因为这并不完全成立，而且 R@5、R@10 在多个数据集上已经饱和。

真正有说服力的结论是：

> **TLDR 在简单、同域数据上与强基线相当，但随着测试条件变难、领域发生偏移或训练语言覆盖受限，其优势显著扩大。**

这正好对应 token-level late interaction 应该解决的问题：不是进一步“刷高”简单样本，而是在局部证据弱、候选容易混淆、模型泛化困难时，保留更细粒度的匹配信息。

---

# 二、结果中最重要的三个发现

## 2.1 双语训练：TLDR 的检测性能稳定领先

定义 TLDR 相对最强基线的绝对增益为：

$$
\Delta_{\mathrm{F1}}
=
\mathrm{F1}_{\mathrm{TLDR}}
-
\max
\left(
\mathrm{F1}_{\mathrm{GLCLAP}},
\mathrm{F1}_{\mathrm{CLAR}}
\right)
$$

其中：

- $\mathrm{F1}_{\mathrm{TLDR}}$：TLDR 的 F1；
- $\mathrm{F1}_{\mathrm{GLCLAP}}$：GLCLAP 的 F1；
- $\mathrm{F1}_{\mathrm{CLAR}}$：CLAR 的 F1；
- $\Delta_{\mathrm{F1}}$：TLDR 相对最强基线提升的百分点。

双语训练下：

| 测试集 | 最强基线 F1 | TLDR F1 | $\Delta_{\mathrm{F1}}$ |
|---|---:|---:|---:|
| AISHELL1-NE | 94.5 | 96.2 | +1.7 |
| ContextASR-ZH | 94.4 | 96.7 | +2.3 |
| ContextASR-EN | 82.0 | 88.8 | **+6.8** |
| AISpeech-Meeting | 69.3 | 69.8 | +0.5 |
| Macro Average | 85.1 | 87.9 | **+2.8** |

这里的核心观察是：

1. TLDR 在四个数据集上都取得最高 F1；
2. 在 AISHELL1-NE 和 ContextASR-ZH 上，R@5、R@10 已接近或达到 100%，存在明显的天花板效应；
3. 最大增益出现在更困难的 ContextASR-EN 上，F1 提升 6.8 个百分点；
4. Meeting 数据上的提升只有 0.5，需要置信区间或多随机种子验证，不能直接宣称显著提升。

因此论文中不要强调“TLDR 将 R@10 从 99.9 提高到 100”，这种结果没有信息量。应强调：

> TLDR 的主要优势体现在阈值判别质量，而不是已经饱和的粗粒度候选召回。

---

## 2.2 中文训练：越困难的测试条件，TLDR 的优势越明显

仅中文训练时：

| 测试集 | 最强基线 F1 | TLDR F1 | $\Delta_{\mathrm{F1}}$ |
|---|---:|---:|---:|
| AISHELL1-NE | 96.9 | 96.8 | -0.1 |
| ContextASR-ZH | 80.6 | 92.6 | **+12.0** |
| ContextASR-EN | 1.3 | 8.7 | **+7.4** |
| AISpeech-Meeting | 49.3 | 65.8 | **+16.5** |
| Macro Average | 57.0 | 66.0 | **+9.0** |

这是目前最强的一组结果。

它展示了非常清楚的难度依赖关系：

- 在简单、同域、接近饱和的 AISHELL1-NE 上，TLDR 与 CLAR 基本持平；
- 在 ContextASR-ZH 上，提升 12.0 个百分点；
- 在 AISpeech-Meeting 上，提升 16.5 个百分点；
- 在未见英语训练条件下，TLDR 的绝对性能仍然较低，但退化明显慢于两个基线。

这可以形成论文的核心经验结论：

> **细粒度 token-level interaction 的价值随着任务难度增加而扩大。全局或池化表示足以处理简单样本，但在分布偏移、低资源训练和困难声学环境中，局部证据保存变得关键。**

这比单纯说“TLDR 更强”更有研究价值，因为它回答了：

> TLDR 在什么情况下有效，以及为什么简单数据集上的收益不明显。

---

## 2.3 TLDR 的优势主要是困难条件下的精确判别，而非普遍提高召回

观察 Precision 和 Recall：

### 中文训练，ContextASR-ZH

- CLAR：P/R = 78.9/82.3；
- TLDR：P/R = 91.4/93.9。

TLDR 同时提升：

- Precision：+12.5；
- Recall：+11.6；
- F1：+12.0。

这表明提升不是简单调整阈值造成的，而是正负样本可分性整体改善。

### 中文训练，AISpeech-Meeting

- CLAR：P/R = 48.4/50.2；
- TLDR：P/R = 68.6/63.3。

提升为：

- Precision：约 +20.2；
- Recall：约 +13.1；
- F1：+16.5。

这里尤其值得强调 Precision 的提升。它可能意味着 token-level late interaction 能更好地拒绝声学上局部相似、但并未真正出现的候选词。

### 双语训练，AISpeech-Meeting

- CLAR：P/R = 71.3/67.4；
- TLDR：P/R = 73.7/66.3。

TLDR 提高 Precision，但略微降低 Recall，最终 F1 只增加 0.5。

这说明在双语充分训练时，Meeting 数据上的提升更像是：

> 更保守、更精确的检索边界，而不是全面提升。

论文中应当诚实呈现这种 trade-off，而不是只报告 F1。

---

# 三、当前结果中必须主动解释的两个异常

## 3.1 ContextASR-ZH 中文训练：F1 大幅提升，但 R@1 反而下降

结果是：

| Model | F1 | R@1 |
|---|---:|---:|
| CLAR | 80.6 | **96.7** |
| TLDR | **92.6** | 95.0 |

TLDR 的 F1 提升 12.0，但 R@1 下降 1.7。

这不是矛盾，因为两类指标衡量的对象不同：

- F1 是**阈值判别指标**：一个候选是否应该被检索出来；
- R@1 是**排序指标**：真实热词是否位于候选列表第一名。

可能出现以下情况：

- TLDR 更好地区分“相关候选”和“不相关候选”，因此 F1 更高；
- 但多个相关候选之间的内部排序不如 CLAR，或者少量样本的第一名发生交换，因此 R@1 略低。

然而审稿人也会提出另一种解释：

> F1 提升是否主要来自更好的分数校准或更适合的阈值，而不是真正更好的表示？

因此需要补充：

1. Precision–Recall 曲线；
2. Average Precision；
3. 正样本和最困难负样本的分数分布；
4. 所有模型统一的阈值选择协议。

最推荐分析 hardest-negative margin：

$$
m_i
=
s_i^{+}
-
\max_{j \in \mathcal{N}_i}s_{ij}^{-}
$$

其中：

- $i$：第 $i$ 条语音；
- $s_i^{+}$：真实热词与语音的相似度；
- $\mathcal{N}_i$：第 $i$ 条语音对应的负候选集合；
- $s_{ij}^{-}$：第 $j$ 个负候选的相似度；
- $m_i$：真实热词相对最困难负候选的分数间隔。

如果 TLDR 的 $m_i$ 分布整体向右移动，就能证明：

> TLDR 确实扩大了正样本与 hardest negative 的判别间隔，而不只是改变了输出分数尺度。

---

## 3.2 中文训练下 ContextASR-EN 的相对提升很大，但绝对性能仍然低

结果为：

| Model | F1 | R@1 | R@5 | R@10 |
|---|---:|---:|---:|---:|
| GLCLAP | 1.3 | 0.2 | 0.7 | 1.0 |
| CLAR | 1.3 | 1.4 | 6.4 | 11.4 |
| TLDR | **8.7** | **16.7** | **36.7** | **53.4** |

TLDR 相对提升非常明显：

- R@1：+15.3；
- R@5：+30.3；
- R@10：+42.0。

但 F1 只有 8.7，所以不能写成：

> TLDR achieves strong zero-shot English retrieval performance.

更准确的表述是：

> TLDR substantially improves zero-shot candidate ranking under Chinese-only training, although reliable cross-lingual detection remains challenging.

中文意思是：

> TLDR 在仅中文训练条件下显著提高了英语候选排序能力，但绝对检测性能仍然有限，跨语言热词检索仍是一个开放问题。

这类诚实表述反而会增强可信度。

---

# 四、主表应该怎样重新设计

你现在的表有几个问题：

1. 每个单元格同时放 F1/P/R，阅读负担很大；
2. 检测指标和排序指标混在一起；
3. 24 行结果横向展开成 8 个复杂列，难以快速比较；
4. “zh en”和“zh”作为空白分组行不够规范；
5. 大量 R@5/R@10 已饱和，遮蔽了真正的差异。

建议拆成两个子表。

---

## Table 1：Threshold-based hotword detection

列为：

| Training | Dataset | Model | Precision | Recall | F1 | $\Delta$F1 |
|---|---|---|---:|---:|---:|---:|

目的：回答

> 模型能否正确决定哪些热词应该被返回？

排版规则：

- F1 放在最后并加粗；
- 最佳结果加粗，第二名加下划线；
- $\Delta$F1 只在 TLDR 行报告；
- 标注统计显著性，例如 $\dagger$ 表示相对 CLAR 的提升通过 bootstrap 检验；
- 分成 `(a) ZH+EN training` 和 `(b) ZH-only training` 两个 panel。

F1 应当作为这张表的核心，因为当前最显著的收益都出现在 F1 上。

---

## Table 2：Candidate ranking performance

列为：

| Training | Dataset | Model | R@1 | R@5 | R@10 |
|---|---|---|---:|---:|---:|

目的：回答

> 当真实热词位于候选库中时，它能否排在前面？

这里需要避免过度解读已经饱和的数字。正文主要讨论：

- R@1；
- 中文训练 ContextASR-EN 的 R@1/R@5/R@10；
- 中文训练 AISpeech-Meeting 的完整 Recall@K。

其他接近 100% 的 R@5/R@10 可以简短说明存在 ceiling effect。

如果篇幅非常紧，正文保留 R@1 和 R@10，完整 R@1/R@5/R@10 放附录。

---

# 五、建议在正文加入一个“增益摘要表”

主表负责完整性，增益表负责传达核心结论。

| Training regime | AISHELL1-NE | ContextASR-ZH | ContextASR-EN | Meeting | Macro |
|---|---:|---:|---:|---:|---:|
| ZH+EN | +1.7 | +2.3 | **+6.8** | +0.5 | +2.8 |
| ZH only | -0.1 | **+12.0** | +7.4 | **+16.5** | +9.0 |

表中数字为 TLDR 相对最强基线的绝对 F1 增益。

这个表能让读者在五秒内理解：

- 双语训练时平均提升 2.8；
- 中文训练时平均提升扩大到 9.0；
- 简单同域数据基本持平；
- 困难域提升明显。

不过 Macro Average 只能作为总结，不能替代逐数据集结果，因为不同数据集的规模和难度不同。表注中应写清楚这是四个数据集等权平均。

---

# 六、最应该画的三张图

## Figure A：Baseline difficulty versus TLDR improvement

横轴：

$$
\mathrm{F1}_{\mathrm{best\ baseline}}
$$

纵轴：

$$
\Delta_{\mathrm{F1}}
$$

每个点代表一个“训练配置 × 测试集”。

如果图中呈现出：

- 基线 F1 高时，TLDR 增益接近零；
- 基线 F1 低时，TLDR 增益变大；

那么它直接支持：

> TLDR 的作用不是在简单样本上制造微小收益，而是在全局池化和粗粒度匹配开始失效时保留有效局部证据。

但目前只有 8 个点，这张图更适合作为结果总结图，而不能单独作为严格统计结论。

---

## Figure B：从 ZH+EN 到 ZH-only 的性能退化

对每个模型画两点连线：

- 左侧：ZH+EN；
- 右侧：ZH-only；
- 纵轴：F1。

重点画 ContextASR-ZH 和 AISpeech-Meeting。

从现有结果看：

### ContextASR-ZH 的 F1 下降

- GLCLAP：下降 11.6；
- CLAR：下降 13.8；
- TLDR：只下降 4.1。

### AISpeech-Meeting 的 F1 下降

- GLCLAP：下降 18.0；
- CLAR：下降 20.0；
- TLDR：只下降 4.0。

这是很强的稳健性证据。可以表述为：

> 当训练语言覆盖或训练数据规模受到限制时，TLDR 在中文跨域测试上的退化明显小于池化式基线。

但必须检查一个混杂因素：ZH+EN 和 ZH-only 是否仅仅语言不同，还是训练数据总量也不同。如果数据量不同，就不能把结果完全归因于语言覆盖，应称为“restricted training condition”。

---

## Figure C：正样本与 hardest negative 的 score margin

建议对三个数据集分别画分布：

1. AISHELL1-NE：简单、接近饱和；
2. ContextASR-ZH：TLDR F1 大幅提升但 R@1 略低；
3. AISpeech-Meeting：最明显的困难域收益。

分别展示 GLCLAP、CLAR、TLDR 的 $m_i$ 分布。

预期结果：

- AISHELL1-NE：三个模型差异较小；
- ContextASR-ZH：TLDR 的 margin 整体更大；
- Meeting：TLDR 显著减少负 margin 样本。

这张图比单纯画 attention heatmap 更有说服力，因为它直接连接：

> token-level matching → hardest-negative separation → F1 improvement。

---

# 七、结果章节的推荐叙事顺序

## 4.1 Overall Performance

回答：

> TLDR 是否整体优于现有方法？

内容：

- 放完整主表；
- 报告 TLDR 在 8 个设置中取得 7 个最高 F1；
- 双语训练 Macro-F1 从 85.1 提升到 87.9；
- 中文训练 Macro-F1 从 57.0 提升到 66.0；
- 明确说明简单数据集存在饱和。

不要逐个朗读表中所有数字。

---

## 4.2 When Does Token-Level Interaction Help?

回答：

> TLDR 的增益出现在哪里？

将数据集分成：

- Easy/in-domain：AISHELL1-NE；
- Cross-domain or difficult：ContextASR-ZH、Meeting；
- Language-mismatched：中文训练下的 ContextASR-EN。

核心结论：

> TLDR 在简单设置中与强基线相当，但在困难或训练受限条件下优势显著扩大。

这是整个实验部分最重要的一节。

---

## 4.3 Detection versus Ranking

回答：

> 为什么 F1 和 R@1 有时表现不一致？

展示：

- PR 曲线；
- Average Precision；
- hardest-negative margin；
- 阈值敏感性曲线。

重点分析中文训练 ContextASR-ZH：

- TLDR F1 +12.0；
- R@1 -1.7。

这能把一个潜在弱点转化成有价值的机制分析：

> 集合判别与候选内部排序是两个不同目标，TLDR 当前主要改善前者。

---

## 4.4 Fine-Grained Breakdown

为了证明收益确实来自 token-level late interaction，至少按照以下因素拆分：

- 热词长度；
- 语音时长；
- 候选集大小；
- 语音中热词所占的时间比例；
- 音近词；
- 子串候选；
- 训练中见过与未见过的热词；
- 单字、双字、多字热词。

最理想的预期结果是：

- 热词越短，global pooling 越容易稀释证据；
- 音近或子串候选越多，frame-level MaxSim 越容易出现虚假峰值；
- TLDR 在这些困难分组上的增益最大。

这样结果才能从“TLDR 数字更高”升级为：

> 为什么 token-level granularity 是热词检索更合适的归纳偏置。

---

# 八、审稿人会立即检查的问题

## 8.1 三个模型是否使用相同 backbone

如果 GLCLAP、CLAR 和 TLDR 使用不同语音编码器、文本编码器或预训练模型，当前结果只能证明：

> TLDR 完整系统优于其他完整系统。

不能证明：

> token-level late interaction 优于 global/local pooling。

论文必须同时提供两类实验：

### Full-system comparison

与原始 GLCLAP、CLAR 配置比较，说明实际系统性能。

### Controlled comparison

固定：

- speech encoder；
- text encoder；
- projection dimension；
- training data；
- batch size；
- loss；
- candidate pool；
- training steps。

只替换：

- global pooling；
- frame-level local matching；
- CIF-token late interaction。

机制结论必须主要依赖 controlled comparison。

---

## 8.2 阈值如何确定

F1 是高度依赖阈值的。

需要在表注或实验设置中明确：

- 阈值是否在 validation set 上选择；
- 是否每个模型使用独立验证阈值；
- 是否每个数据集单独选阈值；
- 是否将 test set 用于选择 best-F1；
- 所有模型是否采用相同的校准流程。

绝对不能在测试集上寻找最优阈值后，直接将 best-F1 当作主结果，而不作说明。

建议同时报告 threshold-free 的 Average Precision，以降低审稿人对阈值选择的疑虑。

---

## 8.3 小幅增益是否显著

以下差异可能落在随机波动范围：

- Meeting 双语训练：+0.5 F1；
- AISHELL1-NE 的 R@1：+0.3；
- R@10 的 0.1 差异。

建议：

- 至少三个随机种子；
- 报告 mean ± standard deviation；
- 对测试 utterance 做 paired bootstrap；
- 小差异没有通过检验时标为 statistically tied。

---

# 九、表格中的数据格式需要先修正

当前至少有以下格式问题：

1. `98.3/99.8.3/100.0` 中的 `99.8.3` 明显是笔误；
2. 大多数结果保留一位小数，但 `2.35`、`48.44`、`50.24` 保留两位；
3. `F1/P/R` 这种斜杠结构难以阅读；
4. `zh en`、`zh` 应改成明确的 `Training Languages` 或 `Training Regime`；
5. `GLCLAP whisper zh en` 将 backbone 和模型名混在一起，其他模型却没有标注 backbone。

最终统一为一位小数即可，因为实验方差通常大于 0.01 个百分点。除非多次实验的标准差小于 0.01，否则两位小数会产生虚假的精确感。

---

# 十、适合写进论文的核心结论

整组结果应被压缩成下面这条逻辑链：

> TLDR 在 8 个训练—测试设置中的 7 个设置上取得最高 F1。其优势在充分训练且接近饱和的 AISHELL1-NE 上较小，但在 ContextASR-ZH、AISpeech-Meeting 以及中文训练下的英语测试中显著扩大。相较于 CLAR，TLDR 的平均 F1 增益从双语训练时的 2.8 个百分点扩大到中文训练时的 9.0 个百分点。这说明 token-level late interaction 的主要价值并非进一步改善简单样本上的粗粒度召回，而是在领域偏移、语言覆盖受限和局部声学证据较弱时，提高真实热词与困难负候选之间的可分性。

当前最值得补的两项实验是：**统一 backbone 的 controlled comparison**，以及 **PR curve + hardest-negative margin 分析**。前者决定增益能否归因于 TLDR 方法，后者决定论文能否从性能比较上升为机制解释。