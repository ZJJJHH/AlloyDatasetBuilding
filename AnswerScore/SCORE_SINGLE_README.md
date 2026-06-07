# Re-scoring a Single Sample

This script is used to re-score and re-optimize samples after answer regeneration.

## Features

- Re-score a sample with a specified question_id
- Automatically locate the question's position in the file
- Re-generate scores and optimized answers
- Keep other model answers unchanged
- Save detailed statistics

## Usage

### Basic Usage

```bash
cd /path/to/AlloyDatasetBuilding/AnswerScore

python score_single.py --type <question_type> --id <question_id>
```

### Parameter Description

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--type` | Yes | Question type | `pathway`, `what_if`, `causal`, `mitigation`, `property_lookup` |
| `--id` | Yes | Question ID | `pathway_000123` |

### Examples

#### Example 1: Re-score a pathway question

```bash
python score_single.py --type pathway --id pathway_000123
```

#### Example 2: Re-score a what-if question

```bash
python score_single.py --type what_if --id what_if_000456
```

#### Example 3: Re-score a causal question

```bash
python score_single.py --type causal --id causal_000789
```

#### Example 4: Re-score a property lookup question

```bash
python score_single.py --type property_lookup --id property_lookup_001234
```

#### Example 5: Re-score a mitigation question

```bash
python score_single.py --type mitigation --id mitigation_005678
```

## Workflow

1. **Load question file**: Load question data from `/path/to/AlloyDatasetBuilding/{question_type}/{question_type}_questions.json`

2. **Find question**: Locate the corresponding question record in the question list by `question_id`

3. **Re-score**: Call the scorer to re-score answers from three models (DeepSeek, Qwen, MiniMax)

4. **Re-optimize**: Re-generate an optimized answer based on the new scoring results

5. **Update file**: Save the scoring and optimization results to the corresponding position in the original question file

6. **Save statistics**: Generate and save API call statistics

## Output Information

The script displays the following information:

```
============================================================
Re-scoring a single sample
============================================================
Question type: pathway
Question ID: pathway_000123
Scoring model: glm
============================================================

Question found, index position: 123
Question content: Explain the evolution path of the α phase in TC4 titanium alloy during heat treatment...

Scoring in progress...
Scoring complete

Optimizing answer in progress...
Optimization complete

✓ Scoring and optimization results updated to: /path/to/AlloyDatasetBuilding/Pathway/pathway_questions.json

Scoring results:
  deepseek: 85/100
  qwen: 92/100
  minimax: 78/100
  glm_optimized: Generated

Statistics saved to: /path/to/AlloyDatasetBuilding/Pathway/pathway_questions_score_stats_glm.json

============================================================
✓ Re-scoring complete!
============================================================
```

## Important Notes

1. **Overwriting existing scores**: If the question already has scores, they will be overwritten by the new scores

2. **Optimized answer**: A new optimized answer will be generated based on the new scoring results

3. **Preserving other fields**: Only the scoring and optimized answer fields are updated; other fields (such as question content, reference_alloy, etc.) remain unchanged

4. **File path**: The script automatically locates the question file; no need to manually specify the path

5. **Error handling**: If the specified question_id is not found, an error message is displayed and the script exits

## Batch Re-scoring

If you need to re-score multiple samples, you can create a simple loop script:

```bash
# Create batch processing script
cat > score_batch.sh << 'EOF'
#!/bin/bash

# List of erroneous samples (needing re-scoring)
IDS=(
    "pathway_000123"
    "pathway_000456"
    "pathway_000789"
)

# Question type
TYPE="pathway"

# Loop re-scoring
for ID in "${IDS[@]}"; do
    echo "Re-scoring: $ID"
    python score_single.py --type $TYPE --id $ID
    echo "Done: $ID"
    echo "---"
done
EOF

# Grant execution permission
chmod +x score_batch.sh

# Run batch processing
./score_batch.sh
```

## FAQ

### Q: Why is re-scoring needed?

A: After answer regeneration, the original scores are outdated and need to be re-scored to obtain the latest scoring results. In particular, when answers have errors (such as garbled text) and are regenerated, re-scoring is mandatory.

### Q: Does re-scoring affect answers from other models?

A: No. Re-scoring only updates the scoring results and optimized answer fields. Answers from other models (such as the content fields of deepseek, qwen) remain unchanged.

### Q: After re-scoring, can I only update the scores without optimizing the answer?

A: The current version performs both scoring and optimization simultaneously. If you only need scoring without optimization, you can modify the `score_single.py` script and comment out the optimization section.

### Q: Where are the re-scoring statistics saved?

A: Statistics are saved in the same directory as the original question file, with the filename:
```
{question_type}_questions_score_stats_{scoring_model}.json
```

For example:
```
/pathway_questions_score_stats_glm.json
```

## Technical Details

### Script Location

```
/path/to/AlloyDatasetBuilding/AnswerScore/score_single.py
```

### Main Functions

- `load_questions(question_type)`: Load question file
- `find_question_by_id(questions_data, question_id)`: Find question record
- `score_single_question(question_type, question_id)`: Re-score a single question

### Supported Question Types

- `what_if`: What-if questions
- `property_lookup`: Property lookup questions
- `causal`: Causal questions
- `mitigation`: Mitigation questions
- `pathway`: Pathway questions

### Supported Scoring Models

- `deepseek`: DeepSeek Chat
- `qwen`: Qwen 3.5
- `glm`: GLM-5
- `minimax`: MiniMax-M2.5

### Scoring and Optimization Pipeline

1. **Scoring Phase**:
   - Score the DeepSeek answer
   - Score the Qwen answer
   - Score the MiniMax answer
   - Generate scoring details and reasoning

2. **Optimization Phase**:
   - Extract the advantages of each answer based on scoring details
   - Generate a comprehensive optimized answer
   - Add it to the question record

## Integration with Answer Regeneration Script

Complete erroneous sample repair workflow:

```bash
# 1. Regenerate answer
cd /path/to/AlloyDatasetBuilding/AnswerGeneration
python regenerate_single.py --type pathway --id pathway_000123

# 2. Re-score
cd /path/to/AlloyDatasetBuilding/AnswerScore
python score_single.py --type pathway --id pathway_000123
```

Or create a unified script:

```bash
cat > fix_single_sample.sh << 'EOF'
#!/bin/bash

ID=$1
TYPE=$2

if [ -z "$ID" ] || [ -z "$TYPE" ]; then
    echo "Usage: ./fix_single_sample.sh <question_id> <question_type>"
    echo "Example: ./fix_single_sample.sh pathway_000123 pathway"
    exit 1
fi

echo "=== Regenerating Answer ==="
cd /path/to/AlloyDatasetBuilding/AnswerGeneration
python regenerate_single.py --type $TYPE --id $ID

echo ""
echo "=== Re-scoring ==="
cd /path/to/AlloyDatasetBuilding/AnswerScore
python score_single.py --type $TYPE --id $ID

echo ""
echo "=== Done ==="
EOF

chmod +x fix_single_sample.sh

# Usage
./fix_single_sample.sh pathway_000123 pathway
```
