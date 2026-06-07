# Answer Regeneration for a Single Sample

This script is used to regenerate answers for erroneous samples discovered during the scoring phase.

## Features

- Regenerate the answer for a specified question_id
- Automatically locate the question's position in the file
- Overwrite the original erroneous answer
- Support manual specification of the model to use
- Save detailed statistics

## Usage

### Basic Usage

```bash
cd /path/to/AlloyDatasetBuilding/AnswerGeneration

python regenerate_single.py --type <question_type> --id <question_id>
```

### Parameter Description

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--type` | Yes | Question type | `pathway`, `what_if`, `causal`, `mitigation`, `property_lookup` |
| `--id` | Yes | Question ID | `pathway_000123` |
| `--model` | No | Model to use | `deepseek`, `qwen`, `glm`, `minimax` |

### Examples

#### Example 1: Regenerate a pathway answer

```bash
python regenerate_single.py --type pathway --id pathway_000123
```

#### Example 2: Specify DeepSeek model for regeneration

```bash
python regenerate_single.py --type what_if --id what_if_000456 --model deepseek
```

#### Example 3: Specify Qwen model for regeneration

```bash
python regenerate_single.py --type causal --id causal_000789 --model qwen
```

#### Example 4: Regenerate a property lookup answer

```bash
python regenerate_single.py --type property_lookup --id property_lookup_001234
```

#### Example 5: Regenerate a mitigation answer

```bash
python regenerate_single.py --type mitigation --id mitigation_005678
```

## Workflow

1. **Load question file**: Load question data from `/path/to/AlloyDatasetBuilding/{question_type}/{question_type}_questions.json`

2. **Find question**: Locate the corresponding question record in the question list by `question_id`

3. **Generate new answer**: Call the corresponding answer generator to generate a new answer

4. **Update file**: Save the new answer to the corresponding position in the original question file

5. **Save statistics**: Generate and save API call statistics

## Output Information

The script displays the following information:

```
============================================================
Regenerate a single answer
============================================================
Question type: pathway
Question ID: pathway_000123
Model: minimax
============================================================

Question found, index position: 123
Question content: Explain the evolution path of the α phase in TC4 titanium alloy during heat treatment...

Generating new answer...

✓ Answer updated to: /path/to/AlloyDatasetBuilding/Pathway/pathway_questions.json
Answer content preview: The evolution path of the α phase in TC4 titanium alloy during heat treatment...

Statistics saved to: /path/to/AlloyDatasetBuilding/Pathway/pathway_questions_answer_stats_minimax.json

============================================================
✓ Regeneration complete!
============================================================
```

## Important Notes

1. **Overwriting existing answers**: If the question already has an answer, it will be overwritten by the newly generated answer

2. **Model configuration**: If the `--model` parameter is not specified, the default model configured in `config.py` will be used

3. **File path**: The script automatically locates the question file; no need to manually specify the path

4. **Error handling**: If the specified question_id is not found, an error message is displayed and the script exits

## Batch Regeneration

If you need to regenerate answers for multiple erroneous samples, you can create a simple loop script:

```bash
# Create batch processing script
cat > regenerate_batch.sh << 'EOF'
#!/bin/bash

# List of erroneous samples
IDS=(
    "pathway_000123"
    "pathway_000456"
    "pathway_000789"
)

# Question type
TYPE="pathway"

# Loop regeneration
for ID in "${IDS[@]}"; do
    echo "Regenerating: $ID"
    python regenerate_single.py --type $TYPE --id $ID
    echo "Done: $ID"
    echo "---"
done
EOF

# Grant execution permission
chmod +x regenerate_batch.sh

# Run batch processing
./regenerate_batch.sh
```

## FAQ

### Q: How do I know which samples need regeneration?

A: During the AnswerScore scoring phase, if garbled text or other errors are found in answers, you can record the corresponding `question_id` and then use this script to regenerate.

### Q: Will regeneration affect scoring?

A: Yes. The regenerated answer will overwrite the erroneous answer in the original file. Subsequent reruns of the scoring script will use the newly generated answer.

### Q: Can I specify a different model for regeneration?

A: Yes. Use the `--model` parameter to specify a different model, for example:
```bash
python regenerate_single.py --type pathway --id pathway_000123 --model deepseek
```

### Q: Where are the regeneration statistics saved?

A: Statistics are saved in the same directory as the original question file, with the filename:
```
{question_type}_questions_answer_stats_{model_name}.json
```

For example:
```
/pathway_questions_answer_stats_minimax.json
```

## Technical Details

### Script Location

```
/path/to/AlloyDatasetBuilding/AnswerGeneration/regenerate_single.py
```

### Main Functions

- `load_questions(question_type)`: Load question file
- `find_question_by_id(questions_data, question_id)`: Find question record
- `regenerate_single_answer(question_type, question_id, model)`: Regenerate answer

### Supported Question Types

- `what_if`: What-if questions
- `property_lookup`: Property lookup questions
- `causal`: Causal questions
- `mitigation`: Mitigation questions
- `pathway`: Pathway questions

### Supported Models

- `deepseek`: DeepSeek Chat
- `qwen`: Qwen 3.5
- `glm`: GLM-4
- `minimax`: MiniMax-M2.5
