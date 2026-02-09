# Project Context: RPG Dependency Graph Analyzer with Island Detection and AI Analysis

## 1. Mission
Build and enhance a Jupyter Notebook tool that parses legacy RPG source code, loads it into Neo4j for cluster analysis (island detection), and uses AI (DeepSeek) to automatically analyze and name each discovered island. 

## 2. Project Structure
```text
/project-root
├── .devcontainer/ # Infrastructure (See Section 3)
│   ├── devcontainer.json      
│   ├── docker-compose.yml 
|   ├── Dockerfile    
│   └── <setup scripts>             
├── src/ # Source Code (RPG files to analyze)
├── tests/ # Test suite for parser functions
├── rpg_dependency_analyzer.ipynb # Main analysis notebook
├── requirements.txt           # Dependencies
└── CLAUDE.md                  # Context (This file)

```

## 3. Infrastructure (DevContainer)

The environment is already defined. Ensure the solution works within these constraints:

* **Services:**
* `app`: Python 3.10 container.
* `neo4j`: Neo4j 5.x container.


* **Connectivity:**
* **Neo4j URI:** `bolt://neo4j:7687` (Service name is 'neo4j' in docker network) OR `bolt://localhost:7687` if mapped.
* **Auth:** `neo4j` / `password`.


* **Required Plugins:**
* `APOC` and `Graph Data Science (GDS)` are enabled via environment variables in `docker-compose.yml`.