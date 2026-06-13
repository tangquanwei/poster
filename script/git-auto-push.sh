#!/bin/bash

# Git 自动推送脚本
# 用法: ./git-auto-push.sh [commit message] [branch name]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取参数
COMMIT_MSG="${1:-Auto commit at $(date '+%Y-%m-%d %H:%M:%S')}"
BRANCH="${2:-$(git rev-parse --abbrev-ref HEAD)}"

echo -e "${BLUE}========== Git 自动推送脚本 ==========${NC}"

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 错误: 当前目录不是 git 仓库${NC}"
    exit 1
fi

# 检查是否有未暂存的变更
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  检测到未暂存的更改${NC}"
    git add -A
    echo -e "${GREEN}✓ 已暂存所有更改${NC}"
else
    echo -e "${YELLOW}ℹ️  检查文件状态...${NC}"
    # 检查未追踪的文件
    UNTRACKED=$(git ls-files --others --exclude-standard)
    if [ -z "$UNTRACKED" ]; then
        echo -e "${YELLOW}ℹ️  没有新的变更需要推送${NC}"
        exit 0
    fi
    git add -A
    echo -e "${GREEN}✓ 已暂存新文件${NC}"
fi

# 显示将要提交的内容
echo -e "${BLUE}--- 待提交内容 ---${NC}"
git diff --cached --stat

# 提交变更
echo -e "${BLUE}提交信息: ${YELLOW}${COMMIT_MSG}${NC}"
git commit -m "$COMMIT_MSG" || {
    echo -e "${RED}❌ 提交失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ 已提交${NC}"

# 推送到远程仓库
echo -e "${BLUE}推送到分支: ${YELLOW}${BRANCH}${NC}"
git push origin "$BRANCH" || {
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ 已推送${NC}"

echo -e "${BLUE}========== 完成 ==========${NC}"
echo -e "${GREEN}✅ Git 自动推送成功!${NC}"
