# Answer Generation System Documentation

## Project Overview

This system provides answer generation capabilities for the titanium alloy Q&A dataset. It adopts a "unified framework + differentiated generation" strategy, supports multiple large language models (DeepSeek, Qwen), and combines RAG retrieval technology to ensure answer accuracy and traceability.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage model parameters and RAG configuration | `config.py` | Supports multi-model configuration, RAG parameter adjustment, and generation parameter settings |
| RAG Retriever | Deep semantic matching retrieval | `rag_retriever.py` | Hybrid keyword and semantic retrieval, supports question-type-specific retrieval strategies |
| LLM Client | LLM API call wrapper | `llm_client.py` | Supports DeepSeek, Qwen and other models, including auto-retry and error handling |
| Answer Generator | Unified answer generation framework | `answer_generator.py` | Provides a common answer generation pipeline with differentiated question-type handling |
| What-if Generator | What-if answer generation | `generate_what_if_answers.py` | Specialized generation strategy for what-if questions |
| Property Lookup Generator | Property lookup answer generation | `generate_property_lookup_answers.py` | Specialized generation strategy for property lookup questions |
| Causal Generator | Causal answer generation | `generate_causal_answers.py` | Specialized generation strategy for causal questions |
| Mitigation Generator | Mitigation answer generation | `generate_mitigation_answers.py` | Specialized generation strategy for mitigation questions |
| Pathway Generator | Pathway answer generation | `generate_pathway_answers.py` | Specialized generation strategy for pathway questions |
| Batch Processor | Batch generation management | `run_all.py` | Supports batch processing across dimensions, test mode, and checkpoint resume |
| System Test | System functionality testing | `test_system.py` | Tests system component functionality to ensure proper operation |

### Technical Features

1. **Unified Framework**: All dimensions share core code with inheritance-based differentiated generation
2. **RAG Enhancement**: Deep semantic matching retrieval enhancement to ensure answer accuracy and traceability
3. **Multi-Model Support**: Supports DeepSeek, Qwen, and other LLMs, easily switchable via configuration files
4. **Fault Tolerance**: Auto-retry of failed API calls, periodic saving of intermediate results, detailed error logging
5. **Batch Processing**: Supports large-scale batch data processing with test mode and checkpoint resume
6. **Incremental Saving**: Saves intermediate results every 10 samples to ensure data safety
7. **Detailed Statistics**: Provides detailed API call statistics and generation result analysis

## System Architecture

```
AnswerGeneration/
├── config.py                      # Configuration file (API keys, model parameters, etc.)
├── rag_retriever.py               # RAG retriever (deep semantic matching)
├── llm_client.py                  # LLM client (DeepSeek/Qwen)
├── answer_generator.py            # Unified answer generation framework
├── generate_what_if_answers.py    # What-if answer generation
├── generate_property_lookup_answers.py  # Property lookup answer generation
├── generate_causal_answers.py     # Causal answer generation
├── generate_mitigation_answers.py # Mitigation answer generation
├── generate_pathway_answers.py    # Pathway answer generation
├── run_all.py                     # Batch execution for all dimensions
└── README.md                      # This document
```

## Quick Start

### 1. Configure API Keys

Edit the `config.py` file and set the LLM API keys:

```python
# Select the model to use
LLM_MODEL = 'deepseek'  # Options: 'deepseek' or 'qwen'

# DeepSeek configuration
DEEPSEEK_CONFIG = {
    "api_key": "YOUR_API_KEY",  # Replace with your DeepSeek API key
    "base_url": "<deepseek-api-endpoint>",
    "model": "deepseek-chat",
    "max_tokens": 1500,
    "temperature": 0.7,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0
}

# Qwen configuration (if using Qwen)
QWEN_CONFIG = {
    "api_key": "YOUR_API_KEY",  # Replace with your Qwen API key
    "base_url": "<qwen-api-endpoint>",
    "model": "qwen-plus",
    "max_tokens": 1500,
    "temperature": 0.7,
    "top_p": 0.95,
    "retry_count": 3,
    "delay_between_calls": 1.0
}
```

### 2. Install Dependencies

```bash
cd /path/to/AlloyDatasetBuilding/AnswerGeneration
pip install requests tqdm
```

### 3. Run Answer Generation

#### Method 1: Generate a Single Dimension

```bash
# Generate what-if answers
python generate_what_if_answers.py

# Generate property lookup answers
python generate_property_lookup_answers.py

# Generate causal answers
python generate_causal_answers.py

# Generate mitigation answers
python generate_mitigation_answers.py

# Generate pathway answers
python generate_pathway_answers.py
```

#### Method 2: Batch Generate All Dimensions

```bash
# Generate all dimensions
python run_all.py

# Generate specific dimensions
python run_all.py --types what_if,property_lookup,causal

# Generate a specific range (indices 0-100)
python run_all.py --start 0 --end 100

# Test mode (processes first 5 only)
python run_all.py --test
```

#### Method 3: Specify Parameters

```bash
# Start from index 100, generate to index 200
python generate_what_if_answers.py --start 100 --end 200

# Test mode
python generate_what_if_answers.py --test
```

### 4. Quick Reference Card

#### Basic Commands

```bash
# Test the system
python test_system.py

# Generate property lookup answers
python generate_property_lookup_answers.py

# Generate what-if answers
python generate_what_if_answers.py

# Generate causal answers
python generate_causal_answers.py

# Generate mitigation answers
python generate_mitigation_answers.py

# Generate pathway answers
python generate_pathway_answers.py

# Batch generate all dimensions
python run_all.py
```

#### Parameter Options

```bash
# Test mode (processes first 5 only)
python run_all.py --test

# Specify range
python run_all.py --start 0 --end 100

# Specify type
python run_all.py --types property_lookup

# Multiple types
python run_all.py --types what_if,causal
```

#### Checkpoint Resume

```bash
# Continue from a specified index
python run_all.py --start 1000

# Specify range
python run_all.py --start 500 --end 1000
```

#### Model Switching

```bash
# Edit config.py
vi config.py

# Modify model selection
LLM_MODEL = 'deepseek'  # or 'qwen'

# Set corresponding API key
DEEPSEEK_CONFIG["api_key"] = "your-key-here"
# or
QWEN_CONFIG["api_key"] = "your-key-here"
```

### 5. Complete Usage Workflow

```bash
# 1. Enter directory
cd /path/to/AlloyDatasetBuilding/AnswerGeneration

# 2. Edit configuration (set API keys)
vi config.py

# 3. Test the system
python test_system.py

# 4. Generate property lookup answers (test)
python generate_property_lookup_answers.py --test

# 5. Generate all dimensions (production)
python run_all.py
```

## Question Type Descriptions

### 1. What-if
**Characteristics**: Highly logical, focusing on design thinking and multi-objective optimization
**Answer Strategy**:
- Provide 2-3 feasible schemes with different technical routes
- Infer performance change trends based on real data
- Include microstructural evolution explanations

### 2. Property Lookup
**Characteristics**: Look-up type questions requiring precise matching
**Answer Strategy**:
- Direct lookup or interpolation from the dataset
- Annotate data sources and test conditions
- Provide uncertainty explanations

### 3. Causal
**Characteristics**: Requires mechanism-level explanation and causal reasoning
**Answer Strategy**:
- Clear causal relationship confirmation
- Layered mechanism explanation (atomic → micro → macroscopic)
- Analyze influencing factors and synergistic effects

### 4. Mitigation
**Characteristics**: Systematic analysis requiring multi-dimensional diagnosis
**Answer Strategy**:
- Root cause analysis (material-process-service three dimensions)
- Detection and verification methods
- Repair and prevention measures

### 5. Pathway
**Characteristics**: Complete path explanation with multi-scale correlation
**Answer Strategy**:
- Complete evolution path (initial → process → intermediate → final)
- Multi-scale correlation (atomic → micro → macroscopic)
- Path control strategy

## Answer Storage Format

Answers are saved directly to the original question file in the following format:

```json
{
  "question_id": "what_if_000000",
  "question_type": "what_if",
  "question_text": "...",
  "reference_alloy": {...},
  "answer_deepseek": {  // or answer_qwen
    "content": "Main answer content",
    "data_sources": ["alloy_000001", "alloy_000002"],
    "model_used": "deepseek-chat"
  }
}
```

## RAG Retrieval Configuration

Configure RAG parameters in `config.py`:

```python
RAG_CONFIG = {
    "data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
    "retrieval_top_k": 5,  # Retrieve top K most relevant samples
    "retrieval_threshold": 0.3,  # Similarity threshold
    "enable_rag": True  # Whether to enable RAG retrieval
}
```

## Advanced Configuration

### Adjust Generation Parameters

```python
GENERATION_CONFIG = {
    "batch_size": 1,  # Batch size
    "start_index": 0,  # Start index
    "end_index": None,  # End index (None means all)
    "save_interval": 10,  # Save interval (save every N items)
    "enable_backup": True  # Whether to enable backup
}
```

### Adjust Model Parameters

You can adjust temperature, top_p, and other parameters in `config.py`:

```python
DEEPSEEK_CONFIG = {
    "temperature": 0.7,  # Generation diversity (0-1)
    "top_p": 0.95,       # Nucleus sampling threshold
    "max_tokens": 1500,  # Maximum number of tokens
    "retry_count": 3,    # Number of failure retries
    "delay_between_calls": 1.0  # Interval between API calls
}
```

## Troubleshooting

### 1. API Call Failure

**Cause**: Invalid API key or network issue

**Solution**:
- Check if the API key is correct
- Verify network connectivity
- Check the error log for specific error messages

### 2. Slow Generation Speed

**Cause**: API call interval set too long

**Solution**:
- Reduce the `delay_between_calls` parameter
- Be careful not to call too frequently, which may cause API rate limiting

### 3. Poor Answer Quality

**Cause**: Model parameters or prompts need adjustment

**Solution**:
- Adjust the `temperature` parameter (increase diversity)
- Check the quality of RAG retrieval results
- Check if the generated prompts are complete

### 4. Checkpoint Resume

If generation is interrupted, you can continue from a specified index:

```bash
python generate_what_if_answers.py --start 100
```

## Output Files

After each dimension is generated, the following files are produced in the same directory as the original question file:

1. **Original question file** (updated, includes answers)
   - `What_if/what_if_questions.json`
   - `PropertyLookup/property_lookup_questions.json`
   - etc.

2. **Statistics file**
   - `What_if/what_if_questions_answer_stats_deepseek.json`
   - Contains API call statistics, success rate, etc.

3. **Backup file** (if enabled)
   - `*.backup_xxx` format

## Technical Features

### 1. Unified Framework
- All dimensions share core code
- Inheritance-based differentiated generation
- Easy to maintain and extend

### 2. RAG Enhancement
- Based on deep semantic matching
- Supports question-type-specific retrieval strategies
- Ensures answer accuracy and traceability

### 3. Multi-Model Support
- DeepSeek model
- Qwen model
- Easily switchable via configuration files

### 4. Fault Tolerance Mechanisms
- Auto-retry of failed API calls
- Periodic saving of intermediate results
- Detailed error logging

## Important Notes

1. **API Call Frequency**: Set an appropriate `delay_between_calls` to avoid API rate limiting
2. **Cost Control**: Monitor API call frequency and token consumption
3. **Data Backup**: Back up original question files before generation
4. **Test First**: Use the `--test` parameter for initial testing
5. **Network Stability**: Ensure stable network connectivity to avoid timeouts

## Contact

For questions or suggestions, please review the code comments or run logs.
