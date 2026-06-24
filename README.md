# Poster

LaTeX poster, slide, paper, and CV workspace. This repository keeps conference poster sources, related figures, compiled PDFs, and a few helper scripts in one place.

## Directory Layout

| Path | Description |
| --- | --- |
| `ACL26/ACL26_AudioRAG/` | ACL 2026 AudioRAG materials, including A0 poster, slides, short paper, figures, and speech notes. |
| `ICASSP26_RLFKV/` | ICASSP 2026 RLFKV poster source and assets. |
| `ICASSP26_SIM/` | ICASSP 2026 SIM poster source and assets. |
| `ICASSP26_TS/` | ICASSP 2026 TS poster source and assets. |
| `CV_Job/` | LaTeX CV based on `altacv`. |
| `script/` | Git auto-commit and push helpers for Windows and Unix-like shells. |
| `tmp/` | Temporary working files. This directory is ignored by Git. |

## Requirements

- A LaTeX distribution such as TeX Live or MiKTeX.
- `latexmk` and `xelatex`.
- Common LaTeX packages used by the templates, including `tikzposter`, `beamerposter`, `fontspec`, `xeCJK`, `tcolorbox`, `qrcode`, `booktabs`, and `tikz`.
- Optional fonts used by some sources, such as Roboto, Source Sans Pro, Helvetica Neue, or Arial. The ACL poster falls back to TeX Gyre Heros when preferred sans fonts are unavailable.

## Build

Use XeLaTeX by default because several files use `fontspec` or Chinese font support.

### ACL AudioRAG

```powershell
cd ACL26\ACL26_AudioRAG
latexmk -xelatex -interaction=nonstopmode -file-line-error poster_acl_a0.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error slides.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error short_paper.tex
```

### ICASSP Posters

```powershell
cd ICASSP26_RLFKV
latexmk -xelatex -interaction=nonstopmode -file-line-error document.tex

cd ..\ICASSP26_SIM
latexmk -xelatex -interaction=nonstopmode -file-line-error document.tex

cd ..\ICASSP26_TS
latexmk -xelatex -interaction=nonstopmode -file-line-error document.tex
```

### CV

```powershell
cd CV_Job
latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex
```

## Clean Build Files

`latexmk` can remove generated auxiliary files:

```powershell
latexmk -c
```

Run it inside the specific project directory you want to clean. Generated LaTeX auxiliary files are also covered by `.gitignore`.

## Git Helper Scripts

Windows:

```powershell
.\script\git-auto-push.bat "update poster files"
```

PowerShell directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\script\git-auto-push.ps1 -Message "update poster files"
```

Unix-like shell:

```bash
./script/git-auto-push.sh "update poster files"
```

The helper scripts stage all changes, create a commit, and push to the current branch unless a branch name is provided.

## Notes

- Keep large temporary exports, archives, and scratch assets under `tmp/` when they do not need version control.
- Prefer editing the source `.tex` files and rebuilding the corresponding PDF in the same directory.
- Before pushing, check the working tree with `git status --short` to avoid committing unrelated generated files.
