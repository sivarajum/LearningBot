// TechStack Learning Hub - Main Application JavaScript

// Technology data structure
const technologies = {
    devops: [
        { name: 'Docker', path: 'DevOps/Docker', icon: 'fab fa-docker', description: 'Containerization platform for building and shipping applications' },
        { name: 'Kubernetes', path: 'DevOps/Kubernetes', icon: 'fab fa-kubernetes', description: 'Container orchestration platform for managing containerized applications' },
        { name: 'Terraform', path: 'DevOps/Terraform', icon: 'fas fa-mountain', description: 'Infrastructure as Code tool for building, changing, and versioning infrastructure' },
        { name: 'GitHub Actions', path: 'DevOps/GitHub-Actions', icon: 'fab fa-github', description: 'CI/CD automation platform integrated with GitHub' },
        { name: 'Jenkins', path: 'DevOps/Jenkins', icon: 'fab fa-jenkins', description: 'Open-source automation server for building, testing, and deploying' },
        { name: 'Monitoring', path: 'DevOps/Monitoring', icon: 'fas fa-chart-line', description: 'Observability and monitoring tools for infrastructure and applications' },
    ],
    data: [
        { name: 'Apache Spark', path: 'DataEngineering/ApacheSpark', icon: 'fas fa-bolt', description: 'Distributed data processing engine for large-scale data analytics' },
        { name: 'Apache Airflow', path: 'DataEngineering/ApacheAirflow', icon: 'fas fa-wind', description: 'Workflow orchestration platform for data pipelines' },
        { name: 'Python', path: 'DataEngineering/Python', icon: 'fab fa-python', description: 'Data processing and scripting language for data engineering' },
        { name: 'Scala', path: 'DataEngineering/Scala', icon: 'fas fa-code', description: 'Functional programming language for big data processing' },
        { name: 'Java', path: 'DataEngineering/Java', icon: 'fab fa-java', description: 'Enterprise data processing and big data applications' },
        { name: 'SQL', path: 'DataEngineering/SQL', icon: 'fas fa-database', description: 'Database querying and data manipulation language' },
        { name: 'Kafka', path: 'DataEngineering/Kafka', icon: 'fas fa-stream', description: 'Distributed event streaming platform for real-time data pipelines' },
        { name: 'Apache Kafka', path: 'ApacheKafka', icon: 'fas fa-stream', description: 'Event streaming platform for building real-time data pipelines' },
        { name: 'Data Modeling', path: 'DataModeling', icon: 'fas fa-project-diagram', description: 'Designing data structures and schemas for databases' },
        { name: 'Data Pipelines', path: 'DataPipelines', icon: 'fas fa-project-diagram', description: 'ETL/ELT pipelines for data transformation and movement' },
        { name: 'Data Warehousing', path: 'DataWarehousing', icon: 'fas fa-warehouse', description: 'Centralized data storage and analytics systems' },
        { name: 'Real-Time Processing', path: 'Real-TimeProcessing', icon: 'fas fa-clock', description: 'Streaming data processing and real-time analytics' },
    ],
    gcp: [
        { name: 'BigQuery', path: 'GCP/BigQuery', icon: 'fas fa-chart-bar', description: 'Serverless data warehouse for large-scale analytics' },
        { name: 'Cloud Storage', path: 'GCP/Cloud-Storage', icon: 'fas fa-cloud-upload-alt', description: 'Object storage service for storing and accessing data' },
        { name: 'Vertex AI', path: 'GCP/Vertex-AI', icon: 'fas fa-brain', description: 'ML platform and MLOps for building and deploying ML models' },
        { name: 'Cloud Run', path: 'GCP/Cloud-Run', icon: 'fas fa-rocket', description: 'Serverless container platform for running stateless containers' },
        { name: 'Cloud Functions', path: 'GCP/Cloud-Functions', icon: 'fas fa-bolt', description: 'Serverless functions for event-driven applications' },
        { name: 'Dataflow', path: 'GCP/Dataflow', icon: 'fas fa-stream', description: 'Stream and batch data processing service' },
        { name: 'Cloud SQL', path: 'GCP/CloudSQL', icon: 'fas fa-database', description: 'Managed relational database service' },
        { name: 'Cloud Spanner', path: 'GCP/Spanner', icon: 'fas fa-globe', description: 'Globally distributed relational database' },
        { name: 'GKE', path: 'GCP/GKE', icon: 'fas fa-cubes', description: 'Google Kubernetes Engine for container orchestration' },
        { name: 'Pub/Sub', path: 'GCP/PubSub', icon: 'fas fa-envelope', description: 'Messaging service for event-driven systems' },
        { name: 'Compute Engine', path: 'GCP/ComputeEngine', icon: 'fas fa-server', description: 'Virtual machines for running workloads' },
        { name: 'VPC', path: 'GCP/VPC', icon: 'fas fa-network-wired', description: 'Virtual private cloud networking' },
        { name: 'IAM', path: 'GCP/IAM', icon: 'fas fa-shield-alt', description: 'Identity and Access Management' },
        { name: 'Cloud Build', path: 'GCP/CloudBuild', icon: 'fas fa-hammer', description: 'CI/CD platform for building and testing applications' },
        { name: 'Cloud Monitoring', path: 'GCP/CloudMonitoring', icon: 'fas fa-chart-line', description: 'Monitoring and observability for GCP resources' },
        { name: 'Cloud Logging', path: 'GCP/CloudLogging', icon: 'fas fa-file-alt', description: 'Centralized logging service' },
        { name: 'Bigtable', path: 'GCP/Bigtable', icon: 'fas fa-table', description: 'NoSQL wide-column database for large-scale applications' },
        { name: 'Firestore', path: 'GCP/Firestore', icon: 'fas fa-fire', description: 'NoSQL document database' },
        { name: 'Workflows', path: 'GCP/Workflows', icon: 'fas fa-sitemap', description: 'Serverless workflow orchestration' },
        { name: 'Load Balancing', path: 'GCP/LoadBalancing', icon: 'fas fa-balance-scale', description: 'Distributed load balancing service' },
        { name: 'Looker', path: 'GCP/Looker', icon: 'fas fa-chart-pie', description: 'Business intelligence and data visualization platform' },
        { name: 'BigQuery ML', path: 'GCP/BigQueryML', icon: 'fas fa-brain', description: 'Machine learning in BigQuery' },
        { name: 'AutoML', path: 'GCP/AutoML', icon: 'fas fa-robot', description: 'Automated machine learning platform' },
        { name: 'Container Registry', path: 'GCP/ContainerRegistry', icon: 'fas fa-box', description: 'Container image storage and management' },
    ],
    'ai-ml': [
        { name: 'scikit-learn', path: 'AI-ML/scikit-learn', icon: 'fas fa-robot', description: 'Machine learning library for Python' },
        { name: 'TensorFlow', path: 'AI-ML/TensorFlow', icon: 'fas fa-network-wired', description: 'Deep learning framework for building neural networks' },
        { name: 'PyTorch', path: 'AI-ML/PyTorch', icon: 'fas fa-fire', description: 'Deep learning research framework' },
        { name: 'MLflow', path: 'AI-ML/MLflow', icon: 'fas fa-chart-line', description: 'ML lifecycle management platform' },
        { name: 'Weights & Biases', path: 'AI-ML/Weights-Biases', icon: 'fas fa-weight', description: 'Experiment tracking and ML platform' },
        { name: 'Jupyter', path: 'AI-ML/Jupyter', icon: 'fas fa-book', description: 'Interactive computing environment for data science' },
        { name: 'Machine Learning', path: 'MachineLearning', icon: 'fas fa-brain', description: 'Comprehensive guide to machine learning concepts' },
        { name: 'MLOps', path: 'MLOps', icon: 'fas fa-cogs', description: 'ML operations and production ML workflows' },
    ],
    'gen-ai': [
        { name: 'OpenAI GPT', path: 'Gen-AI/OpenAI-GPT', icon: 'fas fa-comments', description: 'Large language models and GPT API' },
        { name: 'LangChain', path: 'Gen-AI/LangChain', icon: 'fas fa-link', description: 'Framework for building LLM applications' },
        { name: 'Vector Databases', path: 'Gen-AI/Vector-Databases', icon: 'fas fa-vector-square', description: 'Databases optimized for vector similarity search' },
        { name: 'Embeddings', path: 'Gen-AI/Embeddings', icon: 'fas fa-brain', description: 'Text vectorization and semantic representations' },
        { name: 'RAG', path: 'Gen-AI/RAG', icon: 'fas fa-search', description: 'Retrieval-augmented generation systems' },
        { name: 'LLMs', path: 'LLMs', icon: 'fas fa-language', description: 'Large Language Models guide' },
        { name: 'LLMOps', path: 'LLMOps', icon: 'fas fa-cogs', description: 'LLM operations and production workflows' },
        { name: 'RAG (Root)', path: 'RAG', icon: 'fas fa-search', description: 'Retrieval-augmented generation' },
    ],
    frontend: [
        { name: 'React', path: 'Frontend/React', icon: 'fab fa-react', description: 'Component-based UI framework for building user interfaces' },
        { name: 'TypeScript', path: 'Frontend/TypeScript', icon: 'fas fa-file-code', description: 'Typed superset of JavaScript' },
        { name: 'Streamlit', path: 'Frontend/Streamlit', icon: 'fas fa-stream', description: 'Python framework for building data apps' },
        { name: 'Material-UI', path: 'Frontend/Material-UI', icon: 'fas fa-paint-brush', description: 'React component library implementing Material Design' },
        { name: 'D3.js', path: 'Frontend/D3.js', icon: 'fas fa-chart-pie', description: 'Data visualization library for creating interactive charts' },
    ],
    backend: [
        { name: 'FastAPI', path: 'Backend/FastAPI', icon: 'fas fa-bolt', description: 'Modern Python web framework for building APIs' },
        { name: 'Node.js', path: 'Backend/Node.js', icon: 'fab fa-node-js', description: 'JavaScript runtime for server-side development' },
        { name: 'Python', path: 'Backend/Python', icon: 'fab fa-python', description: 'Backend development with Python' },
        { name: 'Redis', path: 'Backend/Redis', icon: 'fas fa-memory', description: 'In-memory data store and cache' },
        { name: 'SQLite', path: 'Backend/SQLite', icon: 'fas fa-database', description: 'Lightweight embedded database' },
    ],
    databases: [
        { name: 'PostgreSQL', path: 'Databases/PostgreSQL', icon: 'fas fa-elephant', description: 'Advanced open-source relational database' },
        { name: 'MongoDB', path: 'Databases/MongoDB', icon: 'fas fa-leaf', description: 'NoSQL document database' },
        { name: 'Neo4j', path: 'Databases/Neo4j', icon: 'fas fa-project-diagram', description: 'Graph database for connected data' },
        { name: 'Elasticsearch', path: 'Databases/Elasticsearch', icon: 'fas fa-search', description: 'Search and analytics engine' },
        { name: 'Redis', path: 'Databases/Redis', icon: 'fas fa-memory', description: 'In-memory key-value store' },
        { name: 'BigQuery', path: 'BigQuery', icon: 'fas fa-chart-bar', description: 'Serverless data warehouse' },
    ],
    tools: [
        { name: 'VS Code', path: 'Tools/VS-Code', icon: 'fas fa-code', description: 'Popular code editor with extensive extensions' },
        { name: 'Jupyter', path: 'Tools/Jupyter', icon: 'fas fa-book', description: 'Interactive computing environment' },
        { name: 'Git', path: 'Tools/Git', icon: 'fab fa-git-alt', description: 'Version control system' },
        { name: 'Pandas', path: 'Tools/Pandas', icon: 'fas fa-table', description: 'Data manipulation and analysis library' },
        { name: 'NumPy', path: 'Tools/NumPy', icon: 'fas fa-calculator', description: 'Numerical computing library' },
        { name: 'Matplotlib', path: 'Tools/Matplotlib', icon: 'fas fa-chart-line', description: 'Plotting and visualization library' },
        { name: 'Seaborn', path: 'Tools/Seaborn', icon: 'fas fa-palette', description: 'Statistical data visualization' },
        { name: 'Plotly', path: 'Tools/Plotly', icon: 'fas fa-chart-bar', description: 'Interactive visualization library' },
        { name: 'Python', path: 'Python', icon: 'fab fa-python', description: 'Programming language guide' },
        { name: 'Java', path: 'Java', icon: 'fab fa-java', description: 'Java programming guide' },
        { name: 'Scala', path: 'Scala', icon: 'fas fa-code', description: 'Scala programming guide' },
        { name: 'dbt', path: 'dbt', icon: 'fas fa-database', description: 'Data Build Tool for analytics engineering' },
    ]
};

// Initialize Mermaid
mermaid.initialize({ 
    startOnLoad: true,
    theme: 'default',
    themeVariables: {
        primaryColor: '#2563eb',
        primaryTextColor: '#fff',
        primaryBorderColor: '#1e40af',
        lineColor: '#4b5563',
        secondaryColor: '#10b981',
        tertiaryColor: '#f59e0b'
    },
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis'
    }
});

// Render technology cards
function renderTechCard(tech) {
    const hasVisual = true; // Assume all have Visual.md
    const hasGuide = true;
    const hasInterview = true;
    
    return `
        <a href="tech-page.html?path=${encodeURIComponent(tech.path)}" class="tech-card">
            <div class="tech-card-header">
                <div class="tech-icon">
                    <i class="${tech.icon}"></i>
                </div>
                <div>
                    <div class="tech-name">${tech.name}</div>
                    <div class="tech-path">${tech.path}</div>
                </div>
            </div>
            <div class="tech-description">${tech.description}</div>
            <div class="tech-badges">
                ${hasVisual ? '<span class="badge visual">Visual</span>' : ''}
                ${hasGuide ? '<span class="badge guide">Guide</span>' : ''}
                ${hasInterview ? '<span class="badge interview">Interview</span>' : ''}
            </div>
        </a>
    `;
}

// Render all technologies
function renderTechnologies() {
    Object.keys(technologies).forEach(category => {
        const grid = document.getElementById(`${category}-grid`);
        if (grid) {
            grid.innerHTML = technologies[category]
                .map(tech => renderTechCard(tech))
                .join('');
        }
    });
    
    // Update total count
    const total = Object.values(technologies).reduce((sum, arr) => sum + arr.length, 0);
    const totalTechsEl = document.getElementById('totalTechs');
    if (totalTechsEl) {
        totalTechsEl.textContent = `${total}+`;
    }
}

// Search and filter functionality
function setupSearchAndFilter() {
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const categoryBlocks = document.querySelectorAll('.category-block');
    const noResults = document.getElementById('noResults');
    
    function filterTechnologies() {
        const searchTerm = searchInput.value.toLowerCase();
        const activeFilter = document.querySelector('.filter-btn.active')?.dataset.filter || 'all';
        let visibleCount = 0;
        
        categoryBlocks.forEach(block => {
            const category = block.dataset.category;
            const grid = block.querySelector('.tech-grid');
            const cards = grid.querySelectorAll('.tech-card');
            let categoryVisible = false;
            
            cards.forEach(card => {
                const name = card.querySelector('.tech-name').textContent.toLowerCase();
                const path = card.querySelector('.tech-path').textContent.toLowerCase();
                const description = card.querySelector('.tech-description').textContent.toLowerCase();
                
                const matchesSearch = name.includes(searchTerm) || 
                                     path.includes(searchTerm) || 
                                     description.includes(searchTerm);
                const matchesFilter = activeFilter === 'all' || category === activeFilter;
                
                if (matchesSearch && matchesFilter) {
                    card.style.display = 'block';
                    categoryVisible = true;
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            if (categoryVisible) {
                block.style.display = 'block';
            } else {
                block.style.display = 'none';
            }
        });
        
        if (visibleCount === 0) {
            noResults.style.display = 'block';
        } else {
            noResults.style.display = 'none';
        }
    }
    
    searchInput.addEventListener('input', filterTechnologies);
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterTechnologies();
        });
    });
}

// Mobile menu toggle
function setupMobileMenu() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    renderTechnologies();
    setupSearchAndFilter();
    setupMobileMenu();
});

