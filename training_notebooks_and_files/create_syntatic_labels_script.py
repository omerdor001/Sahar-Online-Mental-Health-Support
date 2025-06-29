import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
import pandas as pd
import os
from huggingface_hub import login
token = "enter your token for LLAMA70B or something else"
login(token=token)

model_id = "meta-llama/Llama-3.3-70B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={
        "quantization_config": {
        "load_in_4bit": True,
        "llm_int8_enable_fp32_cpu_offload":True
        },
        "device_map": "cuda", #"device_map": "auto"
        "torch_dtype": torch.bfloat16
    },
)


# Load data
messages = pd.read_csv('trainDatasets/riskfree_messages_seeker_only.csv', low_memory=False)

# Output setup
output_path = "trainDatasets/riskfree_seeker_ONLY_syntasis_results.csv"
if os.path.exists(output_path):
    existing_df = pd.read_csv(output_path)
    start_index = len(existing_df)
    print(f"Resuming from index {start_index}")
else:
    existing_df = pd.DataFrame()
    start_index = 0

# Prompt builder
def build_prompt(text):
    return f"""<s>[INST] <<SYS>>
You are a helpful assistant that evaluates text for suicide risk factors and responds only with "Yes" or "No".
<</SYS>>
Does the following text show signs of any of the following risk factors?
Text: "{text}"
Risk factors to consider:
1. Suicidal intent (explicit or implicit mentions of wanting to die or end one's life)
2. Hopelessness or extreme despair (statements like "there's no way out" or "nothing will ever get better")
3. Social withdrawal or isolation (mentioning feeling alone, abandoned, or disconnected)
4. Self-harm or past suicidal behavior (references to cutting, previous attempts, or self-inflicted harm)
5. Giving away possessions or saying goodbye (indicating preparation for suicide)
6. Expressing a burden mentality ("Everyone would be better off without me")
7. Extreme guilt or self-hatred (statements like "I am worthless" or "I deserve to suffer")
8. Sudden calmness after distress (which might indicate a decision to act)
9. Lack of future-oriented thinking ("I won’t be here much longer" or "It doesn’t matter anymore")
10. Expressions of unbearable emotional pain ("I can’t take this anymore" or "The pain is too much")
Please respond only with a single word: Yes or No: [/INST] \n"""

# Batching setup
batch_size = 32
results = []

with torch.no_grad():
    drop_counter = 0
    for batch_start in range(start_index, len(messages), batch_size):
        drop_counter += 1
        batch_end = min(batch_start + batch_size, len(messages))
        batch = messages.iloc[batch_start:batch_end]

        prompts = [build_prompt(text) for text in batch['text']]

        outputs = pipe(
            prompts,
            max_new_tokens=1,
            do_sample=False,
            return_full_text=False
        )

        for i, output in enumerate(outputs):
            row = batch.iloc[i].to_dict()
            row["generated_text"] = output[0]["generated_text"]
            results.append(row)
        print(outputs)
        # Save every 1000 messages
        if drop_counter > 32:
            df = pd.DataFrame(results)
            if os.path.exists(output_path):
                df.to_csv(output_path, mode='a', header=False, index=False)
            else:
                df.to_csv(output_path, index=False)
            print(f"Saved {batch_end} messages")
            results = []
            drop_counter = 0

# Final save
if results:
    df = pd.DataFrame(results)
    if os.path.exists(output_path):
        df.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df.to_csv(output_path, index=False)
    print("Final batch saved.")