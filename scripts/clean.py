#!/usr/bin/env python3
"""
清理和优化脚本
删除不必要的文件和目录
"""

import os
import shutil

def clean_project():
    """清理项目中不必要的文件"""
    
    base_dir = "/Users/dududu/Desktop/文件/python_code/Q&A platform demo"
    
    # 要删除的目录和文件
    items_to_remove = [
        # 缓存文件
        "__pycache__",
        ".pytest_cache",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        
        # IDE文件
        ".vscode",
        ".idea",
        
        # 临时文件
        "*.tmp",
        "*.log",
        
        # 旧的数据库文件
        "*.db",
        "instance/",
        
        # 测试文件
        "test_*.py",
    ]
    
    print("🧹 开始清理项目...")
    
    # 清理原始项目目录
    for root, dirs, files in os.walk(base_dir):
        # 跳过final_integrated_platform目录
        if "final_integrated_platform" in root:
            continue
            
        for item in items_to_remove:
            if item.startswith("*."):
                # 处理通配符文件
                ext = item[1:]
                for file in files:
                    if file.endswith(ext):
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            print(f"🗑️  删除文件: {file_path}")
                        except:
                            pass
            else:
                # 处理目录
                if item in dirs:
                    dir_path = os.path.join(root, item)
                    try:
                        shutil.rmtree(dir_path)
                        print(f"🗑️  删除目录: {dir_path}")
                    except:
                        pass
    
    print("✅ 项目清理完成!")

if __name__ == "__main__":
    clean_project()
