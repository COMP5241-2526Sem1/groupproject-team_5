#!/bin/bash

# 🛡️ 保护新功能的Git合并脚本
# 专门为qa-platform新功能设计的安全合并工具

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🛡️  保护新功能的Git合并工具${NC}"
    echo "====================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_feature() {
    echo -e "${PURPLE}🔥 $1${NC}"
}

# 检查关键新功能文件
check_new_features() {
    print_info "检查你的新功能文件..."
    
    NEW_FEATURES=(
        "app/models.py:EmailCaptcha邮箱验证码模型"
        "app/models.py:Question问答模型" 
        "app/models.py:Answer回答模型"
        "app/models.py:AnswerVote投票模型"
        "app/routes/qa.py:QA分页功能"
        "app/routes/auth.py:邮箱验证码功能"
        "templates/qa/:QA模板文件"
    )
    
    echo ""
    print_feature "发现的新功能："
    for feature in "${NEW_FEATURES[@]}"; do
        file=$(echo "$feature" | cut -d: -f1)
        desc=$(echo "$feature" | cut -d: -f2)
        if [ -f "$file" ] || [ -d "$file" ]; then
            print_success "$desc - $file"
        else
            print_warning "$desc - $file (文件不存在)"
        fi
    done
    echo ""
}

# 创建功能保护备份
create_feature_backup() {
    print_info "创建新功能专用备份..."
    
    BACKUP_DIR="../qa-platform-features-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份关键新功能文件
    CRITICAL_FILES=(
        "app/models.py"
        "app/routes/qa.py" 
        "app/routes/auth.py"
        "app/forms.py"
        "templates/qa/"
        "migrations/"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [ -e "$file" ]; then
            cp -r "$file" "$BACKUP_DIR/"
            print_success "已备份: $file"
        fi
    done
    
    echo "$BACKUP_DIR" > .feature_backup_path
    print_success "新功能备份完成: $BACKUP_DIR"
    echo ""
}

# 分析模型差异
analyze_model_conflicts() {
    print_info "分析数据库模型潜在冲突..."
    echo ""
    
    if [ -f "app/models.py" ]; then
        print_info "你的新模型类："
        grep -n "^class.*Model" app/models.py || grep -n "^class.*:" app/models.py | head -10
        echo ""
        
        print_warning "合并时需要特别注意的模型："
        echo "📧 EmailCaptcha - 邮箱验证码功能"
        echo "❓ Question - 问答功能"
        echo "💬 Answer - 回答功能" 
        echo "🗳️  AnswerVote - 投票功能"
        echo ""
    fi
}

# 智能合并策略
smart_merge_strategy() {
    print_info "选择合并策略："
    echo ""
    echo "1) 🛡️  保护优先合并 (推荐) - 优先保留你的新功能"
    echo "2) 📝 手动解决冲突 - 逐个文件检查和解决"
    echo "3) 🔍 仅预览冲突 - 不执行合并，只查看潜在冲突"
    echo "4) 🚫 取消合并"
    echo ""
    
    read -p "请选择策略 (1-4): " strategy
    
    case $strategy in
        1)
            protection_first_merge
            ;;
        2)
            manual_conflict_resolution
            ;;
        3)
            preview_conflicts_only
            ;;
        4)
            print_info "合并已取消"
            exit 0
            ;;
        *)
            print_error "无效选择"
            smart_merge_strategy
            ;;
    esac
}

# 保护优先合并
protection_first_merge() {
    print_info "执行保护优先合并..."
    
    # 1. 获取远程信息
    echo ""
    read -p "请输入Git仓库URL: " REPO_URL
    read -p "请输入要合并的分支名: " TARGET_BRANCH
    
    # 2. 初始化git并添加远程
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit with new features"
    fi
    
    git remote add team "$REPO_URL" 2>/dev/null || git remote set-url team "$REPO_URL"
    git fetch team
    
    # 3. 创建合并分支
    MERGE_BRANCH="merge-with-feature-protection-$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$MERGE_BRANCH"
    
    # 4. 使用特殊策略合并
    print_info "尝试智能合并（优先保留新功能）..."
    
    if git merge "team/$TARGET_BRANCH" -X ours; then
        print_success "自动合并成功！新功能已保护"
        
        # 验证关键功能
        verify_features_after_merge
        
        echo ""
        print_success "🎉 合并完成！"
        echo "新分支: $MERGE_BRANCH"
        echo "✅ 你的新功能已得到保护"
        echo ""
        print_info "下一步："
        echo "1. 测试功能: python3 run.py"
        echo "2. 检查新功能是否正常"
        echo "3. 如果满意，推送到远程: git push origin $MERGE_BRANCH"
        
    else
        print_warning "发现复杂冲突，需要手动处理"
        handle_complex_conflicts
    fi
}

# 验证功能完整性
verify_features_after_merge() {
    print_info "验证新功能完整性..."
    
    # 检查关键文件
    CRITICAL_CHECKS=(
        "app/models.py:EmailCaptcha"
        "app/models.py:Question"
        "app/models.py:Answer"
        "app/routes/qa.py:course_qa_list"
        "app/routes/auth.py:send_captcha"
    )
    
    for check in "${CRITICAL_CHECKS[@]}"; do
        file=$(echo "$check" | cut -d: -f1)
        pattern=$(echo "$check" | cut -d: -f2)
        if grep -q "$pattern" "$file" 2>/dev/null; then
            print_success "$pattern 功能完整"
        else
            print_warning "$pattern 可能受到影响"
        fi
    done
}

# 处理复杂冲突
handle_complex_conflicts() {
    print_warning "发现复杂冲突需要处理"
    echo ""
    
    print_info "冲突文件列表:"
    git status --porcelain | grep "^UU\|^AA" | while read -r line; do
        file=$(echo "$line" | awk '{print $2}')
        echo "❌ $file"
    done
    
    echo ""
    print_info "推荐的冲突解决策略："
    echo ""
    echo "对于 app/models.py:"
    echo "  ✅ 保留你的 EmailCaptcha, Question, Answer 模型"
    echo "  ✅ 合并团队的其他模型改动"
    echo ""
    echo "对于 app/routes/:"
    echo "  ✅ 保留你的 qa.py 和验证码功能"
    echo "  ✅ 合并团队的其他路由改动"
    echo ""
    
    print_info "自动修复常见冲突..."
    auto_fix_common_conflicts
    
    echo ""
    print_info "手动解决步骤："
    echo "1. 编辑冲突文件，解决 <<<<<<< ======= >>>>>>> 标记"
    echo "2. 优先保留你的新功能代码"
    echo "3. 运行: git add <文件名>"
    echo "4. 运行: git commit"
    echo "5. 测试功能完整性"
    
    echo ""
    echo "需要帮助解决冲突吗？(y/n):"
    read -r HELP_RESOLVE
    if [ "$HELP_RESOLVE" = "y" ]; then
        interactive_conflict_helper
    fi
}

# 自动修复常见冲突
auto_fix_common_conflicts() {
    print_info "尝试自动修复常见冲突..."
    
    # 检查models.py冲突
    if git status --porcelain | grep -q "UU.*models.py"; then
        print_info "发现models.py冲突，尝试智能合并..."
        
        # 创建临时合并版本
        if grep -q "EmailCaptcha\|Question\|Answer" app/models.py; then
            print_success "检测到新功能模型完整"
        else
            print_warning "新功能模型可能丢失，从备份恢复..."
            BACKUP_PATH=$(cat .feature_backup_path)
            if [ -f "$BACKUP_PATH/app/models.py" ]; then
                # 智能合并模型文件
                python3 -c "
import re

# 读取备份的新功能模型
with open('$BACKUP_PATH/app/models.py', 'r') as f:
    backup_content = f.read()

# 读取当前冲突文件
with open('app/models.py', 'r') as f:
    current_content = f.read()

# 提取新功能模型
new_models = []
for model in ['EmailCaptcha', 'Question', 'Answer', 'AnswerVote']:
    pattern = rf'class {model}.*?(?=class|\Z)'
    match = re.search(pattern, backup_content, re.DOTALL)
    if match:
        new_models.append(match.group(0))

# 清理冲突标记
cleaned_content = re.sub(r'<<<<<<< HEAD.*?=======.*?>>>>>>> .*?\n', '', current_content, flags=re.DOTALL)

# 添加新功能模型
for model in new_models:
    if model.split('(')[0].split()[1] not in cleaned_content:
        cleaned_content += '\n' + model + '\n'

# 写入修复后的文件
with open('app/models.py', 'w') as f:
    f.write(cleaned_content)

print('模型文件已智能合并')
" && print_success "models.py 自动修复完成"
            fi
        fi
    fi
}

# 交互式冲突助手
interactive_conflict_helper() {
    print_info "交互式冲突解决助手"
    
    CONFLICT_FILES=$(git status --porcelain | grep "^UU\|^AA" | awk '{print $2}')
    
    for file in $CONFLICT_FILES; do
        echo ""
        print_info "处理冲突文件: $file"
        echo "选择操作:"
        echo "1) 查看冲突内容"
        echo "2) 保留你的版本 (推荐用于新功能文件)"
        echo "3) 保留团队版本"
        echo "4) 手动编辑"
        echo "5) 跳过这个文件"
        
        read -p "请选择 (1-5): " action
        
        case $action in
            1)
                echo "冲突内容预览:"
                git diff "$file" | head -20
                interactive_conflict_helper_file "$file"
                ;;
            2)
                git checkout --ours "$file"
                git add "$file"
                print_success "已保留你的版本: $file"
                ;;
            3)
                git checkout --theirs "$file" 
                git add "$file"
                print_success "已保留团队版本: $file"
                ;;
            4)
                echo "请手动编辑 $file，完成后按回车继续..."
                read
                git add "$file"
                ;;
            5)
                print_info "跳过 $file"
                ;;
        esac
    done
    
    echo ""
    print_info "冲突解决完成，提交更改..."
    git commit -m "Merge with feature protection: preserve EmailCaptcha, QA system, and pagination"
}

# 仅预览冲突
preview_conflicts_only() {
    print_info "预览模式 - 分析潜在冲突..."
    
    echo ""
    read -p "请输入Git仓库URL: " REPO_URL
    read -p "请输入要合并的分支名: " TARGET_BRANCH
    
    # 获取远程信息
    git remote add temp_preview "$REPO_URL" 2>/dev/null
    git fetch temp_preview
    
    print_info "分析文件差异..."
    
    # 检查关键文件的差异
    KEY_FILES=("app/models.py" "app/routes/qa.py" "app/routes/auth.py")
    
    for file in "${KEY_FILES[@]}"; do
        if git ls-tree temp_preview/"$TARGET_BRANCH" "$file" >/dev/null 2>&1; then
            echo ""
            print_info "文件 $file 的潜在冲突:"
            git diff HEAD temp_preview/"$TARGET_BRANCH" -- "$file" | head -20
            echo "..."
        else
            print_success "$file 是你的新文件，不会有冲突"
        fi
    done
    
    # 清理临时远程
    git remote remove temp_preview
    
    echo ""
    print_info "预览完成。这些是潜在的冲突区域。"
    print_info "建议使用'保护优先合并'策略来保护你的新功能。"
}

# 主函数
main() {
    clear
    print_header
    echo ""
    
    print_feature "检测到的新功能："
    echo "📧 邮箱验证码系统 (EmailCaptcha)"
    echo "❓ QA问答系统 (Question/Answer)"  
    echo "📄 分页功能 (pagination)"
    echo "🗳️  投票功能 (AnswerVote)"
    echo ""
    
    print_warning "这些新功能在Git合并时需要特别保护！"
    echo ""
    
    check_new_features
    create_feature_backup
    analyze_model_conflicts
    smart_merge_strategy
}

# 运行主函数
main
