# my_main.py
from dotenv import load_dotenv
from my_llm import MyLLM  # note: import our own classes here

# load environment
load_dotenv()

# instantiate our rewritten client and specify the provider
llm = MyLLM(provider="ollama")

# prepare messages
messages = [{"role": "user", "content": "你好，请介绍一下你自己。"}]

# 发起调用，think等方法都已从父类继承，无需重写
response_stream = llm.think(messages)

# print response
print("Ollama Response:")
for chunk in response_stream:
    # chunk在my_llm库中已经打印过一遍，这里只需要pass即可
    # print(chunk, end="", flush=True)
    pass
