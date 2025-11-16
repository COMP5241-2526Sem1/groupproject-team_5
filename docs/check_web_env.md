# 在 Render Shell 中运行以下命令来诊断

## 1. 检查 Gunicorn 进程的环境变量

```bash
# 找到 Gunicorn 主进程
ps aux | grep gunicorn | grep -v grep

# 如果找到了进程，记下 PID，然后：
# 假设 PID 是 123，运行：
cat /proc/123/environ | tr '\0' '\n' | grep -i proxy
```

## 2. 从 Web 应用内部检查环境变量

在 Render Shell 中运行：

```bash
python3 << 'PYTHON'
import os
import sys
sys.path.insert(0, '/opt/render/project/src')

print("=== 环境变量检查 ===")
print(f"no_proxy: {os.environ.get('no_proxy', 'NOT SET')}")
print(f"NO_PROXY: {os.environ.get('NO_PROXY', 'NOT SET')}")
print(f"http_proxy: {os.environ.get('http_proxy', 'NOT SET')}")
print(f"https_proxy: {os.environ.get('https_proxy', 'NOT SET')}")
print(f"ARK_API_KEY: {os.environ.get('ARK_API_KEY', 'NOT SET')[:20]}...")
print(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')[:20]}...")
PYTHON
```

## 3. 测试实际 HTTP 请求

```bash
python3 << 'PYTHON'
import os
import requests

# 设置 no_proxy (就像你手动做的那样)
os.environ['no_proxy'] = 'ark.cn-beijing.volces.com,101.126.75.46,*.volces.com'
os.environ['NO_PROXY'] = 'ark.cn-beijing.volces.com,101.126.75.46,*.volces.com'

try:
    response = requests.get('https://ark.cn-beijing.volces.com', timeout=10)
    print(f"✅ 连接成功: Status {response.status_code}")
except Exception as e:
    print(f"❌ 连接失败: {e}")
PYTHON
```

## 4. 模拟 Web 请求（测试 AI 生成）

```bash
curl -X POST https://qa-platform-zmd.onrender.com/activities/generate_questions \
  -H "Content-Type: application/json" \
  -H "Cookie: session=你的session值" \
  -d '{"text": "Test AI generation from curl"}' \
  -v
```

运行这些命令并把输出发给我！
