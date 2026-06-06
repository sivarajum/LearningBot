#!/usr/bin/env python3
"""
TechStack & Specialized 4K Cheat Sheet Generator
Generates professional cheat sheets for all TechStack categories
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

WIDTH, HEIGHT = 3840, 2160

COLORS = {
    'bg': '#0F1419',
    'accent_gcp': '#4285F4',
    'accent_aws': '#FF9900',
    'accent_azure': '#0078D4',
    'accent_bigquery': '#669DF6',
    'accent_spark': '#E25A1C',
    'accent_kafka': '#000000',
    'accent_docker': '#2496ED',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'card_bg': '#1A1F2E',
}

FONTS = {
    'title': 120, 'section': 80, 'subsection': 60, 'body': 50, 'small': 40, 'tiny': 32,
}

class TechStackCheatSheetGenerator:
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
        
        footer = f"LearningBot 2026 • {title} Complete Guide • Professional Reference"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], 
                 fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / filename
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ {filename}")
        return filepath
    
    def generate_bigquery(self):
        """BigQuery comprehensive cheat sheet"""
        sections = [
            {'title': '📊 CORE CONCEPTS',
             'items': ['Datasets: Data containers', 'Tables: Data storage', 'Views: Virtual tables',
                      'Queries: SQL analysis', 'Clustering: Data organization', 'Partitioning: Time-based']},
            {'title': '🔧 QUERY OPTIMIZATION',
             'items': ['Use column selection', 'Partition pruning: Filter early', 'Clustering: Related data',
                      'Denormalization: Join reduction', 'Approximate aggregations', 'Caching: Query results']},
            {'title': '💰 COST OPTIMIZATION',
             'items': ['Slots: Predictable costs', 'Flex Slots: On-demand', 'Reserved capacity',
                      'Query estimation', 'Storage optimization', 'Deletion policies: Auto-expire']},
            {'title': '🔒 SECURITY & IAM',
             'items': ['Dataset-level access', 'Column-level security', 'Row-level security (preview)',
                      'Encryption: CMEK support', 'Service accounts', 'VPC Service Controls']},
            {'title': '📈 ADVANCED FEATURES',
             'items': ['BigQuery ML: In-database ML', 'Federated queries: External data',
                      'Stored procedures: Logic encapsulation', 'BI Engine: In-memory cache',
                      'GIS functions: Geographic analysis', 'Time-series analysis']},
            {'title': '🚀 INTEGRATION & TOOLS',
             'items': ['Dataflow: Stream/batch', 'Pub/Sub: Real-time', 'Cloud Functions: Triggers',
                      'Looker: Dashboarding', 'Sheets: Direct access', 'Python/Java SDKs']}
        ]
        return self._create_cheatsheet("BIGQUERY MASTERY", ('#0F1419', '#2F3F5E'),
                                       COLORS['accent_bigquery'], sections, "TECHSTACK-BigQuery-4K.png")
    
    def generate_gcp(self):
        """Google Cloud Platform comprehensive cheat sheet"""
        sections = [
            {'title': '☁️ COMPUTE SERVICES',
             'items': ['Compute Engine: IaaS VMs', 'App Engine: Managed PaaS', 'Cloud Run: Serverless',
                      'GKE: Kubernetes managed', 'Cloud Functions: FaaS', 'Cloud Workflows: Orchestration']},
            {'title': '💾 STORAGE & DATA',
             'items': ['Cloud Storage: Object storage', 'Cloud SQL: Managed RDBMS', 'Firestore: NoSQL',
                      'BigQuery: Data warehouse', 'Datastore: Document DB', 'Memorystore: Redis/Memcached']},
            {'title': '🧠 AI & ML SERVICES',
             'items': ['Vertex AI: Unified ML platform', 'AutoML: No-code ML', 'BigQuery ML: In-database',
                      'Vertex Search: Semantic search', 'Document AI: Form processing', 'Vision AI: Images']},
            {'title': '🔌 INTEGRATION & MESSAGING',
             'items': ['Pub/Sub: Messaging', 'Cloud Tasks: Queuing', 'Workflows: Process orchestration',
                      'API Gateway: API management', 'Service Directory: Service registry', 'Event Arc: Events']},
            {'title': '🔐 SECURITY & IDENTITY',
             'items': ['IAM: Access control', 'Service Accounts: Machine identity', 'Cloud KMS: Key mgmt',
                      'Secret Manager: Secrets', 'VPC: Network isolation', 'Cloud Armor: DDoS protection']},
            {'title': '📊 MONITORING & OPERATIONS',
             'items': ['Cloud Logging: Log aggregation', 'Cloud Monitoring: Metrics', 'Cloud Trace: Tracing',
                      'Cloud Debugger: Debug production', 'Cloud Profiler: Performance', 'Error Reporting: Errors']}
        ]
        return self._create_cheatsheet("GOOGLE CLOUD PLATFORM (GCP)", ('#0F1419', '#1F2F4E'),
                                       COLORS['accent_gcp'], sections, "TECHSTACK-GCP-4K.png")
    
    def generate_aws(self):
        """Amazon Web Services comprehensive cheat sheet"""
        sections = [
            {'title': '🖥️ COMPUTE SERVICES',
             'items': ['EC2: Virtual machines', 'Lambda: Serverless', 'ECS: Container orchestration',
                      'EKS: Kubernetes managed', 'Fargate: Serverless containers', 'Elastic Beanstalk: PaaS']},
            {'title': '💾 STORAGE & DATABASES',
             'items': ['S3: Object storage', 'EBS: Block storage', 'EFS: File storage',
                      'RDS: Managed RDBMS', 'DynamoDB: NoSQL', 'ElastiCache: In-memory cache']},
            {'title': '📊 DATA & ANALYTICS',
             'items': ['Redshift: Data warehouse', 'Athena: S3 query', 'EMR: Hadoop/Spark',
                      'Glue: ETL service', 'Kinesis: Streaming', 'QuickSight: BI dashboards']},
            {'title': '🧠 ML & AI SERVICES',
             'items': ['SageMaker: ML platform', 'Forecast: Time series', 'Lookout: Anomaly detection',
                      'Textract: Document processing', 'Rekognition: Image/video analysis', 'Lex: Chatbots']},
            {'title': '🔒 SECURITY & COMPLIANCE',
             'items': ['IAM: Access control', 'KMS: Key management', 'Secrets Manager: Secrets',
                      'VPC: Network isolation', 'WAF: Web firewall', 'Shield: DDoS protection']},
            {'title': '📡 NETWORKING & DELIVERY',
             'items': ['CloudFront: CDN', 'Route 53: DNS', 'ELB/ALB/NLB: Load balancers',
                      'VPN: Secure connection', 'DirectConnect: Dedicated connection', 'API Gateway: API management']}
        ]
        return self._create_cheatsheet("AMAZON WEB SERVICES (AWS)", ('#0F1419', '#2F1F1A'),
                                       COLORS['accent_aws'], sections, "TECHSTACK-AWS-4K.png")
    
    def generate_spark(self):
        """Apache Spark comprehensive cheat sheet"""
        sections = [
            {'title': '⚡ SPARK BASICS',
             'items': ['RDD: Immutable collections', 'DataFrame: Structured data', 'Dataset: Type-safe',
                      'SQL: Query interface', 'MLlib: Machine learning', 'GraphX: Graph processing']},
            {'title': '🔄 CORE OPERATIONS',
             'items': ['Transformations: map, filter, join', 'Actions: collect, count, save',
                      'Shuffles: Data movement', 'Caching: Data persistence', 'Broadcasting: Shared vars',
                      'Accumulators: Shared counters']},
            {'title': '🧠 SPARK ML',
             'items': ['Pipelines: ML workflows', 'Transformers: Feature engineering', 'Estimators: Model training',
                      'Evaluators: Model assessment', 'CrossValidator: Hyperparameter tuning', 'Feature scaling: Normalization']},
            {'title': '📊 STRUCTURED STREAMING',
             'items': ['Micro-batching: Processing model', 'Streaming DataFrames', 'Event-time semantics',
                      'Windowed aggregations', 'Watermarking: Late data handling', 'Output modes: Complete/Update/Append']},
            {'title': '⚙️ PERFORMANCE TUNING',
             'items': ['Partitioning: Data distribution', 'Clustering: Data locality', 'Serialization: Data format',
                      'Memory tuning: Executor config', 'Shuffle optimization', 'Broadcast join threshold']},
            {'title': '🚀 DEPLOYMENT & EXECUTION',
             'items': ['Local mode: Development', 'Standalone: Spark cluster', 'YARN: Hadoop integration',
                      'Kubernetes: Container orchestration', 'Mesos: Distributed scheduler', 'Databricks: Managed service']}
        ]
        return self._create_cheatsheet("APACHE SPARK MASTERY", ('#0F1419', '#3F1F1A'),
                                       COLORS['accent_spark'], sections, "TECHSTACK-Spark-4K.png")
    
    def generate_kafka(self):
        """Apache Kafka comprehensive cheat sheet"""
        sections = [
            {'title': '📨 KAFKA FUNDAMENTALS',
             'items': ['Topics: Message categories', 'Partitions: Parallel processing', 'Brokers: Kafka servers',
                      'Producers: Message senders', 'Consumers: Message readers', 'ZooKeeper: Cluster coordination']},
            {'title': '🔄 PRODUCER & CONSUMER',
             'items': ['Key-based partitioning', 'Acks: Durability levels', 'Retries: Failure handling',
                      'Batching: Performance optimization', 'Compression: Data reduction', 'Consumer groups: Scaling']},
            {'title': '📊 STREAM PROCESSING',
             'items': ['Kafka Streams: Topology building', 'StatelessOperations: Transform data', 'Stateful: Aggregations',
                      'Interactive Queries: State store access', 'Exactly-once Semantics', 'Windowing: Time aggregations']},
            {'title': '🔒 SECURITY & RELIABILITY',
             'items': ['TLS/SSL: Encryption', 'SASL: Authentication', 'ACLs: Access control',
                      'Replication: Data redundancy', 'ISR: In-sync replicas', 'Min ISR: Durability guarantee']},
            {'title': '📈 OPERATIONS & MONITORING',
             'items': ['Broker metrics: Performance', 'Consumer lag: Backpressure', 'Offset management',
                      'Health checks: Cluster status', 'Log compaction: Retention policy', 'Garbage collection: Tuning']},
            {'title': '🛠️ DEPLOYMENT & TOOLS',
             'items': ['Confluent Platform: Enterprise', 'Kafka Connect: Integration', 'Schema Registry: Data validation',
                      'Control Center: Management UI', 'KafkaSQL: KSQL streaming', 'Docker: Containerization']}
        ]
        return self._create_cheatsheet("APACHE KAFKA MASTERY", ('#0F1419', '#1F1F1F'),
                                       COLORS['accent_kafka'], sections, "TECHSTACK-Kafka-4K.png")
    
    def generate_docker(self):
        """Docker & Container Technology cheat sheet"""
        sections = [
            {'title': '🐳 DOCKER BASICS',
             'items': ['Images: Blueprints', 'Containers: Running instances', 'Dockerfile: Image definition',
                      'Registries: Image storage', 'Tags: Version management', 'Layers: Image composition']},
            {'title': '🔧 DOCKERFILE BEST PRACTICES',
             'items': ['Multi-stage builds: Size reduction', 'Layer caching: Build speed', 'Alpine: Minimal images',
                      'Non-root users: Security', 'Health checks: Liveness probes', 'Signals: Graceful shutdown']},
            {'title': '🌐 NETWORKING',
             'items': ['Bridge networks: Inter-container', 'Host network: Direct access', 'Overlay: Swarm networks',
                      'DNS: Service discovery', 'Port mapping: Expose services', 'Network policies: Isolation']},
            {'title': '💾 STORAGE & VOLUMES',
             'items': ['Volumes: Persistent data', 'Bind mounts: Host directory', 'tmpfs: Memory mounts',
                      'Volume drivers: Custom storage', 'Named volumes: Management', 'Volume sharing: Multi-container']},
            {'title': '🔍 MONITORING & DEBUGGING',
             'items': ['Logs: Container output', 'Stats: Resource usage', 'Inspect: Configuration details',
                      'Exec: Interactive debugging', 'Attach: Live output', 'Kill signals: Process termination']},
            {'title': '🚀 ADVANCED FEATURES',
             'items': ['Docker Compose: Multi-container', 'Docker Swarm: Orchestration', 'BuildKit: Build engine',
                      'Docker Desktop: Development', 'Content Trust: Image signing', 'Scan: Vulnerability detection']}
        ]
        return self._create_cheatsheet("DOCKER & CONTAINERIZATION", ('#0F1419', '#1F2F4E'),
                                       COLORS['accent_docker'], sections, "TECHSTACK-Docker-4K.png")
    
    def generate_all(self):
        """Generate all TechStack cheat sheets"""
        print("\n🚀 TechStack 4K Cheat Sheet Generation...\n")
        print("📋 Generating TechStack Cheat Sheets:")
        print("─" * 50)
        
        self.generate_bigquery()
        self.generate_gcp()
        self.generate_aws()
        self.generate_spark()
        self.generate_kafka()
        self.generate_docker()
        
        print("─" * 50)
        print(f"\n✅ Generated 6 TechStack 4K cheat sheets!")
        print(f"\n💾 All files in output directory:\n")
        
        total_size = 0
        for f in sorted(self.output_dir.glob('*.png')):
            size_mb = f.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"  ✓ {f.name} ({size_mb:.1f} MB)")
        
        print(f"\nTotal Size: {total_size:.1f} MB")
        print(f"Total Files: {len(list(self.output_dir.glob('*.png')))}")


if __name__ == '__main__':
    generator = TechStackCheatSheetGenerator(output_dir='4k_cheatsheets')
    generator.generate_all()
    print(f"\n🎉 All TechStack cheat sheets generated successfully!\n")
