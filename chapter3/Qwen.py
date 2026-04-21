import ollama

# 指定 ollama 模型的名称
model_name = "qwen3.5:4b"

print(f"准备调用本地 Ollama 模型：{model_name}...")

# 准备对话输入
messages = [
    {"role": "system", "content": "You are a helpful assisant."},
    {"role": "user", "content": "你好，请介绍你自己。"},
]

try:
    # 调用 Ollama 模型生成回答
    response = ollama.chat(model=model_name, messages=messages)

    # 提取并打印模型的回答
    print("\n模型的回答：")
    print(response["message"]["content"])
except Exception as e:
    print(f"\n调用失败，请确保 Ollama 服务正在后台运行，且已下载该模型。错误信息: {e}")
