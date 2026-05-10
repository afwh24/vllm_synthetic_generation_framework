from openai import OpenAI
from config import max_tokens, base_url, model
import json
import requests
from bs4 import BeautifulSoup

#consist of simple helper functions for the main execution

#prompt model for response
def prompt_response(prompt):
    #get prompt response from LLM
    client = OpenAI(base_url=base_url, api_key="no-key-needed", timeout=300)


    resp = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        max_tokens= max_tokens
    )
    return resp.choices[0].message.content


#process the prompt response and return them as JSON output
def split_thinking_and_main_content(content, prompt = None):
    #split thinking content and main content
    if "<think>" in content and "</think>" in content: #Qwen3-32B model
        start_idx = content.find("<think>")
        end_idx = content.find("</think>")
        thinking_content = content[start_idx+len("<think>"): end_idx]
        non_thinking_content = content[end_idx+len("</think>"):]
        main_content = json.loads(non_thinking_content)

        return {
            "prompt": prompt.strip(),
            "thinking_content": thinking_content.strip(),
            "main_content": main_content
        }
    
    elif "</think>" in content: #Qwen3-235B model
        end_idx = content.find("</think>")
        thinking_content = content[:end_idx] 
        non_thinking_content = content[end_idx+len("</think>"):]
        main_content = json.loads(non_thinking_content)

        return {
            "prompt": prompt.strip(),
            "thinking_content": thinking_content.strip(),
            "main_content": main_content
        }
    
    return None



#log the data into jsonl file
def log_to_jsonl(filename, data):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


#parse HTML and return plain text
def extract_text_from_html(raw_html:str):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(strip=True)