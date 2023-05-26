import os
import openai
from tqdm import tqdm
import time

openai.api_key = os.getenv("OPENAI_KEY")

# 定义输入输出目录
input_directory = '../Original'
output_directory = '../English'

# 定义句子结束的标志
end_of_sentence = ['。', '！', '？']

# 定义搜索句子结束标志的范围
N = 50  # 你可以根据实际情况调整这个值

# 遍历文件夹
for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        # 读取文件
        with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as f:
            text = f.read()

        # 将文本分割成多个部分
        parts = []
        while text:
            if len(text) > 1024:
                pos = 1024
                start = max(0, pos - N)
                end = min(len(text), pos + N)
                while pos > start and text[pos] not in end_of_sentence:
                    pos -= 1
                if pos == start:
                    pos = 1024
                    while pos < end and text[pos] not in end_of_sentence:
                        pos += 1
                if pos < end:
                    parts.append(text[:pos+1])
                    text = text[pos+1:]
                else:
                    parts.append(text[:1024])
                    text = text[1024:]
            else:
                parts.append(text)
                text = ''

        # 打开输出文件
        with open(os.path.join(output_directory, filename), 'w', encoding='utf-8') as f:
            for part in tqdm(parts, desc=f"Translating {filename}", unit="part"):
                while True:
                    try:
                        # 使用OpenAI API翻译文本
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",  # 这里需要使用你想要的模型，如GPT-4
                            messages=[
                                {"role": "system", "content": "You are a translator."},
                                {"role": "user", "content": f"Translate this into English:\n\n{part}"}
                            ]
                        )
                        # 将请求的信息和翻译结果写入到文本文件中
                        f.write(f"Request:\n{part}\n")
                        f.write(f"Response:\n{response['choices'][0]['message']['content']}\n")
                        time.sleep(0.1)  # 在每个请求之间添加0.1秒的延迟
                        break
                    except openai.error.RateLimitError:
                        print("Rate limit exceeded, sleeping for a while...")
                        time.sleep(60)  # 等待60秒
                    except openai.error.OpenAIError as e:
                        print(f"An error occurred: {e}")
                        break
