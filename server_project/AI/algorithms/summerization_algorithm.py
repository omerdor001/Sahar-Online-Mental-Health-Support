from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, SummarizationPipeline


class Summarizer:
    _instance = None
    _initialized = False

    def __new__(cls, model_path="../ai_adapters/final_model"):
        print("Creating new Summarizer instance...")
        if cls._instance is None:
            cls._instance = super(Summarizer, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path="/home/stud/sahar_server/testing/server_project/AI/ai_adapters/final_model/"):
        print("Initializing Summarizer...")
        if not Summarizer._initialized:
            print("Initializing model...1")
            try:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            except Exception as e:
                print(f"Error initializing model: {e}")
                raise e
            print("Initializing model...2")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            except Exception as e:
                print(f"Error initializing tokenizer: {e}")
                raise e
            print("Initializing model...3")
            try:
                self.summarizer = SummarizationPipeline(model=self.model, tokenizer=self.tokenizer)
            except Exception as e:
                print(f"Error initializing summarizer: {e}")
                raise e
            print("Initializing model...4")
            Summarizer._initialized = True
            print("Initializing model...5")

    def get_summary(self, text):
        print("Summarizing text...")
        summary = self.summarizer(text,
                    max_new_tokens=128,
                    num_beams=4,
                    no_repeat_ngram_size=2,
                    early_stopping=True)[0]["summary_text"]
        print(f"Summary: {summary}")
        return summary


# Example usage:
if __name__ == "__main__":
    # Both instances will be the same object
    summarizer1 = Summarizer()
    summarizer2 = Summarizer()
    print(f"Are instances the same? {summarizer1 is summarizer2}")  # Will print True
    
    text = "here is the text for inference"
    summary = summarizer1.get_summary(text)
    print(summary)