#!/usr/bin/env python3
"""
Extended 4K Cheat Sheet Generator for LearningBot
Generates additional specialized cheat sheets
"""

import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 3840, 2160
DPI = 300

COLORS = {
    'bg': '#0F1419',
    'accent1': '#00D9FF',
    'accent2': '#FF6B6B',
    'accent3': '#4ECDC4',
    'accent4': '#FFE66D',
    'accent5': '#95E1D3',
    'accent6': '#FF9FF3',
    'accent7': '#54A0FF',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'card_bg': '#1A1F2E',
    'border': '#2A3F5F',
}

FONTS = {
    'title': 120,
    'section': 80,
    'subsection': 60,
    'body': 50,
    'small': 40,
    'tiny': 32,
}

class ExtendedCheatSheetGenerator:
    def __init__(self, output_dir='4k_cheatsheets'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        try:
            self.fonts = {
                'title': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['title']),
                'section': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['section']),
                'subsection': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['subsection']),
                'body': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['body']),
                'small': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['small']),
                'tiny': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", FONTS['tiny']),
            }
        except:
            self.fonts = {k: ImageFont.load_default() for k in FONTS}
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_gradient_background(self, image, color1, color2):
        pixels = image.load()
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(self._hex_to_rgb(color1)[0] * (1 - ratio) + self._hex_to_rgb(color2)[0] * ratio)
            g = int(self._hex_to_rgb(color1)[1] * (1 - ratio) + self._hex_to_rgb(color2)[1] * ratio)
            b = int(self._hex_to_rgb(color1)[2] * (1 - ratio) + self._hex_to_rgb(color2)[2] * ratio)
            for x in range(WIDTH):
                pixels[x, y] = (r, g, b)
    
    def _draw_rounded_rectangle(self, draw, coords, radius=30, fill=None, outline=None, width=2):
        x1, y1, x2, y2 = coords
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)
        if outline:
            draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
            draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
            draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
            draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)
    
    def _create_cheatsheet(self, title, gradient_colors, accent_color, sections, filename):
        """Generic cheatsheet creator"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        self._create_gradient_background(img, gradient_colors[0], gradient_colors[1])
        draw = ImageDraw.Draw(img)
        
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(accent_color))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], 
                 fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        col_width = WIDTH // 3 - 120
        start_y = 400
        row_height = 780
        
        for idx, section in enumerate(sections):
            col = idx % 3
            row = idx // 3
            x = 80 + col * (WIDTH // 3)
            y = start_y + row * row_height
            
            self._draw_rounded_rectangle(
                draw,
                (x, y, x + col_width, y + 700),
                radius=30,
                fill=self._hex_to_rgb(COLORS['card_bg']),
                outline=self._hex_to_rgb(accent_color),
                width=3
            )
            
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(accent_color))
            
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        footer = f"LearningBot 2026 • {title} Comprehensive Guide • All Rights Reserved"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], 
                 fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / filename
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ {filename}")
        return filepath
    
    def generate_data_engineering(self):
        """Data Engineering & Pipelines cheat sheet"""
        sections = [
            {
                'title': '🔄 DATA PIPELINES',
                'items': [
                    'Apache Airflow: DAG orchestration',
                    'Dataflow: Beam processing',
                    'Dbt: Analytics transformation',
                    'Apache Spark: Distributed compute',
                    'Apache Kafka: Event streaming',
                    'Pub/Sub: Message broker',
                ]
            },
            {
                'title': '📊 DATA WAREHOUSING',
                'items': [
                    'BigQuery: Cloud data warehouse',
                    'Snowflake: Cloud native DW',
                    'Redshift: AWS data warehouse',
                    'Synapse: Azure DW',
                    'ClickHouse: OLAP database',
                    'DuckDB: In-process analytics',
                ]
            },
            {
                'title': '🗄️ DATABASES',
                'items': [
                    'PostgreSQL: RDBMS leader',
                    'MySQL: Web-scale DB',
                    'MongoDB: Document NoSQL',
                    'Cassandra: Wide-column store',
                    'DynamoDB: Serverless NoSQL',
                    'Neo4j: Graph database',
                ]
            },
            {
                'title': '⚡ REAL-TIME PROCESSING',
                'items': [
                    'Spark Streaming: Mini-batch',
                    'Kafka Streams: Stream topology',
                    'Flink: True streaming',
                    'Storm: Distributed streaming',
                    'Cloud Functions: Event-driven',
                    'Pub/Sub Lite: Edge streaming',
                ]
            },
            {
                'title': '🔗 INTEGRATION & ETL',
                'items': [
                    'Fivetran: Pre-built connectors',
                    'Stitch: Cloud ETL platform',
                    'Talend: Enterprise integration',
                    'Apache NiFi: Data routing',
                    'Informatica: Data management',
                    'Zapier: API automation',
                ]
            },
            {
                'title': '📈 MONITORING & QUALITY',
                'items': [
                    'Great Expectations: Data tests',
                    'Soda: Data quality rules',
                    'dbt Tests: Transform validation',
                    'Databand: Pipeline visibility',
                    'Collibra: Data governance',
                    'Apache Atlas: Metadata mgmt',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "DATA ENGINEERING & PIPELINES",
            ('#0F1419', '#1F4E4E'),
            COLORS['accent1'],
            sections,
            "04-Data-Engineering-4K.png"
        )
    
    def generate_feature_engineering(self):
        """Advanced Feature Engineering cheat sheet"""
        sections = [
            {
                'title': '🎯 FEATURE SELECTION',
                'items': [
                    'Univariate Analysis: Single feature',
                    'Mutual Information: Dependency',
                    'Correlation Analysis: Linearity',
                    'VIF: Multicollinearity detection',
                    'Chi-square: Categorical features',
                    'Permutation Importance: Model-based',
                ]
            },
            {
                'title': '🔧 FEATURE TRANSFORMATION',
                'items': [
                    'Scaling: StandardScaler, MinMax',
                    'Normalization: Unit norm vectors',
                    'Log Transform: Skewness reduction',
                    'Box-Cox: Optimal normalization',
                    'Polynomial Features: Higher order',
                    'Interaction Terms: Feature cross',
                ]
            },
            {
                'title': '🎨 FEATURE CREATION',
                'items': [
                    'Binning: Continuous discretization',
                    'One-Hot Encoding: Categorical',
                    'Label Encoding: Ordinal mapping',
                    'Target Encoding: Target mean',
                    'Frequency Encoding: Category freq',
                    'Entity Embeddings: Learned repr',
                ]
            },
            {
                'title': '📅 TIME SERIES FEATURES',
                'items': [
                    'Lag Features: Historical values',
                    'Rolling Statistics: Moving avg',
                    'Seasonal Decomposition: Trend',
                    'Fourier Features: Cyclical patterns',
                    'Date Components: Month, day, hour',
                    'Diff Features: Changes over time',
                ]
            },
            {
                'title': '🚀 DIMENSIONALITY REDUCTION',
                'items': [
                    'PCA: Principal component analysis',
                    'UMAP: Manifold learning',
                    't-SNE: Embedding visualization',
                    'Autoencoders: Neural compression',
                    'LDA: Linear discriminant analysis',
                    'Feature Hashing: Sparse repr',
                ]
            },
            {
                'title': '⚙️ AUTOMATION & TOOLS',
                'items': [
                    'Featuretools: Automated engineering',
                    'tsfresh: Time series features',
                    'AutoFE: Genetic algorithm search',
                    'H2O AutoML: Automatic selection',
                    'SHAP: Feature importance explain',
                    'Optuna: Hyperparameter tuning',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "ADVANCED FEATURE ENGINEERING",
            ('#0F1419', '#4E2F1A'),
            COLORS['accent2'],
            sections,
            "08-Feature-Engineering-4K.png"
        )
    
    def generate_system_design(self):
        """System Design Fundamentals cheat sheet"""
        sections = [
            {
                'title': '🏗️ SYSTEM DESIGN BASICS',
                'items': [
                    'Scalability: Handle growth',
                    'Availability: System uptime',
                    'Reliability: Failure tolerance',
                    'Performance: Latency & throughput',
                    'Consistency: Data accuracy',
                    'Maintainability: Code quality',
                ]
            },
            {
                'title': '🔀 LOAD BALANCING',
                'items': [
                    'Round Robin: Simple distribution',
                    'Least Connections: Active tracking',
                    'IP Hash: Session consistency',
                    'Weighted: Capacity-aware',
                    'Geographic: Location-based',
                    'Dynamic: Real-time adjustments',
                ]
            },
            {
                'title': '💾 CACHING STRATEGIES',
                'items': [
                    'Cache-Aside: Lazy loading',
                    'Write-Through: Consistent writes',
                    'Write-Behind: Async writes',
                    'LRU: Least recently used eviction',
                    'Redis: In-memory store',
                    'Memcached: Distributed cache',
                ]
            },
            {
                'title': '📡 DATABASE SCALING',
                'items': [
                    'Replication: Data redundancy',
                    'Sharding: Horizontal partitioning',
                    'Read Replicas: Scale reads',
                    'Write Replicas: High availability',
                    'CQRS: Separate read/write models',
                    'Event Sourcing: Immutable log',
                ]
            },
            {
                'title': '🔗 API DESIGN',
                'items': [
                    'REST: Resource-oriented',
                    'GraphQL: Flexible queries',
                    'gRPC: High-performance RPC',
                    'Webhooks: Event notifications',
                    'Rate Limiting: Quota protection',
                    'Versioning: API evolution',
                ]
            },
            {
                'title': '🛡️ RESILIENCE PATTERNS',
                'items': [
                    'Circuit Breaker: Failure isolation',
                    'Retry Logic: Transient failures',
                    'Bulkhead: Resource isolation',
                    'Timeout: Deadline enforcement',
                    'Fallback: Graceful degradation',
                    'Health Checks: Continuous monitoring',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "SYSTEM DESIGN FUNDAMENTALS",
            ('#0F1419', '#2F1F4E'),
            COLORS['accent6'],
            sections,
            "09-System-Design-4K.png"
        )
    
    def generate_kubernetes(self):
        """Kubernetes & Container Orchestration cheat sheet"""
        sections = [
            {
                'title': '🐳 KUBERNETES BASICS',
                'items': [
                    'Pods: Smallest deployable unit',
                    'Deployments: Replica management',
                    'Services: Network abstraction',
                    'Ingress: External HTTP routing',
                    'ConfigMaps: Config management',
                    'Secrets: Sensitive data storage',
                ]
            },
            {
                'title': '📦 WORKLOAD TYPES',
                'items': [
                    'Deployments: Stateless apps',
                    'StatefulSets: Stateful apps',
                    'DaemonSets: Node-level tasks',
                    'Jobs: One-time tasks',
                    'CronJobs: Scheduled tasks',
                    'Pods: Direct pod specification',
                ]
            },
            {
                'title': '🔧 CONFIGURATION & STORAGE',
                'items': [
                    'Volumes: Data persistence',
                    'PersistentVolumes: Cluster storage',
                    'StorageClasses: Dynamic provision',
                    'Livenessprobes: Restart policy',
                    'ReadinessProbes: Traffic routing',
                    'Resource Limits: CPU/Memory',
                ]
            },
            {
                'title': '🌐 NETWORKING',
                'items': [
                    'Service Types: ClusterIP, NodePort',
                    'LoadBalancer: External access',
                    'Ingress Controller: Layer 7 routing',
                    'NetworkPolicies: Firewall rules',
                    'Namespaces: Multi-tenancy',
                    'RBAC: Access control',
                ]
            },
            {
                'title': '📊 MONITORING & SCALING',
                'items': [
                    'HPA: Horizontal Pod Autoscaling',
                    'VPA: Vertical Pod Autoscaling',
                    'Prometheus: Metrics collection',
                    'Custom Metrics: App-specific',
                    'Logs: Pod logging aggregation',
                    'Events: Cluster events',
                ]
            },
            {
                'title': '🚀 DEPLOYMENT STRATEGIES',
                'items': [
                    'RollingUpdate: Zero downtime',
                    'Canary: Gradual rollout',
                    'Blue-Green: Parallel versions',
                    'Helm Charts: Package management',
                    'GitOps: Git-driven deployment',
                    'Kustomize: Template customization',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "KUBERNETES & ORCHESTRATION",
            ('#0F1419', '#1A3F4E'),
            COLORS['accent7'],
            sections,
            "10-Kubernetes-4K.png"
        )
    
    def generate_backend_development(self):
        """Backend Development Best Practices cheat sheet"""
        sections = [
            {
                'title': '🏗️ ARCHITECTURE PATTERNS',
                'items': [
                    'MVC: Model-View-Controller',
                    'MVP: Model-View-Presenter',
                    'MVVM: Model-View-ViewModel',
                    'Clean Architecture: Domain-focused',
                    'Microservices: Distributed systems',
                    'Monolithic: Single codebase',
                ]
            },
            {
                'title': '🔐 SECURITY BEST PRACTICES',
                'items': [
                    'Authentication: User verification',
                    'Authorization: Permission checking',
                    'HTTPS/TLS: Encrypted transport',
                    'Input Validation: Injection prevention',
                    'CORS: Cross-origin resource sharing',
                    'CSRF Protection: Request validation',
                ]
            },
            {
                'title': '📝 API DESIGN',
                'items': [
                    'REST Conventions: Consistent APIs',
                    'Status Codes: Proper HTTP codes',
                    'Error Handling: Clear messages',
                    'Pagination: Large datasets',
                    'Filtering/Sorting: Query params',
                    'Documentation: Clear API docs',
                ]
            },
            {
                'title': '⚡ PERFORMANCE OPTIMIZATION',
                'items': [
                    'Connection Pooling: DB efficiency',
                    'Query Optimization: Indexing',
                    'Caching: Reduce compute',
                    'Async Processing: Non-blocking',
                    'Compression: Smaller payloads',
                    'CDN: Edge distribution',
                ]
            },
            {
                'title': '🧪 TESTING STRATEGIES',
                'items': [
                    'Unit Tests: Individual functions',
                    'Integration Tests: Component flow',
                    'E2E Tests: Full workflows',
                    'Load Testing: Scalability checks',
                    'Security Testing: Vulnerability scan',
                    'Chaos Testing: Failure modes',
                ]
            },
            {
                'title': '📊 LOGGING & MONITORING',
                'items': [
                    'Structured Logging: JSON format',
                    'Log Levels: DEBUG to ERROR',
                    'Correlation IDs: Request tracking',
                    'Metrics: Performance indicators',
                    'Distributed Tracing: End-to-end',
                    'Alerts: Proactive notifications',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "BACKEND DEVELOPMENT EXCELLENCE",
            ('#0F1419', '#2F1F1A'),
            COLORS['accent4'],
            sections,
            "11-Backend-Development-4K.png"
        )
    
    def generate_python_mastery(self):
        """Python Best Practices & Advanced Techniques cheat sheet"""
        sections = [
            {
                'title': '🐍 PYTHON FUNDAMENTALS',
                'items': [
                    'List Comprehensions: Concise lists',
                    'Generators: Memory efficient',
                    'Decorators: Function enhancement',
                    'Context Managers: Resource mgmt',
                    'Type Hints: Static typing',
                    'Dataclasses: Structured data',
                ]
            },
            {
                'title': '🔧 ADVANCED TECHNIQUES',
                'items': [
                    'Metaclasses: Class customization',
                    'Descriptors: Property control',
                    'Async/Await: Concurrent code',
                    'Coroutines: Generator functions',
                    'Slots: Memory optimization',
                    'Weak References: GC control',
                ]
            },
            {
                'title': '📦 PACKAGING & DISTRIBUTION',
                'items': [
                    'pip: Package manager',
                    'Poetry: Dependency management',
                    'setuptools: Package creation',
                    'Virtual Environments: Isolation',
                    'PyPI: Package registry',
                    'Build Wheels: Distribution format',
                ]
            },
            {
                'title': '🧪 TESTING FRAMEWORKS',
                'items': [
                    'pytest: Modern test framework',
                    'unittest: Standard library',
                    'Mock: Test isolation',
                    'Hypothesis: Property testing',
                    'Coverage: Code coverage tools',
                    'Tox: Multi-env testing',
                ]
            },
            {
                'title': '🔍 CODE QUALITY',
                'items': [
                    'Black: Code formatter',
                    'Flake8: Style enforcement',
                    'Pylint: Code analysis',
                    'Mypy: Static type checking',
                    'isort: Import sorting',
                    'Bandit: Security scanning',
                ]
            },
            {
                'title': '🎯 PERFORMANCE',
                'items': [
                    'Profiling: Identify bottlenecks',
                    'Cython: C extensions',
                    'NumPy: Vectorized operations',
                    'Pandas: Data manipulation',
                    'Multiprocessing: Parallelization',
                    'Numba: JIT compilation',
                ]
            }
        ]
        
        return self._create_cheatsheet(
            "PYTHON MASTERY & BEST PRACTICES",
            ('#0F1419', '#1F2F4E'),
            COLORS['accent3'],
            sections,
            "12-Python-Mastery-4K.png"
        )
    
    def generate_all(self):
        """Generate all extended cheat sheets"""
        print("\n🚀 Extended 4K Cheat Sheet Generation...\n")
        print(f"📍 Output Directory: {self.output_dir.absolute()}\n")
        
        files_generated = []
        
        print("📋 Generating Extended Cheat Sheets:")
        print("─" * 50)
        
        files_generated.append(self.generate_data_engineering())
        files_generated.append(self.generate_feature_engineering())
        files_generated.append(self.generate_system_design())
        files_generated.append(self.generate_kubernetes())
        files_generated.append(self.generate_backend_development())
        files_generated.append(self.generate_python_mastery())
        
        print("─" * 50)
        print(f"\n✅ Generated {len(files_generated)} additional 4K cheat sheets!")
        print(f"\n📊 Image Specifications:")
        print(f"   • Resolution: 3840x2160 (4K)")
        print(f"   • DPI: 300 (Print quality)")
        print(f"   • Format: PNG")
        print(f"\n💾 Total files in output directory:\n")
        
        for f in sorted(self.output_dir.glob('*.png')):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  ✓ {f.name} ({size_mb:.1f} MB)")
        
        return files_generated


if __name__ == '__main__':
    generator = ExtendedCheatSheetGenerator(output_dir='4k_cheatsheets')
    files = generator.generate_all()
    print(f"\n🎉 All extended 4K cheat sheets generated successfully!\n")
