import torch
from safetensors.torch import load_file
from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments

#Cathleen


# Trainer starten & Modell speichern
def transform(train_data): 
    # Minimalistisches PyTorch Dataset
    class TweetDataset(torch.utils.data.Dataset):
        def __init__(self, path):
            self.data = load_file(path)
        def __len__(self):
            return len(self.data["labels"])
        def __getitem__(self, idx):
            return {k: v[idx] for k, v in self.data.items()}

    # Modell laden (Trump vs. Musk = 2 Klassen)
    model = AutoModelForSequenceClassification.from_pretrained("vinai/bertweet-base", num_labels=2)

    # Training-Konfiguration
    args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=64, # Nutzt deinen VRAM effizient
        num_train_epochs=3,
        fp16=True,                       # Hardware-Beschleunigung
        save_strategy="no",              # Spart Zeit
        report_to="none"
    )

    trainer = Trainer(model=model, args=args, train_dataset=TweetDataset(train_data))
    trainer.train() # TODO: Error handeling?
    model.save_pretrained("./final_model")
    print("Training beendet. Modell gespeichert in './final_model'.")
   
    return 0
