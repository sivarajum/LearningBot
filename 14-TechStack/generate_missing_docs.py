#!/usr/bin/env python3
"""
Script to generate missing documentation files (what.md, Visual.md, Interview.md)
for TechStack tools that have interactive HTML files but are missing documentation
"""
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent

# Technology metadata for documentation generation
TECH_METADATA = {
    'dbt': {
        'name': 'dbt',
        'full_name': 'Data Build Tool (dbt)',
        'description': 'Data build tool for transforming data in your warehouse using SQL',
        'category': 'Data Engineering',
        'icon': '🏗️',
        'features': ['SQL-based transformations', 'Version control', 'Testing', 'Documentation', 'Modularity']
    },
    # Add more as needed
}

def create_what_md(tech_dir, tech_key, metadata):
    """Create what.md file"""
    name = metadata.get('name', tech_key)
    full_name = metadata.get('full_name', name)
    description = metadata.get('description', f'{full_name} comprehensive guide')
    
    content = f"""# {full_name}: Comprehensive Guide

## Overview

{description}

## Core Concepts

### What is {full_name}?

{description}

## Key Features

"""
    for feature in metadata.get('features', []):
        content += f"- **{feature}**: Description\n"
    
    content += f"""
## Installation

```bash
# Installation instructions
```

## Getting Started

```bash
# Quick start examples
```

## Advanced Usage

```python
# Advanced examples
```

## Best Practices

1. Best practice 1
2. Best practice 2
3. Best practice 3

## References

- Official documentation: 
- GitHub repository:
"""
    return content

def create_visual_md(tech_dir, tech_key, metadata):
    """Create Visual.md file"""
    name = metadata.get('name', tech_key)
    full_name = metadata.get('full_name', name)
    
    content = f"""# {full_name}: Visual Guide

## Architecture Diagrams

### {full_name} Architecture

```mermaid
graph TD
    A[{full_name}] --> B[Component 1]
    A --> C[Component 2]
    A --> D[Component 3]
    B --> E[Feature 1]
    C --> F[Feature 2]
    D --> G[Feature 3]
```

### Data Flow

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Transform]
    C --> D[Output]
```

### Workflow

```mermaid
flowchart TD
    Start([Start]) --> Step1[Step 1]
    Step1 --> Step2[Step 2]
    Step2 --> Step3[Step 3]
    Step3 --> End([End])
```
"""
    return content

def create_interview_md(tech_dir, tech_key, metadata):
    """Create Interview.md file"""
    name = metadata.get('name', tech_key)
    full_name = metadata.get('full_name', name)
    
    content = f"""# {full_name} Interview Questions and Answers

## Beginner Level Questions

### Q1: What is {full_name} and what problem does it solve?

**Answer:**

{metadata.get('description', 'Description of the tool')}

**Key Use Cases:**
- Use case 1
- Use case 2
- Use case 3

### Q2: What are the core features of {full_name}?

**Answer:**

The core features include:

"""
    for feature in metadata.get('features', []):
        content += f"- **{feature}**: Explanation\n"
    
    content += f"""
### Q3: How do you get started with {full_name}?

**Answer:**

```bash
# Installation and setup steps
```

## Intermediate Level Questions

### Q4: What are the best practices for using {full_name}?

**Answer:**

1. Best practice 1
2. Best practice 2
3. Best practice 3

## Advanced Level Questions

### Q5: How does {full_name} handle [advanced topic]?

**Answer:**

Advanced explanation with code examples.

```python
# Example code
```

## References

- Official documentation
- Community resources
"""
    return content

def main():
    print("🚀 Generating missing documentation files...\n")
    
    # For now, let's focus on dbt as an example
    tech_key = 'dbt'
    tech_dir = BASE_DIR / tech_key
    metadata = TECH_METADATA.get(tech_key, {
        'name': tech_key,
        'full_name': tech_key.upper(),
        'description': f'{tech_key.upper()} comprehensive guide',
        'features': []
    })
    
    if not tech_dir.exists():
        print(f"⚠️  Directory {tech_dir} does not exist")
        return
    
    # Create what.md
    what_file = tech_dir / 'what.md'
    if not what_file.exists():
        content = create_what_md(tech_dir, tech_key, metadata)
        what_file.write_text(content, encoding='utf-8')
        print(f"✅ Created {what_file}")
    
    # Create Visual.md
    visual_file = tech_dir / 'Visual.md'
    if not visual_file.exists():
        content = create_visual_md(tech_dir, tech_key, metadata)
        visual_file.write_text(content, encoding='utf-8')
        print(f"✅ Created {visual_file}")
    
    # Create Interview.md
    interview_file = tech_dir / 'Interview.md'
    if not interview_file.exists():
        content = create_interview_md(tech_dir, tech_key, metadata)
        interview_file.write_text(content, encoding='utf-8')
        print(f"✅ Created {interview_file}")

if __name__ == '__main__':
    main()

