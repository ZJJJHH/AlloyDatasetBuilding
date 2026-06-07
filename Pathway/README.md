# Pathway Question (Why/Pathway) Generator

A tool that uses large language models to generate microstructure evolution path explanation questions based on titanium alloy JSONL datasets, requiring the model to explain the microstructure evolution path behind macroscopic properties, examining the model's multi-scale correlation thinking and systematic analysis capability.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage generation parameters and API configuration | `config.json` | Supports management of generation parameters, API parameters, and RAG configuration |
| RAG Retriever | Mechanism explanation optimized retrieval | `rag_retriever.py` | Retrieval system specially optimized for mechanism explanation, supporting microstructure indexing, process procedure indexing, and strengthening mechanism indexing |
| DeepSeek Client | API call wrapper | `deepseek_client.py` | Supports real API and mock mode, including auto-retry, error handling, and rate limiting management |
| Question Generator | Core generation logic | `generate_pathway_questions.py` | Three-type classification, multi-scale analysis, systematic thinking, and scientific rigor |
| Batch Processor | Batch generation management | `run_generation.py` | Supports batch generation, test mode, and custom parameter settings |

### Technical Features

1. **Microstructure Evolution**: Explains the evolution path of microstructure during various processes
2. **Performance Formation Mechanism**: Analyzes the microscopic formation mechanism of macroscopic properties
3. **Process-Structure-Property Correlation**: Elaborates the complete correlation path from process to structure to property
4. **Multi-scale Analysis**: Mechanism explanation from atomic scale to macroscopic scale
5. **Three-Type Classification**: Classifies mechanism explanations into microstructure evolution, performance formation mechanism, and process-structure-property correlation
6. **Systematic Thinking**: Embodies multi-scale correlation and nonlinear relationships
7. **Scientific Rigor**: Based on fundamental materials science principles and thermodynamic principles
8. **RAG Enhancement**: Uses a specially optimized RAG retrieval system to obtain relevant alloy data
9. **Fault Tolerance**: Automatically retries failed API calls with detailed error handling
10. **Progress Tracking**: Provides beautiful tqdm progress bars and detailed generation statistics
11. **Batch Processing**: Supports large-scale batch question generation

## Project Overview

This project aims to generate mechanism explanation questions for large model training, requiring the model to explain the microstructure evolution path behind macroscopic properties, examining the model's multi-scale correlation thinking and systematic analysis capability.

### Question Type Characteristics
- **Microstructure Evolution**: Explains the evolution path of microstructure during various processes
- **Performance Formation Mechanism**: Analyzes the microscopic formation mechanism of macroscopic properties
- **Process-Structure-Property Correlation**: Elaborates the complete correlation path from process to structure to property
- **Multi-scale Analysis**: Mechanism explanation from atomic scale to macroscopic scale

## File Structure

```
Pathway/
├── generate_pathway_questions.py  # Main generator
├── rag_retriever.py               # RAG retrieval module (microstructure optimized)
├── deepseek_client.py             # DeepSeek API client
├── run_generation.py              # Launch script (with progress bar)
├── config.json                    # Configuration file
├── requirements.txt               # Dependency file
└── README.md                      # Documentation
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
    "output_path": "/path/to/AlloyDatasetBuilding/Pathway/pathway_questions.json",
    "target_question_count": 1000,
    "batch_size": 3,
    "api_delay": 2.0
  },
  "deepseek_config": {
    "api_key": "YOUR_API_KEY",
    "max_tokens": 250,
    "temperature": 0.7
  }
}
```

### Parameter Description

- **target_question_count**: Target number of questions to generate (default 1000)
- **batch_size**: API call batch size
- **api_delay**: API call interval in seconds (mechanism explanation questions need more thinking time)
- **max_tokens**: Maximum tokens per question (mechanism explanation questions are usually longer)
- **temperature**: Generation randomness (0-1, higher = more random)

## Core Modules

### 1. RAG Retriever (`rag_retriever.py`)

Retrieval system specially optimized for mechanism explanation:
- **Microstructure Index**: Specialized index by microstructural features
- **Process Procedure Index**: Index by process procedures
- **Strengthening Mechanism Index**: Index by strengthening mechanisms
- **Relevance Scoring**: Scoring algorithm optimized for mechanism explanation

### 2. DeepSeek Client (`deepseek_client.py`)

API call wrapper:
- Supports real API and mock mode
- Auto-retry and error handling
- Rate limiting management
- Call statistics

### 3. Question Generator (`generate_pathway_questions.py`)

Core generation logic:
- **Three-Type Classification**: Microstructure evolution, performance formation mechanism, process-structure-property correlation
- **Multi-scale Analysis**: Complete mechanism explanation from atomic scale to macroscopic scale
- **Systematic Thinking**: Embodies multi-scale correlation and nonlinear relationships
- **Scientific Rigor**: Based on fundamental materials science principles and thermodynamic principles

## Output Format

Generated questions are saved in JSON format using utf-8-sig encoding:

```json
{
  "metadata": {
    "total_questions": 1000,
    "question_type": "pathway",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "pathway_000001",
      "question_type": "pathway",
      "question_text": "Explain the evolution path and controlling factors of the α phase in TC4 titanium alloy during heat treatment.",
      "pathway_scenario": {
        "pathway_type": "Microstructure evolution",
        "micro_feature": "α phase",
        "process": "Heat treatment process",
        "alloy_composition": "TC4 (Ti-6Al-4V)",
        "application_context": "Aerospace structural components",
        "description": "Analyze the evolution path of the α phase in TC4 titanium alloy during heat treatment"
      },
      "reference_alloy": {
        "composition": "TC4 (Ti-6Al-4V)",
        "application": "Aerospace structural components",
        "source_id": "alloy_000123"
      },
      "metadata": {
        "retrieved_query": "TC4 α phase heat treatment",
        "retrieved_count": 3,
        "model_used": "deepseek",
        "pathway_complexity": "Advanced"
      }
    }
  ]
}
```

## Example Questions

### Microstructure Evolution Type
- "Explain the evolution path and controlling factors of the α phase in TC4 titanium alloy during heat treatment."
- "Analyze the evolution mechanism and influencing factors of grain size in titanium alloys during deformation."

### Performance Formation Mechanism Type
- "Elaborate on the precipitation strengthening formation mechanism of strength in titanium alloys and its microscopic basis."
- "Explore the multi-scale correlation mechanism of toughness in titanium alloys and its optimization pathways."

### Process-Structure-Property Correlation Type
- "Analyze how the heat treatment process in TC4 titanium alloy affects the α+β dual-phase structure, which in turn influences fatigue properties — the complete correlation path."
- "Explain the effect of deformation processes on dislocation density in titanium alloys and its action mechanism on creep properties."

## Progress Bar Feature

The system provides full progress bar display:

**tqdm Beautiful Progress Bar:**
```
Pathway question generation progress: 100%|███████████████████████████| 10/10 [00:26<00:00, 2.67s/item]
```

**Simple Progress Display:**
```
Generation progress: 250/1000 (25.0%) | Speed: 22.5 items/min | Estimated remaining: 33.3 min
```

## Mechanism Explanation Type Coverage

### Supported Mechanism Explanation Types
- **Microstructure Evolution**: Evolution path of microstructure during processes
- **Performance Formation Mechanism**: Microscopic formation mechanism of macroscopic properties
- **Process-Structure-Property Correlation**: Complete correlation path analysis

### Microstructural Feature Coverage
- **Phase Constituents**: α phase, β phase, α+β dual-phase structure
- **Grain Characteristics**: Grain size, grain boundary characteristics
- **Defect Structures**: Dislocation density, twins, precipitates
- **Interface Characteristics**: Phase interfaces, texture

### Process Procedure Coverage
- **Heat Treatment Processes**: Solution treatment, aging treatment, annealing
- **Deformation Processes**: Hot deformation, cold deformation
- **Cooling Processes**: Cooling rate, quenching medium
- **Phase Transformation Processes**: Martensitic transformation, recrystallization

### Strengthening Mechanism Coverage
- **Solid Solution Strengthening**: Alloying element solid solution strengthening
- **Precipitation Strengthening**: Secondary phase precipitation strengthening
- **Grain Refinement Strengthening**: Grain boundary strengthening effect
- **Dislocation Strengthening**: Dislocation interaction
- **Transformation Strengthening**: Transformation-induced strengthening

## Important Notes

### API Usage
- Mechanism explanation questions are more complex, requiring more tokens and thinking time
- Ensure the API key is valid and has sufficient balance
- Pay attention to API call rate limits
- It is recommended to test in mock mode first

### Data Quality
- Ensure the RAG data file exists and is in the correct format
- Generated questions require manual review and filtering
- It is recommended to generate in batches and check quality promptly

### Performance Optimization
- Mechanism explanation question generation is slower; be patient
- Adjust `batch_size` and `delay` parameters as needed
- Consider using local models instead of API calls

## Extension Development

### Adding New Mechanism Explanation Types
1. Add new types in the mechanism explanation builder
2. Update the `pathway_types` section in the configuration file
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
