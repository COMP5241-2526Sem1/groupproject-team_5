#!/usr/bin/env python3
"""
Render 部署快速检查脚本
检查项目是否准备好部署到 Render
"""

import os
import sys
from pathlib import Path

class DeploymentChecker:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def check(self, name, condition, message="", warning=False):
        """检查单个条件"""
        if condition:
            status = "✅" if not warning else "⚠️ "
            print(f"{status} {name}")
            if message:
                print(f"   {message}")
            self.passed += 1
            if warning:
                self.warnings += 1
        else:
            print(f"❌ {name}")
            if message:
                print(f"   {message}")
            self.failed += 1
        return condition
    
    def check_file_exists(self, filepath, description):
        """检查文件是否存在"""
        exists = Path(filepath).exists()
        self.check(
            f"{description}",
            exists,
            f"文件: {filepath}" if exists else f"缺少文件: {filepath}"
        )
        return exists
    
    def check_file_content(self, filepath, keyword, description):
        """检查文件是否包含特定内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                contains = keyword in content
                self.check(
                    description,
                    contains,
                    f"在 {filepath} 中找到" if contains else f"在 {filepath} 中未找到 '{keyword}'"
                )
                return contains
        except:
            self.check(description, False, f"无法读取文件: {filepath}")
            return False

def main():
    print("🚀 Render 部署准备检查")
    print("=" * 60)
    
    checker = DeploymentChecker()
    
    # 1. 检查必需文件
    print("\n📁 检查必需文件...")
    checker.check_file_exists("requirements.txt", "requirements.txt 存在")
    checker.check_file_exists("run.py", "run.py 存在")
    checker.check_file_exists("app/__init__.py", "app/__init__.py 存在")
    checker.check_file_exists(".gitignore", ".gitignore 存在")
    checker.check_file_exists(".env.example", ".env.example 存在")
    
    # 2. 检查 requirements.txt
    print("\n📦 检查 Python 依赖...")
    if Path("requirements.txt").exists():
        checker.check_file_content("requirements.txt", "gunicorn", "包含 gunicorn")
        checker.check_file_content("requirements.txt", "Flask", "包含 Flask")
        checker.check_file_content("requirements.txt", "PyMySQL", "包含 PyMySQL")
        checker.check_file_content("requirements.txt", "cryptography", "包含 cryptography (SSL支持)")
    
    # 3. 检查数据库配置
    print("\n🗄️  检查数据库配置...")
    if Path("app/__init__.py").exists():
        checker.check_file_content(
            "app/__init__.py", 
            "MYSQL_HOST", 
            "使用环境变量配置数据库"
        )
        checker.check_file_content(
            "app/__init__.py",
            "psdb.cloud",
            "支持 PlanetScale 连接"
        )
        checker.check_file_content(
            "app/__init__.py",
            "SQLALCHEMY_ENGINE_OPTIONS",
            "配置了连接池优化"
        )
    
    # 4. 检查 .gitignore
    print("\n🔒 检查安全配置...")
    if Path(".gitignore").exists():
        checker.check_file_content(".gitignore", ".env", ".env 文件被忽略")
        checker.check_file_content(".gitignore", "__pycache__", "__pycache__ 被忽略")
    
    # 5. 检查环境变量
    print("\n⚙️  检查环境变量...")
    has_env = Path(".env").exists()
    checker.check(
        ".env 文件存在",
        has_env,
        "本地开发环境变量已配置" if has_env else "需要创建 .env 文件（从 .env.example 复制）",
        warning=not has_env
    )
    
    # 6. 检查 Git 状态
    print("\n📝 检查 Git 状态...")
    if os.system("git rev-parse --git-dir > /dev/null 2>&1") == 0:
        checker.check(
            "Git 仓库已初始化",
            True,
            "项目在 Git 版本控制下"
        )
        
        # 检查是否在正确的分支
        branch = os.popen("git branch --show-current").read().strip()
        on_zmd = branch == "zmd"
        checker.check(
            f"当前分支: {branch}",
            on_zmd,
            "在 zmd 分支上" if on_zmd else f"建议切换到 zmd 分支: git checkout zmd",
            warning=not on_zmd
        )
        
        # 检查是否有未提交的更改
        status = os.popen("git status --porcelain").read().strip()
        no_changes = len(status) == 0
        checker.check(
            "工作区状态",
            no_changes,
            "没有未提交的更改" if no_changes else "有未提交的更改，建议先提交",
            warning=not no_changes
        )
    else:
        checker.check("Git 仓库", False, "不是 Git 仓库")
    
    # 7. 检查模型定义
    print("\n👤 检查用户模型...")
    if Path("app/models.py").exists():
        checker.check_file_content(
            "app/models.py",
            "unique=True",
            "User.email 字段有唯一约束"
        )
    
    # 8. 部署建议
    print("\n💡 部署建议...")
    print("   1. 确保已在 PlanetScale 创建数据库")
    print("   2. 确保已在 Render 创建 Web Service")
    print("   3. 在 Render 配置环境变量：")
    print("      - SECRET_KEY")
    print("      - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")
    print("      - FLASK_ENV=production")
    print("   4. 推送代码到 GitHub: git push origin zmd")
    print("   5. Render 会自动部署")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 检查总结")
    print("=" * 60)
    print(f"✅ 通过: {checker.passed}")
    print(f"❌ 失败: {checker.failed}")
    print(f"⚠️  警告: {checker.warnings}")
    
    if checker.failed == 0:
        print("\n🎉 太棒了！项目已准备好部署到 Render！")
        print("\n下一步：")
        print("1. 提交并推送代码: git push origin zmd")
        print("2. 在 Render 配置环境变量")
        print("3. 部署应用")
        print("\n详细步骤请查看: RENDER_DEPLOYMENT_GUIDE.md")
        return 0
    else:
        print(f"\n⚠️  有 {checker.failed} 个问题需要解决")
        print("请修复上述问题后再部署")
        return 1

if __name__ == "__main__":
    sys.exit(main())
