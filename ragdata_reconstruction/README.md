# Titanium Alloy CSV-to-JSONL Converter

## Project Overview

This project converts titanium alloy materials science research CSV datasets into JSONL format suitable for large model Retrieval-Augmented Generation (RAG) tasks. The converted data preserves the original CSV column names as JSON key names, facilitating data traceability and maintenance.

## System Architecture and Technical Implementation

### Core Modules

| Module | Function | Implementation File | Technical Details |
|--------|----------|---------------------|-------------------|
| Configuration Management | Manage conversion parameters and file paths | `config.json` | Supports input/output paths, batch size, and encoding settings |
| Data Converter | Core conversion logic | `convert_ti_data.py` | CSV reading, data validation, JSONL writing, and batch processing |
| Text Generator | Semantic enhancement text generation | `text_generator.py` | Natural language description generation, keyword extraction, and performance data summarization |

### Technical Features

1. **Data Conversion**: Preserves original CSV column names as JSON key names, structurally organizing data
2. **Semantic Enhancement**: Automatically generates natural language description text and extracts keyword lists
3. **Retrieval Optimization**: Multi-dimensional retrieval support with vectorization-friendly text format
4. **Batch Processing**: Supports large file batch processing with memory usage optimization
5. **Data Validation**: Built-in data validation and error handling mechanisms
6. **Extensibility**: Supports custom text generation logic and validation rules
7. **Vector Database Integration**: Converted JSONL files can be directly used for vector databases

## File Structure

```
ragdata_reconstruction/
├── convert_ti_data.py      # Main conversion script
├── text_generator.py       # Text description generation module
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## Features

### Data Conversion
- Preserves original CSV column names as JSON key names
- Structurally organizes data (metadata, material_info, performance_data, etc.)
- Supports large file batch processing
- Data validation and error handling

### Semantic Enhancement
- Automatically generates natural language description text
- Extracts keyword lists
- Builds performance data summaries
- Supports mixed Chinese-English content

### Retrieval Optimization
- Multi-dimensional retrieval support (alloy composition, application scenarios, performance parameters, etc.)
- Vectorization-friendly text format
- Supports metadata filtering and sorting

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Configuration Check
Ensure the input file path in `config.json` is correct:

```json
{
  "input_csv": "/path/to/data/csvdata/Ti_data.csv",
  "output_jsonl": "Ti_data_rag.jsonl"
}
```

### 2. Execute Conversion
```bash
python convert_ti_data.py
```

### 3. Verify Results
After conversion, check the output file:
```bash
# Check file size
ls -lh Ti_data_rag.jsonl

# View first few records
head -n 5 Ti_data_rag.jsonl | python -m json.tool
```

## Configuration

### Main Configuration Items

| Item | Description | Default |
|------|-------------|---------|
| `input_csv` | Input CSV file path | `/path/to/data/csvdata/Ti_data.csv` |
| `output_jsonl` | Output JSONL file path | `Ti_data_rag.jsonl` |
| `chunk_size` | Batch processing size | 1000 |
| `encoding` | File encoding | `utf-8` |

### Text Generation Configuration

```json
"text_generation": {
  "max_embedding_text_length": 1000,
  "min_keywords_count": 3,
  "performance_summary_enabled": true
}
```

## Output Format

### JSON Structure

```json
{
  "id": "source_folder_entry_index",
  "metadata": {
    "source_folder": "Data source folder",
    "paper_title": "Paper title",
    "paper_authors": "Author list",
    "paper_innov": "Innovation point description"
  },
  "material_info": {
    "Alloy Composition": "Alloy composition",
    "Material Condition": "Material condition"
  },
  "performance_data": {
    "Tensile_Yield Strength_Engineering Stress (MPa)": "Yield strength",
    "Tensile_Ultimate Tensile Strength_Engineering Stress (MPa)": "Tensile strength"
  },
  "application_info": {
    "Application Domain": "Application domain",
    "Service Environment": "Service environment"
  },
  "elemental_composition": {
    "Al": "Aluminum content",
    "Ti": "Titanium content"
  },
  "embeddings": {
    "text_for_embedding": "Natural language description",
    "keywords": ["Keyword 1", "Keyword 2"],
    "performance_summary": "Performance summary"
  }
}
```

### Text Description Generation Logic

Text descriptions are built according to the following priority:
1. **Paper Information**: Paper title, authors, innovation points
2. **Material Information**: Alloy composition, material condition, preparation process
3. **Performance Data**: Key mechanical property parameters
4. **Application Information**: Application domain, service environment
5. **Research Innovation**: Technical breakthroughs and innovation points

## Advanced Usage

### Custom Text Generation

Modify functions in `text_generator.py` to customize text generation logic:

```python
def custom_embedding_text(row):
    """Custom text description generation"""
    # Your custom logic here
    pass
```

### Batch Processing Multiple Files

Create a batch processing script:

```python
import glob

csv_files = glob.glob("data/*.csv")
for csv_file in csv_files:
    output_file = f"output/{os.path.basename(csv_file).replace('.csv', '.jsonl')}"
    convert_csv_to_jsonl(csv_file, output_file)
```

### Vector Database Integration

Converted JSONL files can be directly used for vector databases:

```python
import chromadb

# Create vector database
client = chromadb.Client()
collection = client.create_collection("titanium_data")

# Load converted data
with open("Ti_data_rag.jsonl", "r") as f:
    for line in f:
        data = json.loads(line)
        
        # Add documents to vector database
        collection.add(
            documents=[data["embeddings"]["text_for_embedding"]],
            metadatas=[{
                "alloy": data["material_info"]["Alloy Composition"],
                "application": data["application_info"]["Application Domain"]
            }],
            ids=[data["id"]]
        )
```

## Troubleshooting

### Common Issues

1. **File Not Found Error**
   ```
   Error: Input file does not exist: /path/to/Ti_data.csv
   ```
   **Solution**: Check the file path in `config.json`

2. **Encoding Error**
   ```
   UnicodeDecodeError: 'utf-8' codec can't decode byte...
   ```
   **Solution**: Change `encoding` in `config.json` to `gbk` or `latin1`

3. **Out of Memory**
   **Solution**: Reduce the `chunk_size` value (e.g., to 500)

### Logging Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Memory Optimization
- Use `chunk_size` to control memory usage
- Process large files in batches
- Release memory resources promptly

### Processing Speed Optimization
- Disable unnecessary validation steps
- Adjust text generation complexity
- Use multi-process processing

## Extension Development

### Adding New Data Fields

1. Add new fields in `config.json`'s `required_columns`
2. Add mappings in `convert_ti_data.py`'s `csv_row_to_json` function
3. Update text generation logic in `text_generator.py`

### Custom Validation Rules

Modify validation functions:
```python
def custom_validation(row):
    """Custom data validation"""
    # Your validation logic here
    pass
```

## Technical Support

For questions or suggestions, please contact the project maintainer.

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-28  
**License**: MIT
