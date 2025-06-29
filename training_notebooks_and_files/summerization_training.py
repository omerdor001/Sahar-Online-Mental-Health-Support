#failed exprement at creating our own training for summerization algorithm, try to search for hebrew_summarizer
import torch
from transformers import T5Tokenizer, Seq2SeqTrainer as Trainer, Seq2SeqTrainingArguments as TrainingArguments
from transformers.models.longt5 import LongT5ForConditionalGeneration # Correct if you are using LongT5

# If biunlp/LongMt5-HeSum is actually based on standard T5/mT5, you might need:
# from transformers import MT5ForConditionalGeneration, T5ForConditionalGeneration
from datasets import load_dataset, DatasetDict
import numpy as np
import evaluate # Hugging Face Evaluate library
import nltk # For ROUGE aist_decode

# It's good practice to download nltk resources if you haven't
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

def check_alloc(message=""):
    if torch.cuda.is_available():
        print(f"--- Memory Stats {message} ---")
        print("Memory allocated:", round(torch.cuda.memory_allocated(0) / 1024**2, 2), "MB")
        # print("Max memory allocated:", round(torch.cuda.max_memory_allocated(0) / 1024**2, 2), "MB") # Can be reset
        print("Memory reserved:", round(torch.cuda.memory_reserved(0) / 1024**2, 2), "MB")
        # print("Max memory reserved:", round(torch.cuda.max_memory_reserved(0) / 1024**2, 2), "MB") # Can be reset
        print("--- End Memory Stats ---")
    else:
        print("CUDA not available, running on CPU.")

check_alloc("Initial")

# --- Configuration ---
MODEL_NAME = "biunlp/LongMt5-HeSum"
DATA_PATH = 'trainDatasets/summeries_cross.csv' # Make sure this path is correct
OUTPUT_DIR = "./longMt5_hebrew_summarization_finetuned"
LOGGING_DIR = "./logs_longMt5_he_sum"

# Tokenizer and Model Max Lengths
# For LongT5, input can be long. For mT5, it's usually 512 or 1024.
# Double-check the config of biunlp/LongMt5-HeSum if it's truly a LongT5 variant.
# If it's a standard mT5 fine-tuned, its max_length might be smaller.
# Let's assume it supports long inputs as per its name.
TOKENIZER_MODEL_MAX_LENGTH = 4096 # Default for LongT5, adjust if needed
MAX_INPUT_LENGTH = 1024 # Or 2048, 4096. Start smaller if OOM, increase if context is lost.
MAX_TARGET_LENGTH = 256  # Max length for generated summaries. 128 was okay too.

# Training Hyperparameters
LEARNING_RATE = 5e-5 # Lowered: 3e-4 might be too high for fine-tuning an already specialized model
PER_DEVICE_TRAIN_BATCH_SIZE = 1 # Keep this if 4096 input length, due to memory
PER_DEVICE_EVAL_BATCH_SIZE = 2   # Can be slightly larger for eval if memory allows
GRADIENT_ACCUMULATION_STEPS = 8 # Effective batch size = 1 * 8 = 8. Adjust as per your GPU memory.
NUM_TRAIN_EPOCHS = 3 # Start with 3, can increase if underfitting
WEIGHT_DECAY = 0.01
LOGGING_STEPS = 100 # Log more frequently
EVAL_STEPS = 500    # Evaluate more frequently
SAVE_STEPS = 500    # Save checkpoints more frequently
FP16 = torch.cuda.is_available() # Enable mixed precision if on GPU

# --- Load Model and Tokenizer ---
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = LongT5ForConditionalGeneration.from_pretrained(MODEL_NAME)
# If you suspect LongT5ForConditionalGeneration is wrong for "biunlp/LongMt5-HeSum",
# and it's actually based on google/mt5-*, you might try:
# from transformers import MT5ForConditionalGeneration
# model = MT5ForConditionalGeneration.from_pretrained(MODEL_NAME)
# tokenizer.model_max_length = TOKENIZER_MODEL_MAX_LENGTH # Set it on tokenizer

# Ensure the model is on the correct device (Trainer usually handles this, but good for clarity)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
check_alloc("After model load")

# --- Load and Prepare Dataset ---
# Load the full dataset
full_dataset = load_dataset('csv', data_files=DATA_PATH)['train']

# Handle potential NAs (IMPORTANT!)
full_dataset = full_dataset.filter(lambda example: example['conversation'] is not None and example['summary'] is not None)
print(f"Dataset size after NA filter: {len(full_dataset)}")

# Split dataset
# If your dataset is small (e.g. < 5k after filtering), consider a larger train set or cross-validation
if len(full_dataset) < 1000:
    print("Warning: Dataset is very small. Model might not train well.")
    # For very small datasets, might only do train and a tiny eval
    # Or use k-fold cross-validation (more complex with Trainer)

dataset_splits = full_dataset.train_test_split(test_size=0.1, seed=42)
# For more robustness, you might want a validation set too for hyperparameter tuning
# temp_train_val = dataset_splits['train'].train_test_split(test_size=0.1, seed=42) # 10% of original train for val
# train_dataset = temp_train_val['train']
# eval_dataset = temp_train_val['test'] # This is now validation
# test_dataset = dataset_splits['test'] # This is the final hold-out test set

train_dataset = dataset_splits['train']
eval_dataset = dataset_splits['test'] # Using test split as validation during training

print(f"Train dataset size: {len(train_dataset)}")
print(f"Eval dataset size: {len(eval_dataset)}")

# --- Preprocessing Function ---
# Add prefix for T5-style models
prefix = "summarize: "

def preprocess_function(examples):
    # The 'examples' will be a dictionary with keys 'conversation' and 'summary',
    # where each value is a list of strings (due to batched=True)
    inputs = [prefix + doc for doc in examples['conversation']]
    model_inputs = tokenizer(inputs, max_length=MAX_INPUT_LENGTH, truncation=True, padding="max_length")

    # Setup the tokenizer for targets
    # The labels should not be padded with pad_token_id, but with -100 so they are ignored in loss
    labels = tokenizer(text_target=examples['summary'], max_length=MAX_TARGET_LENGTH, truncation=True, padding="max_length")
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Apply preprocessing
# Use batched=True for speed!
# num_proc can be set if you have multiple cores and a large dataset
tokenized_train = train_dataset.map(preprocess_function, batched=True, remove_columns=train_dataset.column_names)
tokenized_eval = eval_dataset.map(preprocess_function, batched=True, remove_columns=eval_dataset.column_names)

check_alloc("After tokenization")

# --- Evaluation Metric (ROUGE) ---
rouge_metric = evaluate.load("rouge")

def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    # predictions are often (logits, seq_lengths) or similar. We need generated token IDs.
    # If predict_with_generate=True, predictions should be token IDs.
    # Decode generated summaries
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    # ROUGE expects a list of predictions and a list of lists of references
    # NLTK tokenization for ROUGE
    decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = [["\n".join(nltk.sent_tokenize(label.strip()))] for label in decoded_labels] # Each label wrapped in a list

    result = rouge_metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True, rouge_types=["rouge1", "rouge2", "rougeL"])
    
    # Extract ROUGE F1 scores
    result = {key: value * 100 for key, value in result.items()} # HF evaluate already gives fmeasure
    
    # Add mean generated length
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)
    
    return {k: round(v, 4) for k, v in result.items()}


# --- Training Arguments ---
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="steps",       # Evaluate during training
    eval_steps=EVAL_STEPS,             # How often to evaluate
    logging_dir=LOGGING_DIR,           # Directory for logs
    logging_strategy="steps",
    logging_steps=LOGGING_STEPS,
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS, # Crucial for small per_device_batch_size
    num_train_epochs=NUM_TRAIN_EPOCHS,
    weight_decay=WEIGHT_DECAY,
    save_strategy="steps",             # Save checkpoints during training
    save_steps=SAVE_STEPS,
    save_total_limit=2,                # Only keep the last 2 checkpoints + the best one
    predict_with_generate=True,        # IMPORTANT for seq2seq tasks
    fp16=FP16,                         # Use mixed precision if available
    load_best_model_at_end=True,       # Load the best model found during training at the end
    metric_for_best_model="rougeL",    # Use ROUGE-L to select the best model
    report_to="tensorboard",           # Or "wandb" if you use Weights & Biases
    generation_max_length=MAX_TARGET_LENGTH, # For evaluation generation
    generation_num_beams=4,            # Use beam search for better eval summaries
    # ddp_find_unused_parameters=False, # If using DDP and getting errors, might need this
)
check_alloc("Before Trainer init")

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics  # Enable metrics computation
)
check_alloc("After Trainer init, before train")

# --- Train the Model ---
print("Starting training...")
try:
    trainer.train()
    check_alloc("After training")
    # Save the best model
    trainer.save_model(f"{OUTPUT_DIR}/best_model")
    tokenizer.save_pretrained(f"{OUTPUT_DIR}/best_model")
    print("Training complete. Best model saved.")

except Exception as e:
    print(f"An error occurred during training: {e}")
    import traceback
    traceback.print_exc()
    check_alloc("After error in training")

torch.save(model.state_dict(), "summerization(3).pth")

# --- Example of Inference (after training) ---
def summarize_text(text, trained_model, trained_tokenizer):
    trained_model.eval() # Set model to evaluation mode
    inputs = trained_tokenizer(prefix + text, return_tensors="pt", max_length=MAX_INPUT_LENGTH, truncation=True, padding=True)
    inputs = {k: v.to(trained_model.device) for k, v in inputs.items()} # Move to device
    
    with torch.no_grad():
        summary_ids = trained_model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=MAX_TARGET_LENGTH + 2, # +2 for safety
            early_stopping=True,
            no_repeat_ngram_size=3 # Avoid repetition
        )
    summary = trained_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Load the best model for inference if needed (Trainer loads it if load_best_model_at_end=True)
# model_path = f"{OUTPUT_DIR}/best_model" # or specific checkpoint
# loaded_model = LongT5ForConditionalGeneration.from_pretrained(model_path)
# loaded_tokenizer = T5Tokenizer.from_pretrained(model_path)
# loaded_model.to(device)

print("\n--- Example Inference with Trained Model ---")
if 'eval_dataset' in locals() and len(eval_dataset) > 0:
    sample_conversation = eval_dataset[0]['conversation'] # Take a sample from your eval set
    print(f"Original Conversation:\n{sample_conversation[:1000]}...") # Print first 1000 chars
    
    # Use the model from the trainer (it should be the best one if load_best_model_at_end=True)
    generated_summary = summarize_text(sample_conversation, trainer.model, tokenizer)
    print(f"\nGenerated Summary:\n{generated_summary}")
    
    actual_summary = eval_dataset[0]['summary']
    print(f"\nActual Summary:\n{actual_summary}")
else:
    print("No eval_dataset available for example inference.")

check_alloc("End of script")