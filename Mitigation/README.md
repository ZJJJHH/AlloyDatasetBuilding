# Mitigation Question (Root Cause + Tests + Mitigation) Generator

A tool that uses large language models to generate engineering failure diagnosis questions based on titanium alloy JSONL datasets, simulating complex failure analysis requirements in real engineering scenarios.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage generation parameters and API configuration | `config.json` | Supports management of generation parameters, API parameters, and RAG configuration |
| RAG Retriever | Failure diagnosis optimized retrieval | `rag_retriever.py` | Retrieval system specially optimized for failure diagnosis, supporting failure type indexing, application scenario classification, and performance parameter association |
| DeepSeek Client | API call wrapper | `deepseek_client.py` | Supports real API and mock mode, including auto-retry, error handling, and rate limiting management |
| Question Generator | Core generation logic | `generate_mitigation_questions.py` | Failure scenario construction, three-part structure, complexity grading, and engineering realism |
| Batch Processor | Batch generation management | `run_generation.py` | Supports batch generation, test mode, and custom parameter settings |

### Technical Features

1. **Root Cause Analysis**: Analyzes failure mechanisms and key influencing factors
2. **Detection & Diagnosis Methods**: Proposes detection techniques and diagnostic procedures
3. **Repair & Prevention Measures**: Formulates repair plans and prevention strategies
4. **Three-Part Structure**: Each question includes root cause analysis, detection & diagnosis methods, and repair & prevention measures
5. **Complexity Grading**: Automatically assesses question complexity (Beginner/Intermediate/Advanced)
6. **Engineering Realism**: Ensures questions have practical engineering significance and challenge
7. **RAG Enhancement**: Uses a specially optimized RAG retrieval system to obtain relevant alloy data
8. **Fault Tolerance**: Automatically retries failed API calls with detailed error handling
9. **Progress Tracking**: Provides beautiful tqdm progress bars and detailed generation statistics
10. **Batch Processing**: Supports large-scale batch question generation

## Project Overview

This project aims to generate failure diagnosis questions for large model training, simulating complex failure analysis requirements in real engineering scenarios.

### Question Type Characteristics
- **Root Cause Analysis**: Analyzes failure mechanisms and key influencing factors
- **Tests & Diagnosis**: Proposes detection techniques and diagnostic procedures
- **Mitigation & Prevention**: Formulates repair plans and prevention strategies

## File Structure

```
Mitigation/
├── generate_mitigation_questions.py  # Main generator
├── rag_retriever.py                 # RAG retrieval module (failure diagnosis optimized)
├── deepseek_client.py               # DeepSeek API client
├── run_generation.py                # Launch script (with progress bar)
├── config.json                      # Configuration file
├── requirements.txt                 # Dependency file
└── README.md                        # Documentation
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
    "output_path": "/path/to/AlloyDatasetBuilding/Mitigation/mitigation_questions.json",
    "target_question_count": 1000,
    "batch_size": 3,
    "api_delay": 2.0
  },
  "deepseek_config": {
    "api_key": "YOUR_API_KEY",
    "max_tokens": 300,
    "temperature": 0.7
  }
}
```

### Parameter Description

- **target_question_count**: Target number of questions to generate (default 1000)
- **batch_size**: API call batch size (smaller for more complex failure diagnosis questions)
- **api_delay**: API call interval in seconds (more thinking time needed for failure diagnosis)
- **max_tokens**: Maximum tokens per question (failure diagnosis questions are usually longer)
- **temperature**: Generation randomness (0-1, higher = more random)

## Core Modules

### 1. RAG Retriever (`rag_retriever.py`)

Retrieval system specially optimized for failure diagnosis:
- **Failure Type Index**: Specialized index by failure type
- **Application Scenario Classification**: Engineering scenarios such as aerospace, biomedical, chemical equipment
- **Performance Parameter Association**: Intelligent association of performance parameters with failure modes
- **Relevance Scoring**: Scoring algorithm optimized for failure diagnosis

### 2. DeepSeek Client (`deepseek_client.py`)

API call wrapper:
- Supports real API and mock mode
- Auto-retry and error handling
- Rate limiting management
- Call statistics

### 3. Question Generator (`generate_mitigation_questions.py`)

Core generation logic:
- **Failure Scenario Construction**: Builds realistic failure scenarios based on alloy characteristics and application contexts
- **Three-Part Structure**: Root cause analysis + Detection & diagnosis methods + Repair & prevention measures
- **Complexity Grading**: Automatically assesses question complexity (Beginner/Intermediate/Advanced)
- **Engineering Realism**: Ensures questions have practical engineering significance and challenge

## Output Format

Generated questions are saved in JSON format using utf-8-sig encoding:

```json
{
  "metadata": {
    "total_questions": 1000,
    "question_type": "mitigation",
    "dataset_version": "1.0"
  },
  "questions": [
    {
      "question_id": "mitigation_000001",
      "question_type": "mitigation",
      "question_text": "For the stress corrosion cracking problem occurring in TC4 titanium alloy aerospace engine blades, please analyze the root cause, propose detection methods, and formulate repair and prevention measures.",
      "failure_scenario": {
        "alloy": "TC4 titanium alloy",
        "application": "Aerospace engine blades",
        "failure_type": "Stress corrosion cracking",
        "symptoms": "Cracks appearing, propagating along grain boundaries, with corrosion products on the surface",
        "operating_conditions": "High temperature and high pressure environment, subjected to centrifugal force and aerodynamic loads"
      },
      "reference_alloy": {
        "composition": "TC4 (Ti-6Al-4V)",
        "application": "Aerospace structural components",
        "source_id": "alloy_000123"
      },
      "metadata": {
        "retrieved_query": "TC4 stress corrosion",
        "retrieved_count": 3,
        "model_used": "deepseek",
        "complexity_level": "Advanced"
      }
    }
  ]
}
```

## Example Questions

### Stress Corrosion Cracking Type
- "For the stress corrosion cracking problem occurring in TC4 titanium alloy aerospace engine blades, please analyze the root cause, propose detection methods, and formulate repair and prevention measures."

### Fatigue Fracture Type
- "Fatigue fracture failure of TC4 titanium alloy in biomedical implants. Please conduct a systematic failure analysis and propose solutions."

### High-Temperature Creep Failure Type
- "High-temperature creep failure mechanism analysis of titanium alloys in chemical equipment reactor vessels. Design detection procedures and prevention strategies."

### Hydrogen Embrittlement Type
- "Hydrogen embrittlement failure of titanium alloys in offshore platform structural components. Please propose a complete diagnosis and repair plan."

## Progress Bar Feature

The system provides full progress bar display:

**tqdm Beautiful Progress Bar:**
```
Mitigation question generation progress: 100%|███████████████████████████| 10/10 [00:27<00:00, 2.74s/item]
```

**Simple Progress Display:**
```
Generation progress: 250/1000 (25.0%) | Speed: 21.9 items/min | Estimated remaining: 34.2 min
```

## Failure Type Coverage

### Supported Failure Types
- **Stress Corrosion Cracking**: Cracks propagating along grain boundaries, with corrosion products on the surface
- **Fatigue Fracture**: Fatigue cracks under cyclic loading
- **High-Temperature Creep Failure**: Plastic deformation and creep voids at high temperatures
- **Hydrogen Embrittlement**: Brittle fracture caused by hydrogen atom penetration
- **Corrosion Perforation**: Material thinning due to localized corrosion
- **Wear Failure**: Dimensional changes due to surface wear
- **Impact Damage**: Brittle fracture under impact loading
- **Thermal Fatigue**: Thermal stress cracks under thermal cycling

### Application Scenario Coverage
- Aerospace engine blades
- Chemical equipment reactor vessels
- Biomedical implants
- Offshore platform structural components
- Automotive engine components
- Nuclear power plant heat exchangers
- Sports equipment
- Military equipment

## Important Notes

### API Usage
- Failure diagnosis questions are more complex, requiring more tokens and thinking time
- Ensure the API key is valid and has sufficient balance
- Pay attention to API call rate limits
- It is recommended to test in mock mode first

### Data Quality
- Ensure the RAG data file exists and is in the correct format
- Generated questions require manual review and filtering
- It is recommended to generate in batches and check quality promptly

### Performance Optimization
- Failure diagnosis question generation is slower; be patient
- Adjust `batch_size` and `delay` parameters as needed
- Consider using local models instead of API calls

## Extension Development

### Adding New Failure Types
1. Add new failure types in the failure scenario builder
2. Update the `failure_scenarios` section in the configuration file
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
