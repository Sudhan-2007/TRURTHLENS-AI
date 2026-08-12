"""Fine-tune a DistilBERT sequence classifier for fake-news detection.

Ready to run when a real dataset and (ideally) a GPU are available:
    python -m ai_engine.training.train_distilbert

Config values live in ai-engine/config/config.py.
"""
import numpy as np
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
    AutoModelForSequenceClassification,
)

from ..config import (
    CLASS_LABELS,
    DISTILBERT_BASE_MODEL,
    DISTILBERT_MODEL_DIR,
    LIAR_TEST_PATH,
    MAX_SEQUENCE_LENGTH,
    NUM_LABELS,
    TEST_SIZE,
    TRAIN_BATCH_SIZE,
    TRAIN_EPOCHS,
    TRAIN_LEARNING_RATE,
    VALIDATION_SIZE,
)
from ..datasets.prepare import default_train_path, load_dataset
from ..evaluation.metrics import evaluate_classification, save_report


def tokenize_fn(examples, tokenizer=None):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding=False,
        max_length=MAX_SEQUENCE_LENGTH,
    )


def main():
    train_df = load_dataset(default_train_path())
    test_df = load_dataset(LIAR_TEST_PATH) if LIAR_TEST_PATH.exists() else None

    if test_df is None:
        train_df, test_df = train_test_split(
            train_df, test_size=TEST_SIZE, stratify=train_df["label_id"], random_state=42
        )

    # 80/10/10 split: carve a validation set out of the training data so the
    # held-out test set is only touched for the final evaluation.
    train_df, val_df = train_test_split(
        train_df, test_size=VALIDATION_SIZE, stratify=train_df["label_id"], random_state=42
    )

    tokenizer = AutoTokenizer.from_pretrained(DISTILBERT_BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        DISTILBERT_BASE_MODEL, num_labels=NUM_LABELS
    )

    train_ds = Dataset.from_pandas(train_df[["text", "label_id"]]).rename_column("label_id", "labels")
    val_ds = Dataset.from_pandas(val_df[["text", "label_id"]]).rename_column("label_id", "labels")
    test_ds = Dataset.from_pandas(test_df[["text", "label_id"]]).rename_column("label_id", "labels")

    train_ds = train_ds.map(tokenize_fn, batched=True, fn_kwargs={"tokenizer": tokenizer})
    val_ds = val_ds.map(tokenize_fn, batched=True, fn_kwargs={"tokenizer": tokenizer})
    test_ds = test_ds.map(tokenize_fn, batched=True, fn_kwargs={"tokenizer": tokenizer})

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    args = TrainingArguments(
        output_dir=str(DISTILBERT_MODEL_DIR),
        num_train_epochs=TRAIN_EPOCHS,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=TRAIN_BATCH_SIZE,
        learning_rate=TRAIN_LEARNING_RATE,
        eval_strategy="epoch",
        save_strategy="steps",
        save_steps=500,
        save_total_limit=3,
        logging_steps=50,
        report_to=[],
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
    )

    last_checkpoint = None
    if DISTILBERT_MODEL_DIR.exists():
        checkpoints = [
            d for d in DISTILBERT_MODEL_DIR.iterdir()
            if d.name.startswith("checkpoint-")
        ]
        if checkpoints:
            last_checkpoint = str(
                max(checkpoints, key=lambda d: int(d.name.split("-")[1]))
            )

    trainer.train(resume_from_checkpoint=last_checkpoint)

    preds = trainer.predict(test_ds)
    y_score = torch.softmax(torch.tensor(preds.predictions), dim=-1)[:, 1].numpy()
    report = evaluate_classification(test_df["label_id"].values, y_score)
    report["dataset"] = "LIAR/PolitiFact" if LIAR_TEST_PATH.exists() else "demo"
    print(f"DistilBERT test metrics: {report}")
    save_report(report, DISTILBERT_MODEL_DIR.parent.parent / "evaluation" / "distilbert_report.json")

    trainer.save_model(str(DISTILBERT_MODEL_DIR))
    tokenizer.save_pretrained(str(DISTILBERT_MODEL_DIR))


if __name__ == "__main__":
    main()
