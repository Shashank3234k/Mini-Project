#!/usr/bin/env python
"""Test script to verify disease data loading"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from chatbot.data_loader import DiseaseDataLoader

# Load disease data
loader = DiseaseDataLoader(str(PROJECT_ROOT / "disease_info.json"))

# Test retrieving Fungal Infection
disease = loader.get_disease("fungal infection")
print("=" * 60)
print(f"Disease data keys: {disease.keys()}")
print("=" * 60)

for key, value in disease.items():
    if isinstance(value, list):
        print(f"{key}: (list with {len(value)} items)")
        for item in value[:2]:  # Print first 2
            print(f"  • {item}")
    else:
        val_str = str(value)[:100]  # First 100 chars
        print(f"{key}: {val_str}")

print("=" * 60)
print("✅ All disease fields loaded successfully!")
