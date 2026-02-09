# Project Context: RPG Dependency Graph Analyzer with Island Detection

## 1. Mission
Build and enhance a Jupyter Notebook tool that parses legacy source code and loads it into Neo4j for cluster analysis. 

## 2. Project Structure
```text
/project-root
├── .devcontainer/ # Infrastructure (See Section 3)
│   ├── devcontainer.json      
│   ├── docker-compose.yml 
|   ├── Dockerfile    
│   └── <setup scripts>             
├── src/ # Source Code (Simulated Repo)
├── rpg_dependency_analyzer.ipynb # THE OUTPUT (Create this)
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