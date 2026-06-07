# Round 2 Answer Scoring System

This directory contains the second-round scoring code for titanium alloy question answers. The second-round scoring uses the Kimi large language model to independently score four answers (DeepSeek, Qwen, MiniMax, GLM-5 optimized) and selects the highest-scoring answer as the final answer.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage scoring model, round identifier, and scoring dimensions | `config.py` | Supports multi-model configuration, custom scoring rounds and dimension weights |
| Scoring Client | LLM API call wrapper | `score_client.py` | Supports Kimi, DeepSeek, Qwen and other models, including auto-retry and error handling |
| Score Generator | Core scoring logic | `score_generator.py` | RAG-enhanced scoring, multi-dimensional score calculation |
| RAG Retriever | Scoring-specific retrieval | `score_rag_retriever.py` | Hybrid semantic and keyword-based retrieval, automatically filters the most relevant alloy data |
| Batch Processor | Batch scoring and management | `run_all.py` | Incremental saving, checkpoint resume, intermediate file management |
| Score Fixer | Auto-fix scoring issues | `fix_scores_auto.py` | Detects and repairs scoring anomalies, ensuring data consistency |
| Score Validator | Validate scoring results | `validate_scores.py` | Checks scoring completeness and reasonableness, generates validation reports |

### Technical Features

1. **Multi-Model Support**: Supports Kimi, DeepSeek, Qwen, GLM and other LLMs for scoring
2. **RAG-Enhanced Scoring**: Uses a specialized RAG retriever to retrieve relevant alloy data from Ti_data.jsonl for scoring support
3. **Incremental Processing**: Saves intermediate files every 10 samples, supports checkpoint resume
4. **Multi-dimensional Scoring**: Designs specialized scoring dimensions and weights for different question types
5. **Detailed Error Handling**: Includes API call error handling, retry mechanism, and detailed error logging
6. **Statistical Analysis**: Provides detailed API call statistics and scoring result analysis

## Feature Introduction

### Scoring System
- Uses the Kimi LLM for multi-dimensional scoring of four answers
- Supports evaluation schemes for four question dimensions:
  - **What-if**: Feasibility, Technical Rationality, Data Support, Scheme Diversity, Expression Clarity
  - **Causal**: Causal Correctness, Mechanism Explanation Depth, Terminology Usage, Logical Coherence
  - **Mitigation**: Diagnostic Accuracy, Solution Feasibility, Systematicalness, Operability
  - **Pathway**: Path Completeness, Mechanism Clarity, Logical Coherence, Professional Depth

### Scoring Round Identifier
- The second-round scoring uses field names in the `score2-x` format (x is the round identifier)
- Modify the `SCORE_ROUND` parameter in `config.py` to customize the round identifier

## Directory Structure

```
AnswerScore2/
├── config.py              # Configuration file, including Kimi scoring model and scoring dimension configuration
├── score_client.py        # Scoring LLM client (supports Kimi and others)
├── score_generator.py     # Scorer (using RAG retriever)
├── score_rag_retriever.py # Scoring-specific RAG retriever
├── run_all.py             # Batch scoring script
├── README.md              # This document
└── incremental/           # Intermediate file directory (auto-generated)
```

## Configuration

### Scoring Model Selection

Modify the `SCORE_MODEL` variable in `config.py`:

```python
SCORE_MODEL = 'kimi'  # Options: 'kimi', 'deepseek', 'qwen', 'glm', or 'minimax'
```

### Scoring Round Identifier

Modify the `SCORE_ROUND` variable in `config.py`:

```python
SCORE_ROUND = '2-1'  # Custom round identifier, used to generate score2-x field names
```

### Kimi API Configuration

In `config.py`, configure the Kimi LLM API key:

```python
KIMI_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<kimi-api-endpoint>",
    "model": "moonshot-v1-8k",
    "max_tokens": 2000,
    "temperature": 0.7,
    "retry_count": 3,
    "delay_between_calls": 1.5
}
```

### Scoring Dimension Configuration

Each question type has different scoring dimensions and weights, viewable and modifiable in `config.py`:

- `WHAT_IF_SCORE_CONFIG`
- `PROPERTY_LOOKUP_SCORE_CONFIG`
- `CAUSAL_SCORE_CONFIG`
- `MITIGATION_SCORE_CONFIG`
- `PATHWAY_SCORE_CONFIG`

## Quick Start

### 1. Install Dependencies

```bash
pip install openai>=1.0.0 tqdm requests
```

### 2. Configure API Key

In `config.py`, configure the Kimi LLM API key:

```python
KIMI_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "base_url": "<kimi-api-endpoint>",
    "model": "moonshot-v1-8k",
    "max_tokens": 2000,
    "temperature": 0.7,
    "retry_count": 3,
    "delay_between_calls": 1.5
}
```

### 3. Run Scoring

#### Batch Process All Question Types

```bash
cd /path/to/AlloyDatasetBuilding/AnswerScore2
python run_all.py
```

#### Process Specific Question Types

```bash
python run_all.py --types "what_if,causal,mitigation,pathway"
```

#### Process a Range of Questions

```bash
python run_all.py --start 0 --end 100
```

#### Clean Up Intermediate Files

```bash
python run_all.py --clean
```

#### Auto-fix Scoring

```bash
python fix_scores_auto.py
```

#### Validate Scoring Results

```bash
python validate_scores.py
```

## Detailed Scoring Pipeline

### 1. Preparation Phase
- Load configuration files, determine scoring model and round identifier
- Check if question files exist, create intermediate files (if needed)
- Initialize scoring client and RAG retriever

### 2. Scoring Phase
- For each question, extract four answers (DeepSeek, Qwen, MiniMax, GLM-5 optimized)
- Use the RAG retriever to retrieve relevant alloy data (up to 3 records) from Ti_data.jsonl
- Build scoring prompts containing questions, answers, and retrieved alloy data
- Call the LLM API for scoring
- Parse scoring results, extract dimension scores and total scores

### 3. Saving Phase
- Save intermediate files every 10 questions
- After completion, generate final scoring results
- Output API call statistics

### 4. Validation Phase
- Use validate_scores.py to verify the completeness of scoring results
- Check if all answers have scores
- Detect scoring anomalies
- Generate validation reports

## New Feature Descriptions

### 1. Auto-fix Scoring (fix_scores_auto.py)

**Function**: Automatically detect and repair scoring anomalies

**Implementation Details**:
- Detect answers with missing scores
- Identify scoring format errors
- Automatically re-score abnormal items
- Maintain data consistency

**Usage**:
```bash
python fix_scores_auto.py
```

### 2. Score Validation (validate_scores.py)

**Function**: Validate the completeness and reasonableness of scoring results

**Implementation Details**:
- Check if all answers have scores
- Verify scoring format correctness
- Detect scoring anomalies (e.g., total score out of range)
- Generate detailed validation reports

**Usage**:
```bash
python validate_scores.py
```

### 3. Scoring Round Management

**Function**: Support multi-round scoring and round identifier management

**Implementation Details**:
- Set the round identifier via the `SCORE_ROUND` variable in config.py
- Scoring results are stored in field names with the score2-x format (x is the round identifier)
- Support parallel storage and comparison of multi-round scoring results

**Configuration Example**:
```python
SCORE_ROUND = '2-1'  # Round 2, first scoring
# Scoring field name will be score2-1
```

## Scoring Result Format

Scoring results are added to the original question file in the following format:

```json
{
  "answer_deepseek": {
    "content": "...",
    "data_sources": [...],
    "model_used": "deepseek",
    "score2-1": {
      "Feasibility": "27/30",
      "Technical Rationality": "28/30",
      "Data Support": "18/20",
      "Scheme Diversity": "9/10",
      "Expression Clarity": "9/10",
      "Total Score": "91/100",
      "score_model": "moonshot-v1-8k"
    }
  },
  "answer_qwen": {
    "content": "...",
    "data_sources": [...],
    "model_used": "qwen3.5-397b-a17b",
    "score2-1": {
      "Feasibility": "28/30",
      "Technical Rationality": "29/30",
      "Data Support": "19/20",
      "Scheme Diversity": "9/10",
      "Expression Clarity": "9/10",
      "Total Score": "94/100",
      "score_model": "moonshot-v1-8k"
    }
  },
  "answer_minimax": {
    "content": "...",
    "data_sources": [...],
    "model_used": "MiniMax-M2.5",
    "score2-1": {
      "Feasibility": "26/30",
      "Technical Rationality": "27/30",
      "Data Support": "17/20",
      "Scheme Diversity": "8/10",
      "Expression Clarity": "9/10",
      "Total Score": "87/100",
      "score_model": "moonshot-v1-8k"
    }
  },
  "answer_glm-5_optimized": {
    "content": "...",
    "data_sources": [...],
    "model_used": "glm-5_optimized",
    "score2-1": {
      "Feasibility": "29/30",
      "Technical Rationality": "30/30",
      "Data Support": "20/20",
      "Scheme Diversity": "10/10",
      "Expression Clarity": "10/10",
      "Total Score": "99/100",
      "score_model": "moonshot-v1-8k"
    }
  }
}
```

### Notes

- **All Answers**: Include the `score2-x` field (x is the round identifier), recording the scoring results
- **score_model**: Records the name of the scoring model used

## Intermediate File Management

- The system incrementally saves intermediate files every 10 samples
- Intermediate files are saved in the same directory as the original question file, with filenames like `xxx.intermediate_2-1`
- After full completion, intermediate files are used to overwrite the original question files
- Use the `--clean` parameter to clean up intermediate files

## API Call Statistics

After completion, the system outputs API call statistics:

```
API Call Statistics: {
  "total_calls": 200,
  "successful_calls": 195,
  "failed_calls": 5,
  "success_rate": "97.5%",
  "model": "moonshot-v1-8k"
}
```

## Evaluation Dimension Description

### What-if

| Evaluation Dimension | Weight | Description |
|---------------------|--------|-------------|
| Feasibility | 30% | Whether the scheme is feasible and the process is realizable |
| Technical Rationality | 30% | Whether the technical approach is reasonable and the mechanism is scientific |
| Data Support | 20% | Whether there is data source support and accurate citations |
| Scheme Diversity | 10% | Whether multiple schemes are provided and diverse |
| Expression Clarity | 10% | Whether the expression is clear and the structure is reasonable |

### Causal

| Evaluation Dimension | Weight | Description |
|---------------------|--------|-------------|
| Causal Correctness | 30% | Whether the causal relationship is correct |
| Mechanism Explanation Depth | 30% | Whether the mechanism is deeply explained |
| Terminology Usage | 20% | Whether professional terminology is used |
| Logical Coherence | 20% | Whether the reasoning process is coherent |

### Mitigation

| Evaluation Dimension | Weight | Description |
|---------------------|--------|-------------|
| Diagnostic Accuracy | 30% | Whether the problem diagnosis is accurate |
| Solution Feasibility | 30% | Whether the solutions are feasible |
| Systematicalness | 20% | Whether the problem is systematically analyzed |
| Operability | 20% | Whether the solutions are operable |

### Pathway

| Evaluation Dimension | Weight | Description |
|---------------------|--------|-------------|
| Path Completeness | 30% | Whether the path description is complete |
| Mechanism Clarity | 30% | Whether the mechanism description is clear |
| Logical Coherence | 20% | Whether the reasoning process is coherent |
| Professional Depth | 20% | Whether the professional depth is sufficient |

## Important Notes

1. **API Call Costs**: The scoring process requires API calls to the Kimi LLM; please manage costs
2. **Delay Settings**: The system defaults to a 1.5-second delay between API calls to avoid rate limiting
3. **Error Retries**: The system automatically retries failed API calls up to 3 times
4. **Intermediate Files**: Regularly back up intermediate files to prevent data loss
5. **Scoring Model**: The Kimi LLM excels in professional domain evaluation
6. **RAG Retriever**: The system uses a specialized RAG retriever (score_rag_retriever.py) to retrieve relevant alloy data from Ti_data.jsonl for data corroboration during scoring

## FAQ

### Q: Scoring results not saved to the original file?
A: Check the intermediate files (e.g., `xxx.intermediate_2-1`). After full completion, they will automatically overwrite the original file.

### Q: How to reprocess a specific question type?
A: Simply run `python run_all.py --types "question_type"`.

### Q: How to process only some questions?
A: Use the `--start` and `--end` parameters to specify a range, e.g., `--start 0 --end 100`.

### Q: How are relevant alloy data obtained during scoring?
A: The system uses a specialized RAG retriever (score_rag_retriever.py) to retrieve relevant alloy data from Ti_data.jsonl. The retriever automatically retrieves the top 3 most relevant alloy records based on alloy composition, performance category, test conditions, and other information in the question scenario, providing them as scoring evidence to the scoring LLM.

### Q: How to modify the round identifier?
A: Modify the `SCORE_ROUND` variable in `config.py`, for example, `SCORE_ROUND = '2-1'`, and the scoring field name will automatically change to `score2-1`.

## Contributions

For questions or suggestions, please contact the project maintainer.

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-13  
**License**: MIT
