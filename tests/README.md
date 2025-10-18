# QA平台测试模块

这个目录包含QA教育平台的各种测试文件。

## 测试结构

- `test_ai_features.py` - AI功能测试
- `test_qa_routes.py` - QA路由测试  
- `test_models.py` - 数据模型测试
- `test_auth.py` - 认证功能测试

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_ai_features.py

# 运行AI功能测试
python tests/test_ai_features.py
```

## 环境要求

- pytest
- Flask-Testing
- API密钥配置（ARK_API_KEY 或 OPENAI_API_KEY）
