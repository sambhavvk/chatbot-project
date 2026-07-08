"""
Training Script - Fine-tunes DistilBERT for intent classification on banking77.
Designed to run on NVIDIA RTX 4060 Ti with CUDA.
"""

import os
import json
import logging
from typing import Dict, Any
import numpy as np

import torch
from datasets import load_dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import evaluate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG = {
    "model_name": "distilbert-base-uncased",
    "dataset_name": "mteb/banking77",
    "output_dir": "models/intent_model",
    "num_train_epochs": 5,
    "per_device_train_batch_size": 32,
    "per_device_eval_batch_size": 64,
    "learning_rate": 5e-5,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "eval_steps": 200,
    "save_steps": 200,
    "logging_steps": 100,
    "save_total_limit": 2,
    "load_best_model_at_end": True,
    "metric_for_best_model": "eval_f1",
    "greater_is_better": True,
    "fp16": torch.cuda.is_available(),
    "early_stopping_patience": 3,
    "max_length": 128,
    "seed": 42,
}


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def tokenize_function(examples: Dict[str, Any], tokenizer) -> Dict[str, Any]:
    """Tokenize text examples."""
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=CONFIG["max_length"],
    )


def compute_metrics(eval_pred) -> Dict[str, float]:
    """
    Compute evaluation metrics: accuracy, precision, recall, f1.

    Args:
        eval_pred: Tuple of (logits, labels).

    Returns:
        Dict of metric names to values.
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    accuracy = accuracy_score(labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="weighted", zero_division=0
    )

    return {
        "eval_accuracy": accuracy,
        "eval_precision": precision,
        "eval_recall": recall,
        "eval_f1": f1,
    }


def prepare_dataset() -> tuple:
    """
    Load banking77 dataset and split into train/val/test.

    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset, num_labels, id2label, label2id).
    """
    logger.info("Loading dataset: %s", CONFIG["dataset_name"])
    dataset = load_dataset(CONFIG["dataset_name"])

    # banking77 has a 'train' split only; we need to split it
    full_train = dataset["train"]

    # Create label mappings
    label_names = list(set(full_train["label_text"]))
    label_names.sort()
    id2label = {i: name for i, name in enumerate(label_names)}
    label2id = {name: i for i, name in enumerate(label_names)}

    # Add numeric label column
    def map_label(example):
        example["label"] = label2id[example["label_text"]]
        return example

    full_train = full_train.map(map_label)

    # Split: 80% train, 10% val, 10% test
    train_test = full_train.train_test_split(test_size=0.2, seed=CONFIG["seed"])
    val_test = train_test["test"].train_test_split(
        test_size=0.5, seed=CONFIG["seed"]
    )

    train_dataset = train_test["train"]
    val_dataset = val_test["train"]
    test_dataset = val_test["test"]

    num_labels = len(label_names)
    logger.info("Number of labels: %d", num_labels)
    logger.info(
        "Dataset sizes - Train: %d, Val: %d, Test: %d",
        len(train_dataset),
        len(val_dataset),
        len(test_dataset),
    )

    return train_dataset, val_dataset, test_dataset, num_labels, id2label, label2id


def train() -> None:
    """Main training function."""
    # Check CUDA availability
    if torch.cuda.is_available():
        logger.info("CUDA available: %s", torch.cuda.get_device_name(0))
        logger.info("VRAM: %.1f GB", torch.cuda.get_device_properties(0).total_memory / 1e9)
    else:
        logger.warning("CUDA not available - training on CPU (will be slow)")

    set_seed(CONFIG["seed"])

    # Prepare data
    train_dataset, val_dataset, test_dataset, num_labels, id2label, label2id = (
        prepare_dataset()
    )

    # Load tokenizer and model
    logger.info("Loading model: %s", CONFIG["model_name"])
    tokenizer = DistilBertTokenizerFast.from_pretrained(CONFIG["model_name"])
    model = DistilBertForSequenceClassification.from_pretrained(
        CONFIG["model_name"],
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )

    # Tokenize datasets
    logger.info("Tokenizing datasets...")
    tokenized_train = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer), batched=True
    )
    tokenized_val = val_dataset.map(
        lambda x: tokenize_function(x, tokenizer), batched=True
    )
    tokenized_test = test_dataset.map(
        lambda x: tokenize_function(x, tokenizer), batched=True
    )

    # Set format for PyTorch
    columns = ["input_ids", "attention_mask", "label"]
    tokenized_train.set_format("torch", columns=columns)
    tokenized_val.set_format("torch", columns=columns)
    tokenized_test.set_format("torch", columns=columns)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=CONFIG["output_dir"],
        num_train_epochs=CONFIG["num_train_epochs"],
        per_device_train_batch_size=CONFIG["per_device_train_batch_size"],
        per_device_eval_batch_size=CONFIG["per_device_eval_batch_size"],
        learning_rate=CONFIG["learning_rate"],
        warmup_steps=CONFIG["warmup_steps"],
        weight_decay=CONFIG["weight_decay"],
        eval_strategy="steps",
        eval_steps=CONFIG["eval_steps"],
        save_steps=CONFIG["save_steps"],
        logging_steps=CONFIG["logging_steps"],
        save_total_limit=CONFIG["save_total_limit"],
        load_best_model_at_end=CONFIG["load_best_model_at_end"],
        metric_for_best_model=CONFIG["metric_for_best_model"],
        greater_is_better=CONFIG["greater_is_better"],
        fp16=CONFIG["fp16"],
        report_to="none",
        seed=CONFIG["seed"],
        dataloader_drop_last=False,
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=CONFIG["early_stopping_patience"])],
    )

    # Train
    logger.info("Starting training...")
    trainer.train()

    # Evaluate on test set
    logger.info("Evaluating on test set...")
    test_results = trainer.evaluate(tokenized_test)
    logger.info("Test results: %s", test_results)

    # Save final model and tokenizer
    logger.info("Saving model to %s", CONFIG["output_dir"])
    trainer.save_model(CONFIG["output_dir"])
    tokenizer.save_pretrained(CONFIG["output_dir"])

    # Save label mappings in model directory
    with open(os.path.join(CONFIG["output_dir"], "label_info.json"), "w") as f:
        json.dump({"id2label": id2label, "label2id": label2id}, f, indent=2)

    logger.info("Training complete! Model saved to %s", CONFIG["output_dir"])


if __name__ == "__main__":
    train()