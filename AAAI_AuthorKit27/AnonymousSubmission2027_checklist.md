# AnonymousSubmission2027.tex 检查清单

来源文件：`AnonymousSubmission2027.tex`  
适用目标：AAAI 2027 匿名投稿 / camera-ready 前的 LaTeX 与 PDF 自查

## 当前文件初检

- [x] 使用 `\documentclass[letterpaper]{article}`。
- [x] 使用 `\usepackage[submission]{aaai2027}`，当前为匿名投稿模式。
- [x] 保留 `\pdfinfo{ /TemplateVersion (2027.1) }`。
- [x] 使用 `\frenchspacing`。
- [x] 使用 `\bibliography{aaai2027}`。
- [ ] 当前标题仍是 AAAI 模板标题，应替换为论文真实标题。
- [ ] 当前作者信息仍包含 AAAI Press Staff 示例内容；匿名投稿应改为 `Anonymous Submission` 并清空 affiliations。
- [ ] 当前正文仍是 AAAI 作者说明模板，应替换为论文正文。
- [ ] `ReproducibilityChecklist.tex` 当前未被包含；按会议要求确认是否需要提交或取消注释。
- [ ] 提交前清理 PDF 元数据，避免泄露作者身份。

## 匿名投稿

- [ ] 作者姓名、单位、邮箱、资助信息、致谢等身份信息已移除或匿名化。
- [ ] 自引文不会让审稿人明显推断作者身份；必要时使用匿名表述。
- [ ] 代码、数据集、扩展版本链接不会去匿名化。
- [ ] PDF 元数据已清除，包括 Author、Title、Creator、Producer 中的敏感信息。
- [ ] 不包含 camera-ready 阶段才需要的版权声明或版权转让材料。
- [ ] 已确认会议是否要求可复现性检查清单、补充材料或技术附录。

## 必需文件

- [ ] 主 PDF 文件可打开、页数正确、内容完整。
- [ ] LaTeX 源码是单一 `.tex` 文件；正文不使用 `\input` 拆分章节。
- [ ] `.bib` 文件已随源文件提交。
- [ ] 只包含编译论文实际需要的图像文件。
- [ ] 包含必要的 LaTeX 生成文件，例如 `.aux`、`.bbl`、PDF 等，按会议提交说明执行。
- [ ] 不提交未使用图像、旧版本草稿、无关 `.tex` 文件、说明模板或临时文件。
- [ ] 源文件可在标准 TeX Live 2020 环境下编译。
- [ ] 最终源文件归档为 `.zip`，且大小不超过会议要求限制。
- [ ] 源文件命名符合提交说明；camera-ready 通常要求以第一作者姓氏命名。

## LaTeX Preamble

- [ ] 保留 `aaai2027.sty` 和 `aaai2027.bst`，没有修改样式文件。
- [ ] 保留并正确使用 `url`、`graphicx`、`natbib`、`caption`。
- [ ] 没有额外加载字体包，例如 `times`、`helvet`、`courier`、`lmodern`。
- [ ] 没有加载会嵌入链接或书签的包，例如 `hyperref`、`navigator`、`pdfcomment`。
- [ ] 没有加载会修改页面布局、标题、间距或引用格式的包。
- [ ] 自定义宏不会修改 margin、spacing、font size、caption、float 或 bibliography 样式。
- [ ] `\setcounter{secnumdepth}` 只使用 0、1 或 2；短 poster / extended abstract 不使用章节编号。

## 禁用命令

- [ ] 未使用 `\addtolength`、`\baselinestretch`、`\linespread`。
- [ ] 未使用 `\clearpage`、`\newpage`、`\pagebreak` 或其他强制分页命令。
- [ ] 未使用 `\pagestyle`，PDF 中没有页码、页眉或页脚。
- [ ] 未使用 `\tiny`。
- [ ] 未使用 `\columnsep`、`\topmargin`、`\textheight` 等页面布局修改命令。
- [ ] 未在 caption、figure、table、section、subsection、reference 附近使用负 `\vspace` 或负 `\vskip`。
- [ ] 未在 `\includegraphics` 中使用 `trim`、`clip`、`viewport` 等伪裁剪方式。
- [ ] 未使用 `\nocopyright`。
- [ ] 如使用 `\setlength{\tabcolsep}{...}`，仅用于压缩表格列间距这一允许例外。

## 禁用或高风险包

- [ ] 未使用 `authblk`、`balance`、`CJK`、`float`、`flushend`。
- [ ] 未使用 `fullpage`、`geometry`、`layout`、`multicol`。
- [ ] 未使用 `titlesec`、`tocbibind`、`ulem`、`savetrees`、`setspace`。
- [ ] 未使用 `pgfplots`、`pstricks`、`epsfig`、`epsf`、`psfig`。
- [ ] 未使用 `babel`、`t1enc`、`euler` 等可能冲突的字体或语言包。
- [ ] 如果需要算法或代码块，确认所用包与 AAAI 样式兼容。

## 页面与版式

- [ ] PDF 是 US Letter 纸张，不是 A4。
- [ ] 正文为 AAAI 双栏格式。
- [ ] 首页面距、后续页面距和两栏 gutter 未被手动修改。
- [ ] 所有页面内容都在 margin 和 gutter 内，没有溢出。
- [ ] 页面数量符合会议限制。
- [ ] PDF 文件大小符合会议限制。
- [ ] PDF 版本为 1.5 或更高。
- [ ] PDF 不加密、不设密码。
- [ ] PDF 不包含书签、内部链接或嵌入超链接。

## 字体与正文

- [ ] 正文使用 AAAI 样式自动提供的 Times-like serif 字体。
- [ ] 正文字号为 10pt，行距为 12pt。
- [ ] 没有通过命令缩小正文字号或行距。
- [ ] 正文文本为黑色；颜色只用于图中或极少量必要细节。
- [ ] PDF 中所有字体已嵌入。
- [ ] PDF 和图中的字体均不是 Type 3。
- [ ] 非 Roman 字符未作为正文依赖字体出现；如必须出现，限制在位图图像中。

## 标题、作者与摘要

- [ ] 标题为 Title Case，不是 sentence case。
- [ ] 标题居中、跨双栏、格式由样式文件控制。
- [ ] 匿名投稿阶段作者为 `Anonymous Submission`，affiliations 为空。
- [ ] camera-ready 阶段作者、单位、邮箱、共同贡献和通讯作者标记格式正确。
- [ ] 摘要使用 `abstract` 环境。
- [ ] 摘要中不包含引用。
- [ ] 摘要后如使用 `links` 环境，位置在 abstract 与正文之间，且不破坏匿名性。

## 章节结构

- [ ] 主体章节顺序合理，标题不过度细碎。
- [ ] 可选 content appendices 位于主文之后，并计入页数限制。
- [ ] 可选 `Ethical Statement` 使用未编号章节。
- [ ] 可选 `Acknowledgments` 位于 references 前，匿名投稿阶段通常不出现。
- [ ] `References` 位于论文末尾，不在 references 后再放正文图表。
- [ ] Supplementary Material / Technical Appendices 的位置和提交方式符合会议说明。

## 图像与图表

- [ ] 所有图像均为 `.jpg`、`.png` 或 `.pdf`。
- [ ] 未使用 `.gif`、`.ps`、`.eps` 图像。
- [ ] EPS/PostScript 图已在 LaTeX 外部转换为 PDF。
- [ ] 图像已在外部工具中裁剪和调整尺寸，没有依赖 LaTeX 的 `trim` 或 `clip`。
- [ ] 图像分辨率足够，照片和位图至少约 300 dpi。
- [ ] 图中的文字至少 9pt，线宽至少 0.5pt。
- [ ] 图中字体已嵌入。
- [ ] 图注位于图下方，10pt roman，不加粗、不缩小。
- [ ] 图按首次提及位置附近放置，没有集中放到文末。
- [ ] 图不会越过页边距或栏间距。
- [ ] 使用颜色的图在灰度下仍可理解。
- [ ] 颜色对比度满足 WCAG 2.0 4.5:1 要求。
- [ ] 图表不只依赖颜色区分类别。
- [ ] 未使用 `minipage` 组合图。

## 表格

- [ ] 表格正文为 10pt roman；必要时最多降至 9pt。
- [ ] 未使用 `\resizebox` 或类似方式整体缩放表格。
- [ ] 过宽表格改为双栏表格或拆分为多个表格。
- [ ] 表格没有侵入 margin 或 gutter。
- [ ] 表注位于表格下方，10pt roman，不加粗、不缩小。
- [ ] 数字精度、列标题和换行经过压缩优化，而不是用格式 hack 挤压。

## 算法与代码块

- [ ] 算法作为浮动体放置，优先位于页面顶部或底部。
- [ ] 算法 caption 位于 header 区域并符合 AAAI 示例样式。
- [ ] 算法主体和结束线格式正确。
- [ ] listing 作为浮动体放置，caption 位于 header 区域。
- [ ] listing 不使用背景色。
- [ ] listing 行号如存在，完全位于正文栏内。

## 引用与参考文献

- [ ] 使用 `natbib` / AAAI 支持的引用命令。
- [ ] 引用格式为作者-年份格式。
- [ ] 四名及以上作者正文引用使用 first author + et al.。
- [ ] 文末使用 `\bibliography{...}`，不手动指定 `\bibliographystyle`。
- [ ] 使用 `aaai2027.bst` 生成参考文献。
- [ ] `.bib` 条目类型正确，例如 `@article`、`@inproceedings`、`@book`、`@misc`。
- [ ] arXiv 文献包含 `eprint` 与 `archivePrefix`。
- [ ] 网页资源包含 URL 和访问日期。
- [ ] 参考文献字段完整，没有缺作者、年份、题名、出版信息等关键字段。
- [ ] 参考文献字体不小于 9pt；仅在超页数时才考虑使用 `\small`。

## 编译与日志

- [ ] 使用 PDFLaTeX 工作流编译。
- [ ] 编译无 error。
- [ ] 编译日志无 unresolved references。
- [ ] 编译日志无 undefined citations。
- [ ] 编译日志无 overfull boxes；尤其检查公式、表格、图像和长 URL。
- [ ] 生成的 PDF 与提交的 `.tex` 源文件内容一致。
- [ ] 在另一台标准 LaTeX 环境或干净目录中测试过重新编译。

## PDF 终检

- [ ] 逐页检查 PDF，图、表、公式、引用、脚注和页尾均显示正常。
- [ ] 所有图像清晰可读，没有裁剪错误或隐藏层问题。
- [ ] 没有内容进入页边距、栏间距或页面外。
- [ ] 没有页码、页眉、页脚。
- [ ] 没有 PDF 书签和嵌入链接。
- [ ] PDF Fonts 面板中所有字体均已嵌入，且无 Type 3。
- [ ] PDF 元数据已清理。
- [ ] PDF 不受密码保护。

## 可复现性与补充材料

- [ ] 已确认 AAAI/具体 track 是否要求 reproducibility checklist。
- [ ] 如需包含清单，取消注释并检查 `\input{ReproducibilityChecklist.tex}` 路径。
- [ ] 如清单单独提交，文件名和格式符合会议说明。
- [ ] 补充材料不泄露匿名身份。
- [ ] 补充材料的提交方式、页数、格式和公开策略符合会议说明。

## 提交前归档

- [ ] 删除未使用图像、旧 PDF、说明模板和临时文件。
- [ ] `.zip` 中包含所有且仅包含必要源文件。
- [ ] `.zip` 大小符合限制。
- [ ] PDF、`.tex`、`.bib`、图像文件版本一致。
- [ ] 文件名符合提交系统要求。
- [ ] 在最终归档目录中完成一次从源码到 PDF 的完整编译验证。
