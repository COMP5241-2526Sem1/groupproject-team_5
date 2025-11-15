"""
测试从 worker 进程的角度发起 ARK API 请求
这个脚本模拟 Gunicorn worker 的环境
"""
import os
import sys

print("=" * 60)
print("环境变量检查")
print("=" * 60)
print(f"no_proxy: {os.environ.get('no_proxy', 'NOT SET')}")
print(f"NO_PROXY: {os.environ.get('NO_PROXY', 'NOT SET')}")
print(f"ARK_API_KEY: {os.environ.get('ARK_API_KEY', 'NOT SET')[:20]}...")
print()

# 测试 1: 使用 requests 库
print("=" * 60)
print("测试 1: 使用 requests 直接连接")
print("=" * 60)
try:
    import requests
    response = requests.get('https://ark.cn-beijing.volces.com', timeout=10)
    print(f"✅ requests 连接成功: Status {response.status_code}")
except Exception as e:
    print(f"❌ requests 连接失败: {type(e).__name__}: {e}")
print()

# 测试 2: 使用 ARK SDK
print("=" * 60)
print("测试 2: 使用 ARK SDK 调用 API")
print("=" * 60)
try:
    from volcenginesdkarkruntime import Ark
    
    ark_api_key = os.environ.get('ARK_API_KEY')
    if not ark_api_key:
        print("❌ ARK_API_KEY 未设置")
    else:
        client = Ark(
            api_key=ark_api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            timeout=30
        )
        
        response = client.chat.completions.create(
            model="ep-20250115221628-jffrr",  # doubao-1-5-pro-32k-250115
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'test success' if you can read this."}
            ],
            max_tokens=50
        )
        
        print(f"✅ ARK SDK 调用成功!")
        print(f"Response: {response.choices[0].message.content}")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("提示: 可能需要安装 volcenginesdkarkruntime")
except Exception as e:
    print(f"❌ ARK SDK 调用失败: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
print()

# 测试 3: 检查 urllib3 的代理配置
print("=" * 60)
print("测试 3: 检查 urllib3 代理配置")
print("=" * 60)
try:
    import urllib3
    from urllib3.util.ssl_ import create_urllib3_context
    
    # 检查是否有代理管理器
    print(f"urllib3 version: {urllib3.__version__}")
    
    # 尝试禁用代理警告
    urllib3.disable_warnings()
    
    # 创建一个 PoolManager 并测试
    http = urllib3.PoolManager()
    response = http.request('GET', 'https://ark.cn-beijing.volces.com', timeout=10)
    print(f"✅ urllib3 连接成功: Status {response.status}")
except Exception as e:
    print(f"❌ urllib3 测试失败: {type(e).__name__}: {e}")
print()

# 测试 4: 检查 DNS 解析
print("=" * 60)
print("测试 4: DNS 解析检查")
print("=" * 60)
try:
    import socket
    hostname = 'ark.cn-beijing.volces.com'
    ip = socket.gethostbyname(hostname)
    print(f"✅ DNS 解析成功: {hostname} -> {ip}")
    
    # 测试直接 IP 连接
    try:
        import requests
        response = requests.get(f'https://{ip}', 
                               headers={'Host': hostname},
                               timeout=10,
                               verify=False)  # 跳过 SSL 验证
        print(f"✅ 直接 IP 连接成功: Status {response.status_code}")
    except Exception as e:
        print(f"⚠️ 直接 IP 连接失败: {type(e).__name__}: {e}")
except Exception as e:
    print(f"❌ DNS 解析失败: {type(e).__name__}: {e}")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
