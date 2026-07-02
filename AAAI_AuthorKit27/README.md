# AAAI Author Kit 常用命令

本文档记录当前项目维护 `aaai2027.tex` 时常用的 PowerShell 命令。LaTeX Workshop 已配置为把编译产物输出到 `build/`，不要再把 `.aux`、`.log`、`.fls` 等中间文件写到项目根目录。

## VS Code

推荐插件：

```text
james-yu.latex-workshop
```

项目级配置：

```text
.vscode/settings.json
```

当前默认行为：

- 保存 `.tex` 时自动编译。
- 默认 recipe 为 `pdfLaTeX only`，不会在没有引用时运行 BibTeX。
- 编译输出目录为 `build/`。
- PDF 预览使用 VS Code tab。
- SyncTeX 已关闭，减少 Windows 下文件占用问题。

## TeXstudio

`aaai2027.tex` 顶部已经加入 TeXstudio 可识别的 magic comments：

```tex
% !TeX root = aaai2027.tex
% !TeX encoding = UTF-8
% !TeX program = pdflatex
% !BIB program = bibtex
```

在 TeXstudio 中打开 `aaai2027.tex` 后，建议按下面方式配置当前论文的编译命令。

1. 打开 `Options > Configure TeXstudio > Commands`。
2. 将 `PdfLaTeX` 设置为：

```text
pdflatex -synctex=0 -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build %.tex
```

3. 本项目有引用时，在终端或 TeXstudio 的自定义命令中运行 BibTeX：

```text
bibtex build/aaai2027
```

4. 回到 TeXstudio 连续运行两次 `PdfLaTeX`，得到最终 PDF：

```text
build\aaai2027.pdf
```

如果 TeXstudio 提示找不到 `pdflatex` 或 `bibtex`，把 TeX Live 路径加入 Windows `PATH`，当前机器上的路径是：

```text
D:\texlive\2026\bin\windows
```

## 编译论文

创建输出目录：

```powershell
New-Item -ItemType Directory -Force build | Out-Null
```

默认快速编译，所有中间结果和 PDF 都进入 `build/`：

```powershell
pdflatex -synctex=0 -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build aaai2027.tex
```

使用 latexmk 编译，但不运行 BibTeX：

```powershell
latexmk -synctex=0 -interaction=nonstopmode -file-line-error -pdf -bibtex- -outdir=build aaai2027.tex
```

正文已有 `\cite{...}` 后，再使用完整 BibTeX 流程：

```powershell
pdflatex -synctex=0 -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build aaai2027.tex
bibtex build/aaai2027
pdflatex -synctex=0 -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build aaai2027.tex
pdflatex -synctex=0 -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build aaai2027.tex
```

输出 PDF：

```text
build\aaai2027.pdf
```

## 检查日志

查看 LaTeX error：

```powershell
rg -n "^!|Emergency stop|Fatal error" build\aaai2027.log
```

查看 overfull / underfull：

```powershell
rg -n "Overfull|Underfull" build\aaai2027.log
```

查看未定义引用、交叉引用或 citation：

```powershell
rg -n "undefined|Undefined|Citation|Reference|Rerun" build\aaai2027.log
```

没有正文引用时，BibTeX 的 `I found no \citation commands` 不是 LaTeX 错误。当前默认 recipe 不运行 BibTeX，等正文加入 `\cite{...}` 后再手动选择完整 BibTeX recipe。

## 搜索论文内容

查看章节结构：

```powershell
rg -n "\\section|\\subsection|\\subsubsection" aaai2027.tex
```

搜索方法相关内容：

```powershell
rg -n "CLAR|CIF|MaxSim|hotword|global|local|Inference|Training" aaai2027.tex
```

搜索待办或占位内容：

```powershell
rg -n "TODO|FIXME|placeholder|AAAI Press|Anonymous Submission" aaai2027.tex
```

## 提交前格式自查

检查 AAAI 禁用包：

```powershell
rg -n "\\usepackage.*(authblk|balance|CJK|float|flushend|fullpage|geometry|hyperref|navigator|setspace|titlesec|ulem|wrapfig|pgfplots)" aaai2027.tex
```

检查 AAAI 禁用命令：

```powershell
rg -n "\\(nocopyright|addtolength|balance|baselinestretch|clearpage|columnsep|newpage|pagebreak|pagestyle|tiny|vspace\\{-|vskip\\{-)" aaai2027.tex
```

检查图片裁剪参数：

```powershell
rg -n "includegraphics.*(trim|clip|viewport)" aaai2027.tex
```

检查当前检查清单：

```powershell
notepad z2027_checklist.md
```

## 文件与 Git 状态

查看目录文件：

```powershell
Get-ChildItem -Force
```

查看修改状态：

```powershell
git status --short
```

查看论文源码 diff：

```powershell
git diff -- aaai2027.tex
```

检查 diff 中的空白问题：

```powershell
git diff --check -- aaai2027.tex README.md .vscode/settings.json .gitignore
```

## 清理编译产物

清理 `build/` 中的编译产物：

```powershell
Remove-Item -Recurse -Force build
```

重新创建空的 `build/`：

```powershell
New-Item -ItemType Directory -Force build | Out-Null
```

清理根目录中遗留的旧 LaTeX 中间文件：

```powershell
Remove-Item -ErrorAction SilentlyContinue aaai2027.aux, aaai2027.bbl, aaai2027.blg, aaai2027.fdb_latexmk, aaai2027.fls, aaai2027.log, aaai2027.out, aaai2027.synctex.gz, aaai2027.toc
```

## 常用路径

论文源码：

```text
D:\workspaceFolder\poster\AAAI_AuthorKit27\aaai2027.tex
```

编译输出：

```text
D:\workspaceFolder\poster\AAAI_AuthorKit27\build
```

CLAR 方法笔记：

```text
D:\workspaceFolder\2ndBrain\notes\projects\ASR+RAG2026\CLAR 方法.md
```

检查清单：

```text
D:\workspaceFolder\poster\AAAI_AuthorKit27\z2027_checklist.md
```
