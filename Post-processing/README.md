# Data Post-processing Script

## Feature Overview

This script performs post-processing on the constructed Q&A dataset, primarily including:
- Renaming JSON files (removing the `_questions` suffix)
- Keeping specified fields only
- Sorting answers by total score and renaming them
- Renaming scoring fields

## Main Features

1. **File Renaming**:
   - Renames `causal_questions.json` to `causal.json`
   - Same logic for other dimensions

2. **Field Simplification**:
   - At the question level, keeps: `question_id`, `question_type`, `question_text`, `metadata`
   - In metadata, keeps: `model_used`, `causal_complexity`
   - At the answer level, keeps: `content`, `model_used`, `score_1`, `score_2`

3. **Answer Sorting**:
   - Sorts by the sum of `score2-1` and `score2-2` total scores in descending order
   - Renames answers to `answer_A`, `answer_B`, `answer_C`, `answer_D`

4. **Scoring Field Renaming**:
   - `score2-1` → `score_1`
   - `score2-2` → `score_2`

## Usage

### Basic Usage

```bash
cd /path/to/AlloyDatasetBuilding/Post-processing

# Use default output directory (same as input file)
python data_postprocessing.py --input_json /path/to/your_questions.json

# Specify output directory
python data_postprocessing.py --input_json /path/to/your_questions.json --output_dir /path/to/output
```

### Parameter Description

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--input_json` | Yes | Input JSON file path | `--input_json /path/to/AlloyDatasetBuilding/Causal/causal_questions.json` |
| `--output_dir` | No | Output directory (defaults to input file's directory) | `--output_dir /path/to/AlloyDatasetBuilding/Processed` |

### Examples

```bash
# Process causal question dataset
python data_postprocessing.py \
    --input_json /path/to/AlloyDatasetBuilding/Causal/causal_questions.json

# Process what-if question dataset with specified output directory
python data_postprocessing.py \
    --input_json /path/to/AlloyDatasetBuilding/What_if/what_if_questions.json \
    --output_dir /path/to/AlloyDatasetBuilding/Processed

# Batch process all dimensions
for dim in Causal What_if Mitigation Pathway; do
    python data_postprocessing.py \
        --input_json /path/to/AlloyDatasetBuilding/$dim/${dim,,}_questions.json
done
```

## Input/Output Format

### Input Format

```json
{
  "metadata": {
    "total_questions": 1000,
    "question_type": "causal_questions",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "causal_000000",
      "question_type": "causal",
      "question_text": "Question content",
      "metadata": {
        "model_used": "deepseek",
        "causal_complexity": "Advanced",
        "retrieved_query": "TC4 process parameters",
        "retrieved_count": 3
      },
      "answer_deepseek": {
        "content": "Answer content",
        "model_used": "deepseek",
        "score2-1": {
          "Causal Correctness": "26/30",
          "Mechanism Explanation Depth": "27/30",
          "Terminology Usage": "18/20",
          "Logical Coherence": "18/20",
          "Total Score": "89/100",
          "score_model": "kimi-k2.5"
        },
        "score2-2": { ... }
      },
      "answer_qwen": { ... },
      "answer_minimax": { ... },
      "answer_glm-5_optimized": { ... }
    }
  ]
}
```

### Output Format

```json
{
  "metadata": {
    "total_questions": 1000,
    "question_type": "causal",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "causal_000000",
      "question_type": "causal",
      "question_text": "Question content",
      "metadata": {
        "model_used": "deepseek",
        "causal_complexity": "Advanced"
      },
      "answers": [
        {
          "answer_A": {
            "content": "Best answer content",
            "model_used": "glm-5",
            "score_1": {
              "Causal Correctness": "28/30",
              "Mechanism Explanation Depth": "28/30",
              "Terminology Usage": "18/20",
              "Logical Coherence": "18/20",
              "Total Score": "92/100"
            },
            "score_2": { ... }
          }
        },
        {
          "answer_B": { ... }
        },
        {
          "answer_C": { ... }
        },
        {
          "answer_D": { ... }
        }
      ]
    }
  ]
}
```

## Processing Pipeline

### 1. Metadata Extraction

Extracts key information from the original metadata:
- `model_used`: The model used for question generation
- `causal_complexity`: Question complexity (causal questions only)

### 2. Answer Collection and Sorting

- Collects all 4 answers (answer_deepseek, answer_qwen, answer_minimax, answer_glm-5_optimized)
- Computes the total score for each answer: `score2-1 total + score2-2 total`
- Sorts by total score in descending order

### 3. Answer Renaming

- Highest score answer → `answer_A`
- Second highest answer → `answer_B`
- Third highest answer → `answer_C`
- Fourth highest answer → `answer_D`

### 4. Scoring Field Renaming

- `score2-1` → `score_1`
- `score2-2` → `score_2`

## Application Scenarios

### 1. Model Fine-tuning Data Preparation

The processed data has a more standardized format, suitable for:
- Scoring model fine-tuning
- Inverse design model fine-tuning
- Model evaluation datasets

### 2. Data Analysis

- Sort by answer quality for easier analysis of high-quality answer characteristics
- Unified field naming facilitates data processing

### 3. Data Publication

- Simplified field structure makes data sharing easier
- Clear field naming improves readability

## Important Notes

1. **Field Completeness**: If some answers lack scoring fields, they will be automatically skipped
2. **Sorting Basis**: Sorting is based solely on the sum of `score2-1` and `score2-2` totals
3. **Output Overwrite**: If the output file already exists, it will be overwritten
4. **Encoding**: Output files use UTF-8 encoding

## Extension Features

To add new processing logic, you can:
1. Add new metadata extraction logic in the `extract_metadata_info` function
2. Add new answer field extraction logic in the `extract_answer_info` function
3. Add new processing steps in the `process_question` function

## Technical Support

For questions or suggestions, please check:
1. Whether the JSON file format is correct
2. Whether all scoring fields exist and are in the correct format
3. Whether all answer fields are complete

## Example Output

After processing the causal question dataset, the output file is `causal.json`, containing:
- 1,000 questions
- 4 answers per question (sorted by total score)
- Simplified field structure
- Renamed scoring fields
