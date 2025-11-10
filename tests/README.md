# QA平台测试模块

本目录包含QA教育平台的测试文件。

## 主要测试文件

### test_ai_features.py
**最全面的AI功能测试文件** - 推荐使用此文件进行所有AI相关功能测试

✨ 功能包括：
- AI问题生成测试（支持ARK API、OpenAI API、回退模式）
- 内容质量分析测试
- API错误处理测试
- 性能测试
- 问题质量检查
- 交互式测试功能

## 运行测试

```bash
# 运行AI功能测试
python tests/test_ai_features.py

# 运行根目录下的登录测试
python test_login.py
```

## 其他测试相关文件

根目录下还有以下测试相关文件：
- `test_login.py` - 登录功能测试
- `create_test_data.py` - 创建测试数据
- `clear_test_data.py` - 清除测试数据
- `generate_test_data.py` - 生成测试数据

## 环境要求

- Python 3.x
- Flask及相关依赖
- API密钥配置（可选）：
  - `ARK_API_KEY` - 字节跳动ARK API
  - `OPENAI_API_KEY` - OpenAI API
  - 注：未配置API密钥时将自动使用回退模式

## 已清理的冗余文件

以下测试文件已被删除，其功能已被 `test_ai_features.py` 覆盖：
- ❌ `test_app.py` - 基础Flask应用测试
- ❌ `quick_ai_test.py` - 快速AI测试
- ❌ `test_api_connection.py` - API连接测试
- ❌ `test_ark_api.py` - ARK API测试
- ❌ `test_ai.py`（根目录）- AI功能测试
