import os
import openai
from tqdm import tqdm
import time
import argparse
import sys

# List of supported languages
supported_languages = ['English', 'Spanish', 'French', 'German', 'Italian', 'Dutch', 'Russian', 'Chinese', 'Japanese', 'Korean']

# Create the parser
parser = argparse.ArgumentParser(description='Translate text files.')
parser.add_argument('--bilingual', action='store_true', help='Print both the original and translated text.')
parser.add_argument('--language', default='English', help=f"The target language for translation. Supported languages are: {', '.join(supported_languages)}")

# Parse the arguments
args = parser.parse_args()

# Check if the selected language is supported
if args.language not in supported_languages:
    print(f"Error: The language '{args.language}' is not supported.")
    sys.exit(1)

openai.api_key = os.getenv("OPENAI_KEY")

input_directory = '../Original'
output_directory = f'../{args.language}'

# If the output directory does not exist, create it
os.makedirs(output_directory, exist_ok=True)

end_of_sentence = ['。', '！', '？']

N = 50 

for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as f:
            text = f.read()

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

        with open(os.path.join(output_directory, filename), 'w', encoding='utf-8') as f:
            for part in tqdm(parts, desc=f"Translating {filename}", unit="part"):
                while True:
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": f"You are a translator."},
                                {"role": "user", "content": f"Translate this into {args.language}:\n\n{part}"}
                            ]
                        )
                        if args.bilingual:
                            f.write(f"{part}\n")
                        f.write(f"{response['choices'][0]['message']['content']}\n")
                        time.sleep(0.1)
                        break
                    except openai.error.RateLimitError:
                        print("Rate limit exceeded, sleeping for a while...")
                        time.sleep(60)
                    except openai.error.OpenAIError as e:
                        print(f"An error occurred: {e}")
                        break
