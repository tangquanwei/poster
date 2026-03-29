# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LaTeX conference poster for ICASSP 2026 titled "Mitigating Hallucination in Financial RAG via Fine-grained Knowledge Verification" (RLFKV). The poster presents research from Ant Group on reducing hallucinations in financial RAG systems using reinforcement learning with fine-grained knowledge verification.

## Building the Poster

The poster uses `pdflatex` to compile:

```bash
pdflatex document.tex
```

Or use your preferred LaTeX distribution (TeX Live, MiKTeX, etc.) with the `pdflatex` command.

Required packages (typically included in standard LaTeX distributions):
- `beamer` with `beamerposter` (A0 landscape poster format)
- `ctex` (Chinese language support)
- `tikz` with libraries: `shapes.geometric`, `arrows.meta`, `positioning`, `calc`
- `booktabs`, `amsmath`, `amssymb`, `graphicx`

## Project Structure

```
document.tex    - Single main file containing entire poster (no separate sections)
document.*      - Build outputs (.aux, .log, .nav, .out, .snm, .toc)
```

The poster is a single-file document with all content inline. It uses a 3-column `columns` environment with `block` environments for each section.
