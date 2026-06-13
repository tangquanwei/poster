param(
    [string]$Message,
    [string]$Branch
)

$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Text)
    Write-Host $Text -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Text)
    Write-Host $Text -ForegroundColor Green
}

function Write-Warn {
    param([string]$Text)
    Write-Host $Text -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Text)
    Write-Host $Text -ForegroundColor Red
}

try {
    Write-Info "========== Git Auto Push (Windows) =========="

    git rev-parse --git-dir *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Current directory is not a Git repository."
    }

    if ([string]::IsNullOrWhiteSpace($Message)) {
        $Message = "Auto commit at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }

    if ([string]::IsNullOrWhiteSpace($Branch)) {
        $Branch = (git branch --show-current).Trim()
    }

    if ([string]::IsNullOrWhiteSpace($Branch)) {
        throw "Cannot detect current branch. Please pass a branch name."
    }

    $status = git status --porcelain
    if ([string]::IsNullOrWhiteSpace(($status -join ""))) {
        Write-Warn "No changes to commit or push."
        exit 0
    }

    Write-Info "--- Working tree changes ---"
    git status --short

    git add -A
    if ($LASTEXITCODE -ne 0) {
        throw "git add failed."
    }
    Write-Ok "Staged all changes."

    $cached = git diff --cached --name-only
    if ([string]::IsNullOrWhiteSpace(($cached -join ""))) {
        Write-Warn "No staged changes after git add."
        exit 0
    }

    Write-Info "--- Commit stat ---"
    git diff --cached --stat

    Write-Info "Commit message: $Message"
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }
    Write-Ok "Committed changes."

    Write-Info "Pushing to origin/$Branch ..."
    git push origin $Branch
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed."
    }

    Write-Ok "Git auto push completed successfully."
    Write-Info "========== Done =========="
}
catch {
    Write-Fail "ERROR: $($_.Exception.Message)"
    exit 1
}
