# AlloyDatasetBuilding — Alloy Q&A Dataset Construction

This project aims to construct a comprehensive dataset for training large language models on heavy-alloy inverse design Q&A. It includes four dimensions of professional questions with corresponding answers and a complete scoring system. The project adopts RAG (Retrieval-Augmented Generation) technology to enhance Q&A generation, ensuring accuracy, professionalism, and traceability.

## 1. Question Generation Technical Architecture

### 1.1 Four-Dimensional Question System Design

This project constructs a four-dimensional professional question system oriented toward alloy inverse design, with each type targeting different cognitive levels and engineering requirements:

#### 1.1.1 What-if (Minimal Change)

**Technical Positioning**: Targets material inverse design and multi-objective optimization scenarios, examining the model's creative design capability under constraints.

**Scenario Construction Techniques**:
- **Design Space Definition**: Builds a composition-process-property mapping space based on real alloy data
- **Constraint Generation**: Extracts limiting factors such as cost, density, and process complexity from real engineering constraints
- **Scenario Template Design**: Predefines scenario types such as material design optimization and process path optimization
- **Multi-objective Trade-offs**: Intelligent combination of design objectives and constraints to generate engineering-valuable counterfactual scenarios

**Core Logic**:
- Based on baseline materials, explore performance change trends through composition/process adjustments
- Search for optimal design solutions under multiple constraints
- Embody inverse design thinking: deducing material design parameters from target performance

#### 1.1.2 Causal (Does X Cause Y)

**Technical Positioning**: Examines the model's mechanism-level understanding of alloying element effects and process parameter influence trends.

**Scenario Construction Techniques**:
- **Element-Property Association Library**: Builds an association matrix between alloying elements (Al, V, Sn, Zr, Mo, etc.) and performance indicators (strength, toughness, fatigue, etc.)
- **Process-Property Causal Chain**: Constructs causal relationships between process parameters (heat treatment temperature, cooling rate, deformation amount) and final properties
- **Influence Relationship Types**: Defines increase, decrease, improve, deteriorate, promote, inhibit influence relationships
- **Composite Influence Analysis**: Supports generation of element-process composite influence scenarios

**Core Logic**:
- Clear causal relationship confirmation: answering the binary judgment of "whether X causes an effect"
- Layered mechanism explanation: multi-scale explanation from atomic scale → microstructure → macroscopic properties
- Influencing factor analysis: considering synergistic effects, interactions, and other complex factors

#### 1.1.3 Mitigation (Root Cause + Tests + Mitigation)

**Technical Positioning**: Simulates real engineering failure scenarios, examining the model's systematic analysis and complex failure resolution capability.

**Scenario Construction Techniques**:
- **Failure Mode Library**: Establishes typical failure modes such as stress corrosion cracking, fatigue fracture, high-temperature creep failure, and hydrogen embrittlement
- **Application Scenario Matching**: Selects appropriate failure scenarios based on service environments (aerospace, chemical equipment, biomedical, etc.)
- **Failure Symptom Generation**: Describes typical failure characteristics such as crack propagation, fatigue striations, and creep voids
- **Operating Condition Modeling**: Builds actual service conditions including temperature, pressure, and loading

**Core Logic**:
- Three-dimensional diagnostic framework: systematic analysis of material-process-service environment
- Detection and verification methods: providing non-destructive testing, fractographic analysis, and other verification approaches
- Repair and prevention measures: providing solutions from both short-term repair and long-term prevention dimensions

#### 1.1.4 Pathway (Why / Pathway)

**Technical Positioning**: Requires the model to explain the microstructure evolution path behind macroscopic properties, examining multi-scale correlation modeling capability.

**Scenario Construction Techniques**:
- **Microstructural Feature Library**: Defines microstructural features such as α phase, β phase, grain size, precipitates, and dislocation density
- **Process Path Modeling**: Constructs evolution paths for heat treatment, deformation, cooling, aging, and other process steps
- **Strengthening Mechanism Classification**: Covers solid solution strengthening, precipitation strengthening, grain refinement strengthening, dislocation strengthening, and other mechanisms
- **Multi-scale Correlation**: Complete path chain from atomic scale → microstructure → macroscopic properties

**Core Logic**:
- Complete evolution path: comprehensive description from initial state → intermediate states → final state
- Multi-scale correlation: quantitative association between microstructure evolution and macroscopic properties
- Path control strategy: providing process optimization suggestions based on mechanistic understanding

### 1.2 RAG Retrieval-Augmented Generation Technology

This project employs specially optimized RAG (Retrieval-Augmented Generation) technology to ensure the accuracy and professionalism of question generation.

#### 1.2.1 Retrieval Architecture Design

```
Data Source Layer (Ti_data.jsonl / Al_data.jsonl)
    ↓
Preprocessing Layer (Data Loading & Index Building)
    ↓
Retrieval Layer (Multi-dimensional Keyword Matching)
    ↓
Ranking Layer (Relevance Scoring)
    ↓
Output Layer (Top-K Most Relevant Samples)
```

#### 1.2.2 Multi-dimensional Index Construction

**Alloy Grade Index**:
- Extracts TC series (TC1-TC9), TA series (TA1-TA9), TB series (TB1-TB9)
- Recognizes standard grade formats such as Ti-Al-V
- Supports smart matching of composition descriptions

**Application Domain Index**:
- Aerospace, biomedical, chemical, marine, automotive, etc.
- Establishes domain-property-process association indices

**Performance Data Index**:
- Property types: tensile, fatigue, corrosion, impact, creep, hardness, etc.
- Extracts performance parameter keywords (yield strength, tensile strength, elongation, etc.)

**Embedding Text Index**:
- Converts structured data into natural language descriptions
- Generates embedding texts for semantic matching
- Supports deeper semantic retrieval

#### 1.2.3 Relevance Scoring Algorithm

```python
relevance_score = 
    α × alloy_match_score +
    β × application_match_score +
    γ × performance_match_score +
    δ × keyword_overlap_score
```

- **Alloy Match**: Similarity based on alloy grades and composition descriptions
- **Application Match**: Semantic matching based on application domains
- **Performance Match**: Keyword matching based on performance indicators
- **Keyword Overlap**: Keyword overlap between query and records

#### 1.2.4 Question-Type-Specific Retrieval Strategies

Different question types use different retrieval weights and strategies:

| Question Type | Alloy Grade Weight | Application Domain Weight | Performance Indicator Weight | Retrieval Strategy |
|--------------|-------------------|--------------------------|----------------------------|-------------------|
| What-if | 0.4 | 0.3 | 0.3 | Composition-Process-Property Joint Retrieval |
| Causal | 0.3 | 0.2 | 0.5 | Performance Indicator Priority Retrieval |
| Mitigation | 0.3 | 0.4 | 0.3 | Application Scenario Priority Retrieval |
| Pathway | 0.3 | 0.2 | 0.5 | Performance & Process Joint Retrieval |

### 1.3 Question Generation Pipeline

```
Data Loading → Scenario Generation → RAG Retrieval → Prompt Construction → LLM Generation → Post-processing → Output
```

**Key Steps**:
1. **Scenario Generation**: Generate question scenario descriptions based on predefined templates
2. **RAG Retrieval**: Retrieve the top 3-5 most relevant alloy records as references
3. **Prompt Construction**: Integrate scenario information, reference data, and question requirements into prompts
4. **LLM Generation**: Call large language models to generate professional questions
5. **Post-processing**: Format output, add metadata and citation information

## 2. RAG Retrieval Technical Details

### 2.1 Data Source Structure

**Ti_data.jsonl / Al_data.jsonl**:
- **Material Information**: Alloy composition, material condition
- **Process Information**: Preparation process, heat treatment process, processing technique
- **Performance Data**: Tensile, compression, fatigue, hardness, corrosion performance indicators
- **Test Conditions**: Test temperature, loading rate, etc.
- **Application Information**: Application domain, service environment
- **Innovation Points**: Paper innovation highlights

### 2.2 Retriever Implementation Details

**RAGRetriever Class Core Methods**:

```python
def _build_index(self):
    """Build multi-dimensional indices"""
    - Extract alloy grades → alloy_code_index
    - Extract application domains → application_index
    - Extract performance keywords → performance_index
    - Extract embedding keywords → embedding_index

def retrieve(self, query, k=5):
    """Retrieve Top-K most relevant samples"""
    - Extract query keywords
    - Calculate relevance scores
    - Sort by score
    - Return top K results
```

### 2.3 Score RAG Retriever (ScoreRAGRetriever)

**Dedicated for answer scoring phase**:
- Builds performance parameter index (property_index)
- Supports precise retrieval based on property values
- Provides relevant reference data for scoring models
- Ensures objectivity and consistency of scoring

## 3. Answer Generation Technology

### 3.1 Unified Generation Framework

Adopts a "unified framework + differentiated generation" strategy, with all question types sharing core code:

```
AnswerGenerator (Base Class)
    ├── RAG Retriever
    ├── LLM Client
    └── generate_answer() (subclass implementation)
        ├── WhatIfAnswerGenerator
        ├── CausalAnswerGenerator
        ├── MitigationAnswerGenerator
        └── PathwayAnswerGenerator
```

### 3.2 RAG-Enhanced Answer Generation Pipeline

```
Question Input → RAG Retrieval → Context Building → Prompt Construction → LLM Generation → Answer Output
                                                    ↓
                                            Data Source Citation
```

**Key Features**:
- **Context Enhancement**: Retrieved relevant data serves as generation context
- **Data Citation**: Answers annotated with data source (source_id list)
- **Model Agnostic**: Supports DeepSeek, Qwen, GLM, MiniMax, and other models

### 3.3 Question-Type-Specific Answer Strategies

| Question Type | Answer Structure | Core Requirements |
|--------------|-----------------|-------------------|
| What-if | Multi-scheme comparison | Provide 2-3 feasible schemes, infer based on real data |
| Causal | Mechanism-level explanation | Clear causal relationship, layered mechanism explanation |
| Mitigation | Diagnosis-remediation framework | Root cause analysis, detection and remediation plans |
| Pathway | Complete path chain | Evolution path + multi-scale correlation + control strategy |

## 4. Scoring System Technology

### 4.1 Dual-Round Scoring Architecture

#### Round 1 Scoring (AnswerScore)

**Scoring Model**: DeepSeek / Qwen / GLM / MiniMax

**Scoring Dimensions**:

| Question Type | Scoring Dimensions | Weight Distribution |
|--------------|-------------------|---------------------|
| What-if | Feasibility, Technical Rationality, Data Support, Scheme Diversity, Expression Clarity | 30+30+20+10+10 |
| Causal | Causal Correctness, Mechanism Depth, Terminology Usage, Logical Coherence | 30+30+20+20 |
| Mitigation | Diagnostic Accuracy, Solution Feasibility, Systematicalness, Operability | 30+30+20+20 |
| Pathway | Path Completeness, Mechanism Clarity, Logical Coherence, Professional Depth | 30+30+20+20 |

**Scoring Pipeline**:
1. Load questions and answers from three models
2. Build scoring prompts (including scenario information)
3. Call the scoring model for multi-dimensional evaluation
4. Extract scoring details and reasoning
5. Generate optimization prompts
6. Generate comprehensive optimized answer

#### Round 2 Scoring (AnswerScore2)

**Scoring Model**: Kimi (for high-quality evaluation)

**Scoring Targets**: Answers from four models (DeepSeek, Qwen, MiniMax, GLM-5 optimized)

**Scoring Characteristics**:
- Stricter scoring standards
- More detailed scoring reasoning
- Used for final answer quality verification

### 4.2 Scoring Prompt Design

**Core Elements**:
- Question text and scenario information
- Answers to be evaluated (with model identifiers)
- Scoring dimension and weight descriptions
- Output format requirements
- Scoring reasoning requirements

**Usage of Scoring Reasoning**:
- Used for subsequent answer optimization
- Provides detailed strength/weakness analysis
- Supports comprehensive optimization decisions

### 4.3 Optimized Answer Generation

**Optimization Strategy**:
1. Comprehensively analyze the strengths and weaknesses of each answer
2. Extract the advantageous parts of each answer
3. Compensate for the deficiencies of each answer
4. Generate the optimal comprehensive answer

**Optimization Principles**:
- Retain advantageous content
- Compensate for deficiencies
- Ensure accuracy
- Maintain conciseness

## 5. Data Reconstruction Technology

### 5.1 CSV-to-JSONL Conversion

**ragdata_reconstruction Module**:
- convert_ti_data.py: Titanium alloy CSV data conversion
- text_generator.py: Embedding text generation
- Supports aluminum alloy data processing

### 5.2 Embedding Text Generation Technology

**build_embedding_text() Function**:
- Basic information: paper title, alloy composition, material condition
- Process information: preparation, heat treatment, processing technique
- Performance data: tensile, hardness, fatigue, and other key properties
- Test conditions: temperature, environment, etc.
- Application information: domain, service environment
- Innovation points: simplified description to avoid excessive length

**Text Construction Strategy**:
- Organized in sections, logically clear
- Priority on key data
- Avoid redundant information
- Maintain semantic coherence

## 6. System Technical Characteristics

### 6.1 API Call Management

**Retry Mechanism**:
- Automatically retry failed API calls (default 3 times)
- RateLimitError handling: exponential backoff waiting
- APIError handling: detailed error logging

**Traffic Control**:
- Configurable API call intervals
- Batch size control
- Avoid API rate limiting

### 6.2 Fault Tolerance and Recovery

**Checkpoint Resume**:
- Intermediate results saved periodically
- Support for specifying start index
- Automatically skip already processed data

**Error Handling**:
- Single record failure does not affect the overall process
- Detailed error log records
- Facilitates problem diagnosis

### 6.3 Data Consistency

**Encoding Standards**:
- Unified use of utf-8-sig encoding
- Avoid Chinese garbled text issues
- File format consistency checks

**Format Standards**:
- Unified JSON output format
- Standardized metadata structure
- Consistent field naming

## 7. Project Statistics

### 7.1 Data Scale

| Data Type | Scale | Description |
|-----------|-------|-------------|
| Question Dataset | 4,000 entries | 1,000 per each of 4 dimensions |
| Answer Dataset | 16,000 entries | 4,000 per dimension (4 models) |
| RAG Retrieval Source | 56,515 entries | Titanium alloy data records |
| Scoring Data | 32,000 entries | 16,000 answers × 2 rounds of scoring |

### 7.2 Data Quality Characteristics

- **Based on Real Data**: All questions and answers are based on real alloy data
- **Highly Professional**: Question design conforms to materials science professional standards
- **Good Diversity**: Covers different complexity levels and application scenarios
- **High Practicality**: Has actual engineering application value
- **Traceability**: Each answer is annotated with data sources
- **Multi-model Comparison**: Provides answers and scores from multiple models

### 7.3 System Functions

- **Question Generation**: Professional question generation across 4 dimensions
- **Answer Generation**: Multi-model answer generation
- **Answer Scoring**: Dual-round scoring system
- **Data Reconstruction**: CSV-to-JSONL format conversion
- **Batch Processing**: Large-scale data processing capability
- **Checkpoint Resume**: Continue processing after interruption

## 8. Technology Stack

### 8.1 Core Dependencies

- **LLM APIs**: DeepSeek, Qwen, GLM, MiniMax, Kimi
- **RAG Retrieval**: Custom retriever based on keyword matching
- **Data Processing**: Python standard library (json, re, collections)
- **Progress Display**: tqdm
- **HTTP Requests**: OpenAI Python SDK

### 8.2 Technical Characteristics

- **Modular Design**: Independent functional modules, easy to maintain
- **Extensible Architecture**: Supports adding new question types and models
- **Configuration-Driven**: Flexibly adjust parameters via configuration files
- **Engineering Practices**: Comprehensive error handling and logging

---

**Project Positioning**: Large model training dataset construction for alloy inverse design  
**Technical Core**: RAG-enhanced Q&A generation and multi-round scoring system  
**Application Goal**: Provide professional Q&A training data for heavy alloy material design
