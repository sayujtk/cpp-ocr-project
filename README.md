# C++ Handwritten Code OCR (Azure OCR + Indentation Recognition)

This project is a **2-step pipeline** to convert an image of **handwritten C++ code** into **digital C++ code with recovered indentation**.

It is inspired by the indentation-recovery idea used in the CodeOCR research pipeline (clustering lines based on x-coordinates), but this implementation is simplified for a student project demo:
- **OCR provider:** Microsoft **Azure** only
- **Post-correction (LLM):** not included yet (planned later)

---

## What the project does (2 steps)

### Step 1 — OCR (Azure)
- Input: a handwritten C++ code image (e.g., `test5.png`)
- Output:
  - prints recognized text to terminal
  - saves full Azure OCR response JSON to a file like `OCR_output_test5.json`

Implemented in: `test_ocr.py`

### Step 2 — Indentation Recognition (MeanShift clustering)
- Input: Azure OCR JSON output from Step 1
- Extracts per-line bounding boxes and uses the **top-left x-coordinate** as a signal for indentation.
- Runs **MeanShift clustering** on x-coordinates to group lines into indentation levels.
- Reconstructs the final code using **4 spaces per indentation level**.

Implemented in:
- `process_indentation.py` (extract Azure JSON → standard format)
- `cpp_indentation_recognition.py` (MeanShift indentation algorithm)
- `run_full_pipeline.py` (end-to-end runner)

---

## Folder / File Structure

Expected structure:

```text
cpp-ocr-project/
├── cpp_indentation_recognition.py     # MeanShift indentation recognition (core)
├── process_indentation.py             # Parses Azure OCR JSON + calls indentation recognizer
├── run_full_pipeline.py               # CLI runner: JSON -> indented .cpp output
├── test_ocr.py                        # Azure OCR script: image -> JSON
├── requirements.txt                   # Python dependencies
├── README.md                          # This file
├── .env                               # Azure credentials (NOT committed)
├── .gitignore                         # Ignore venv, .env, outputs, etc.
├── venv/                              # Python virtual environment (NOT committed)
├── cpp_code_images/                   # Put handwritten C++ images here
│   └── test5.png
├── ocr_outputs/                       # (optional) store OCR JSON outputs here
│   └── OCR_output_test5.json
└── results/                           # final code outputs + metadata
    ├── corrected_test5.cpp
    └── corrected_test5_metadata.json
```

> Notes:
> - `venv/` and `.env` should never be committed.
> - `ocr_outputs/` and `results/` can be committed or ignored depending on whether you want to store demo outputs.

---

## Requirements

- WSL (Ubuntu/Debian)
- Python 3.9+ (you seem to have Python 3.12, that’s fine)
- Azure Computer Vision resource (endpoint + key)

---

## Setup (WSL)

### 1) Install venv support (if needed)
If you got the error **ensurepip is not available**, run:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
```

### 2) Create and activate virtual environment
From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
```

Upgrade pip:

```bash
pip install --upgrade pip
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

---

## Configure Azure credentials

Create a file called `.env` in the project root:

```env
AZURE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
AZURE_KEY=<your_azure_key>
```

---

## Run the pipeline

### Step 1 — Run Azure OCR
1) Put your image in `cpp_code_images/` (example: `test5.png`)
2) In `test_ocr.py`, set:

```python
image_path = "cpp_code_images/test5.png"
```

3) Run:

```bash
python3 test_ocr.py
```

It will generate something like:
- `OCR_output_test5.json`

**Tip:** Move it into `ocr_outputs/` for cleanliness:
```bash
mv OCR_output_test5.json ocr_outputs/
```

---

### Step 2 — Run indentation recognition
```bash
python3 run_full_pipeline.py \
  --input-json ocr_outputs/OCR_output_test5.json \
  --output-file results/corrected_test5.cpp \
  --show-comparison
```

Outputs:
- `results/corrected_test5.cpp` (final indented C++ code)
- `results/corrected_test5_metadata.json` (debug + clustering info)

---

## How indentation recovery works (concept)

Azure provides per-line bounding boxes. For each recognized line we take:
- `x = top-left x-coordinate`

Then:
1. Cluster all line `x` values using **MeanShift**
2. Sort clusters by average x (leftmost cluster = indent level 0)
3. Assign indentation level to each line based on its cluster
4. Rebuild code with: `indent = 4 spaces * indent_level`

This is language-agnostic and works for C++ as long as indentation is visually consistent in the handwritten image.

---

## Troubleshooting

### “code: command not found” in WSL
Install VS Code + Remote WSL extension on Windows, then reopen WSL and try again.

### Azure OCR returns no text
- Check `.env` values
- Confirm the Azure resource supports Read/OCR
- Try a clearer image (higher contrast, less blur)

### Indentation levels look wrong
- Handwriting left margins may be inconsistent
- Try forcing a bandwidth:
```bash
python3 run_full_pipeline.py --input-json ... --output-file ... --bandwidth 25
```

---

## Next steps / planned work
- Add **C++-specific post-correction** (token fixes like `#include`, `std::`, `<<`, `>>`, braces)
- Add optional **LLM post-correction** after indentation recovery
- Add evaluation metrics (edit distance / exact match) on a labeled dataset