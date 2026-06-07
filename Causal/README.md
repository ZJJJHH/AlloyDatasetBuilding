# Causal Question (Does X Cause Y) Generator

A tool that uses large language models to generate causal relationship analysis questions based on titanium alloy JSONL datasets, examining the model's understanding of alloying element action mechanisms and process parameter influence trends.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage generation parameters and API configuration | `config.json` | Supports management of generation parameters, API parameters, and RAG configuration |
| RAG Retriever | Causal relationship analysis retrieval | `rag_retriever.py` | Retrieval system optimized for causal analysis, supporting element indexing, process parameter indexing, and performance indicator association |
| DeepSeek Client | API call wrapper | `deepseek_client.py` | Supports real API and mock mode, including auto-retry, error handling, and rate limiting management |
| Question Generator | Core generation logic | `generate_causal_questions.py` | Causal relationship construction, three-type classification, mechanism analysis requirements, and scientific rigor assurance |
| Batch Processor | Batch generation management | `run_generation.py` | Supports batch generation, test mode, and custom parameter settings |

### Technical Features

1. **Element Influence Analysis**: Analyzes the influence mechanisms of alloying elements on properties
2. **Process Influence Analysis**: Analyzes the influence trends of process parameters on properties
3. **Composite Influence Analysis**: Analyzes the synergistic mechanisms of elements and processes
4. **Micro-mechanism Explanation**: Explains macroscopic property changes from a microstructural perspective
5. **RAG Enhancement**: Uses a specially optimized RAG retrieval system to obtain relevant alloy data
6. **Three-Type Classification**: Classifies causal relationships into element influence, process influence, and composite influence
7. **Fault Tolerance**: Automatically retries failed API calls with detailed error handling
8. **Progress Tracking**: Provides beautiful tqdm progress bars and detailed generation statistics
9. **Batch Processing**: Supports large-scale batch question generation

## Project Overview

This project aims to generate causal relationship analysis questions for large model training, examining the model's understanding of alloying element action mechanisms and process parameter influence trends.

### Question Type Characteristics
- **Element Influence Analysis**: Mechanisms of alloying element effects on properties
- **Process Influence Analysis**: Trends of process parameter effects on properties
- **Composite Influence Analysis**: Synergistic mechanisms of elements and processes
- **Micro-mechanism Explanation**: Explaining macroscopic property changes from a microstructural perspective

## File Structure

```
Causal/
├── generate_causal_questions.py  # Main generator
├── rag_retriever.py             # RAG retrieval module (mechanism understanding optimized)
├── deepseek_client.py           # DeepSeek API client
├── run_generation.py            # Launch script (with progress bar)
├── config.json                  # Configuration file
├── requirements.txt             # Dependency file
└── README.md                    # Documentation
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
    "output_path": "/path/to/AlloyDatasetBuilding/Causal/causal_questions.json",
    "target_question_count": 1000,
    "batch_size": 3,
    "api_delay": 1.5
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
- **batch_size**: API call batch size
- **api_delay**: API call interval in seconds
- **max_tokens**: Maximum tokens per question (moderate for causal analysis questions)
- **temperature**: Generation randomness (0-1, higher = more random)

## Core Modules

### 1. RAG Retriever (`rag_retriever.py`)

Retrieval system specially optimized for causal relationship analysis:
- **Element Index**: Specialized index by alloying elements
- **Process Parameter Index**: Index by process parameters
- **Performance Indicator Association**: Intelligent association of performance indicators with causal relationships
- **Relevance Scoring**: Scoring algorithm optimized for mechanism understanding

### 2. DeepSeek Client (`deepseek_client.py`)

API call wrapper:
- Supports real API and mock mode
- Auto-retry and error handling
- Rate limiting management
- Call statistics

### 3. Question Generator (`generate_causal_questions.py`)

Core generation logic:
- **Causal Relationship Construction**: Builds causal relationships based on alloying elements and process parameters
- **Three-Type Classification**: Element influence, process influence, composite influence
- **Mechanism Analysis Requirements**: Requires explanation of influence mechanisms and microstructural changes
- **Scientific Rigor Assurance**: Based on materials science principles and practical engineering applications

## Output Format

Generated questions are saved in JSON format using utf-8-sig encoding:

```json
{
  "metadata": {
    "total_questions": 1000,
    "question_type": "causal",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "causal_000001",
      "question_type": "causal",
      "question_text": "Does Al element content cause an increase in the strength of titanium alloys? Please explain its influence mechanism.",
      "causal_scenario": {
        "causal_type": "Element influence",
        "cause": "Adding Al element",
        "effect": "Strength",
        "relationship": "Increase",
        "alloy_composition": "TC4 (Ti-6Al-4V)",
        "application_context": "Aerospace structural components",
        "description": "Analyze the influence mechanism of Al element on titanium alloy strength"
      },
      "reference_alloy": {
        "composition": "TC4 (Ti-6Al-4V)",
        "application": "Aerospace structural components",
        "source_id": "alloy_000123"
      },
      "metadata": {
        "retrieved_query": "TC4 Al element strength",
        "retrieved_count": 3,
        "model_used": "deepseek",
        "causal_complexity": "Intermediate"
      }
    }
  ]
}
```

## Example Questions

### Element Influence Type
- "Does Al element content cause an increase in the strength of titanium alloys? Please explain its influence mechanism."
- "Analyze the improvement mechanism of V element on the toughness of titanium alloys."

### Process Influence Type
- "How does solution treatment temperature affect the corrosion resistance of titanium alloys? Please explain from a microstructural perspective."
- "Mechanism analysis of the promoting effect of aging treatment on the fatigue performance of titanium alloys."

### Composite Influence Type
- "Explore the synergistic influence of Al element content and solution treatment temperature on the thermal stability of titanium alloys."
- "Analyze the composite influence mechanism of V element and aging treatment on the ductility of titanium alloys."

## Progress Bar Feature

The system provides full progress bar display:

**tqdm Beautiful Progress Bar:**
```
Causal question generation progress: 100%|███████████████████████████| 10/10 [00:21<00:00, 2.14s/item]
```

**Simple Progress Display:**
```
Generation progress: 250/1000 (25.0%) | Speed: 28.0 items/min | Estimated remaining: 26.8 min
```

## Causal Relationship Type Coverage

### Supported Causal Relationship Types
- **Element Influence**: Mechanisms of alloying element effects on properties
- **Process Influence**: Trends of process parameter effects on properties
- **Composite Influence**: Synergistic mechanisms of elements and processes

### Alloying Element Coverage
- **Major alloying elements**: Al, V, Sn, Zr, Mo, Nb, Ta, Fe
- **Trace elements**: Cr, Ni, Cu, Si, O, N, H, C

### Process Parameter Coverage
- **Heat treatment processes**: Solution treatment, aging treatment, annealing temperature
- **Deformation processes**: Deformation amount, deformation temperature
- **Cooling processes**: Cooling rate, quenching medium

### Performance Indicator Coverage
- **Mechanical properties**: Strength, ductility, toughness, hardness
- **Durability properties**: Fatigue performance, creep performance
- **Environmental properties**: Corrosion resistance, thermal stability

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
- Causal relationship analysis questions require some thinking time
- Adjust `batch_size` and `delay` parameters as needed
- Consider using local models instead of API calls

## Extension Development

### Adding New Causal Relationship Types
1. Add new types in the causal relationship builder
2. Update the `causal_types` section in the configuration file
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
