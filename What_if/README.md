# What-if Question Generator

A tool that uses the DeepSeek API to automatically generate counterfactual design questions based on titanium alloy JSONL datasets, primarily targeting reverse design, multi-objective optimization, and other scenarios for titanium alloy materials.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage generation parameters and API configuration | `config.json` | Supports management of generation parameters, API parameters, and RAG configuration |
| RAG Retriever | Alloy data retrieval | `rag_retriever.py` | Keyword matching-based retrieval system supporting alloy grade recognition, application domain classification, and performance type matching |
| DeepSeek Client | API call wrapper | `deepseek_client.py` | Supports real API and mock mode, including auto-retry, error handling, and rate limiting management |
| Question Generator | Core generation logic | `generate_what_if_questions.py` | Question template design, alloy data parsing, counterfactual question construction, and batch generation control |
| Batch Processor | Batch generation management | `run_generation.py` | Supports batch generation, test mode, and custom parameter settings |

### Technical Features

1. **Counterfactual Thinking**: Raises "what if...then..." type questions based on existing data
2. **Reverse Design**: Thinks about material design starting from performance objectives
3. **Multi-objective Optimization**: Balances mutually conflicting performance requirements
4. **Constraints**: Considers real-world constraints such as cost, process, and environment
5. **RAG Enhancement**: Uses RAG retrieval technology to retrieve relevant alloy data from Ti_data.jsonl
6. **Fault Tolerance**: Automatically retries failed API calls with detailed error handling
7. **Progress Tracking**: Provides beautiful tqdm progress bars and detailed generation statistics
8. **Batch Processing**: Supports large-scale batch question generation

## Project Overview

This project aims to generate counterfactual design questions for large model training, primarily targeting reverse design, multi-objective optimization, and other scenarios for titanium alloy materials.

### Question Type Characteristics
- **Counterfactual Thinking**: Raises "what if...then..." type questions based on existing data
- **Reverse Design**: Thinks about material design starting from performance objectives
- **Multi-objective Optimization**: Balances mutually conflicting performance requirements
- **Constraints**: Considers real-world constraints such as cost, process, and environment

## File Structure

```
What_if/
├── generate_what_if_questions.py  # Main generator
├── rag_retriever.py              # RAG retrieval module
├── deepseek_client.py            # DeepSeek API client
├── run_generation.py             # Launch script
├── config.json                   # Configuration file
├── requirements.txt              # Dependency file
└── README.md                     # Documentation
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit the `config.json` file and set your DeepSeek API key:

```json
{
  "deepseek_config": {
    "api_key": "YOUR_API_KEY",
    ...
  }
}
```

### 3. Run the Generator

#### Basic Usage (requires valid API key)
```bash
python run_generation.py
```

#### Test Mode (uses mock client)
```bash
python run_generation.py --mock --test
```

#### Custom Parameters
```bash
# Generate 500 questions
python run_generation.py --count 500

# Specify output path
python run_generation.py --output /path/to/output.json

# Use custom configuration file
python run_generation.py --config my_config.json
```

## Configuration

### Main Configuration Items

```json
{
  "generation_config": {
    "rag_data_path": "/path/to/AlloyDatasetBuilding/Ti_data.jsonl",
    "output_path": "/path/to/AlloyDatasetBuilding/What_if/what_if_questions.json",
    "target_question_count": 1000,
    "batch_size": 5,
    "api_delay": 1.0
  },
  "deepseek_config": {
    "api_key": "YOUR_API_KEY",
    "max_tokens": 200,
    "temperature": 0.7
  }
}
```

### Parameter Description

- **target_question_count**: Target number of questions to generate (default 1000)
- **batch_size**: API call batch size (controls request frequency)
- **api_delay**: API call interval in seconds
- **max_tokens**: Maximum tokens per question
- **temperature**: Generation randomness (0-1, higher = more random)

## Core Modules

### 1. RAG Retriever (`rag_retriever.py`)

Simple retrieval system based on keyword matching:
- Alloy grade recognition (TC4, Ti-6Al-4V, etc.)
- Application domain classification (aerospace, biomedical, etc.)
- Performance type matching (tensile, fatigue, corrosion, etc.)
- Relevance scoring algorithm

### 2. DeepSeek Client (`deepseek_client.py`)

API call wrapper:
- Supports real API and mock mode
- Auto-retry and error handling
- Rate limiting management
- Call statistics

### 3. Question Generator (`generate_what_if_questions.py`)

Core generation logic:
- Question template design
- Alloy data parsing
- Counterfactual question construction
- Batch generation control

## Output Format

Generated questions are saved in JSON format:

```json
{
  "metadata": {
    "total_questions": 10,
    "question_type": "what_if",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "what_if_000000",
      "question_type": "what_if",
      "question_text": "In aerospace applications, how can the fatigue life of TC4 titanium alloy be improved by adjusting the heat treatment process?",
      "reference_alloy": {
        "composition": "Ti-6Al-4V (wt.%) (TC4)",
        "application": "Biomedical implants",
        "source_id": "alloy_000004"
      },
      "metadata": {
        "retrieved_query": "Corrosion resistant titanium alloy",
        "retrieved_count": 3,
        "model_used": "deepseek"
      }
    }
  ]
}
```

## Example Questions

### Composition Optimization
- "How can the aluminum content in TC4 titanium alloy be adjusted to balance strength and toughness?"
- "In Ti-5Al-2.5Sn alloy, how can high-temperature performance be improved through microalloying additions?"

### Process Adjustment
- "How can the heat treatment process of TC4 be optimized to improve its fatigue life?"
- "How can the processing flow of titanium alloys be simplified while maintaining mechanical properties?"

### Alternative Approaches
- "Under cost constraints, how to design a low-cost titanium alloy to replace TC4?"
- "For biomedical applications, how can the surface biocompatibility of titanium alloys be improved?"

### Multi-objective Optimization
- "How to balance the three conflicting properties of strength, toughness, and corrosion resistance in titanium alloys?"
- "How to find the optimal material design solution between lightweight and high strength?"

## Important Notes

### API Usage
- Ensure the API key is valid and has sufficient balance
- Pay attention to API call rate limits
- It is recommended to test in mock mode first

### Data Quality
- Ensure the RAG data file exists and is in the correct format
- Generated questions require manual review and filtering
- It is recommended to generate in batches and check quality promptly

### Performance Optimization
- Be mindful of API costs when generating large quantities
- Adjust `batch_size` and `delay` parameters as needed
- Consider using local models instead of API calls

## Extension Development

### Adding New Question Types
1. Add new templates in `generate_what_if_questions.py`
2. Update the `question_types` section in the configuration file
3. Modify generation logic to support multiple types

### Improving the Retrieval System
1. Integrate vector databases (e.g., FAISS)
2. Use semantic similarity retrieval
3. Add more complex scoring algorithms

### Quality Evaluation Module
1. Add automatic quality evaluation
2. Integrate manual review interface
3. Establish question filtering criteria

## Technical Support

For questions or suggestions, please check:
1. Whether the configuration file is correct
2. Whether the API key is valid
3. Whether the data file exists
4. Whether all dependency packages are installed
