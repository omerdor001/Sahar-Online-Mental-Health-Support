import os
import warnings

warnings.filterwarnings("ignore")

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class BasicAlgorithm:
    def __init__(self):
        # creating model and tokenizer

        self.model = AutoModelForSequenceClassification.from_pretrained(
            "onlplab/alephbert-base", num_labels=2
        )
        self.tokenizer = AutoTokenizer.from_pretrained("onlplab/alephbert-base")

        # loading modal and setting it to eval mode to avoid parameters change while predicting
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the relative path to the model file
        relative_path = os.path.join(
            current_dir,
            "alephbert_model.pt",
        )

        # Load the model using the relative path
        self.model_path = relative_path
        self.model.load_state_dict(
            torch.load(self.model_path, map_location=torch.device("cpu"))
        )
        self.model.eval()

    def process(self, texts: [str]):
        # tokenizing the texts and passing them to the model
        tokens = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        )
        outputs = self.model(**tokens)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1).detach().numpy()
        return probabilities
