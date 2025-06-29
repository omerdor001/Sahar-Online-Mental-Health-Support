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
messages = pd.read_csv("trainDatasets/combined_ONLY_riskfull_messages_syntatic.csv", low_memory=False)

# Output setup
output_path = "trainDatasets/data_augmentation_results.csv"
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
You are a helpful and safety-aware assistant helping augment Hebrew text data for suicide risk detection. Your task is to generate realistic rephrasings of highly suicidal-risk Hebrew messages.

Guidelines:
- Preserve the core **meaning** and **emotional tone** of the original message.
- Keep the **suicidal intent** explicit or clearly implied.
- Rephrase the sentence naturally in **spoken or written Hebrew**.
- Avoid simple synonym replacement—diversify **structure**, **style**, and **wording**.
- The original sentence is highly suicidal. The rephrased outputs must reflect the same level of risk.
- Do not censor or soften the sentiment.
- Return only a tuple of 3 sentences in this format:
("sentence1", "sentence2", "sentence3")
<</SYS>>
Rephrase the following sentence into 3 different versions while preserving its highly suicidal nature:
Sentence: "{text}"
[/INST]
"""

# Batching setup
batch_size = 8
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
            max_new_tokens=512,
            do_sample=True,
            return_full_text=False
        )

        for i, output in enumerate(outputs):
            row = batch.iloc[i].to_dict()
            row["generated_text"] = output[0]["generated_text"]
            results.append(row)
        print(outputs)
        # Save every 64 messages
        if drop_counter > 7:
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