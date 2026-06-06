#!/usr/bin/env python3
"""
4K Cheat Sheet Generator for LearningBot Sections
Generates professional 4K (3840x2160) PNG images for all learning sections
"""

import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json

# 4K Resolution
WIDTH, HEIGHT = 3840, 2160
DPI = 300

# Color Scheme - Professional with gradients support
COLORS = {
    'bg': '#0F1419',
    'accent1': '#00D9FF',  # Cyan
    'accent2': '#FF6B6B',  # Red
    'accent3': '#4ECDC4',  # Teal
    'accent4': '#FFE66D',  # Yellow
    'accent5': '#95E1D3',  # Mint
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'card_bg': '#1A1F2E',
    'border': '#2A3F5F',
}

# Font sizes for 4K (scale up from standard)
FONTS = {
    'title': 120,
    'section': 80,
    'subsection': 60,
    'body': 50,
    'small': 40,
    'tiny': 32,
}

class CheatSheetGenerator:
    def __init__(self, output_dir='4k_cheatsheets'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Try to load system fonts, fall back to default
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
            # Fallback to default font
            self.fonts = {k: ImageFont.load_default() for k in FONTS}
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_gradient_background(self, image, color1, color2):
        """Create a gradient background"""
        pixels = image.load()
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(self._hex_to_rgb(color1)[0] * (1 - ratio) + self._hex_to_rgb(color2)[0] * ratio)
            g = int(self._hex_to_rgb(color1)[1] * (1 - ratio) + self._hex_to_rgb(color2)[1] * ratio)
            b = int(self._hex_to_rgb(color1)[2] * (1 - ratio) + self._hex_to_rgb(color2)[2] * ratio)
            for x in range(WIDTH):
                pixels[x, y] = (r, g, b)
    
    def _draw_rounded_rectangle(self, draw, coords, radius=30, fill=None, outline=None, width=2):
        """Draw a rounded rectangle"""
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
    
    def _add_text_wrapped(self, draw, text, xy, max_width, font, fill, line_spacing=20):
        """Add wrapped text with proper line spacing"""
        x, y = xy
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        current_y = y
        for line in lines:
            draw.text((x, current_y), line, font=font, fill=fill)
            current_y += line_spacing
        
        return current_y
    
    def generate_ml_fundamentals(self):
        """Generate ML Fundamentals cheat sheet"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        draw = ImageDraw.Draw(img)
        
        # Create gradient background
        self._create_gradient_background(img, '#0F1419', '#1A2F4E')
        draw = ImageDraw.Draw(img)
        
        # Title
        title = "ML FUNDAMENTALS"
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(COLORS['accent1']))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        # Content sections in 3 columns
        sections = [
            {
                'title': '🎯 CORE CONCEPTS',
                'items': [
                    'Supervised Learning: Classification, Regression',
                    'Unsupervised Learning: Clustering, Dimensionality',
                    'Reinforcement Learning: Agents, Rewards',
                    'Feature Engineering: Scaling, Encoding',
                    'Model Evaluation: Accuracy, Precision, Recall',
                    'Cross-Validation: K-fold, Stratified',
                ]
            },
            {
                'title': '🔧 KEY ALGORITHMS',
                'items': [
                    'Linear & Logistic Regression',
                    'Decision Trees & Random Forests',
                    'Support Vector Machines (SVM)',
                    'K-Means & Hierarchical Clustering',
                    'Neural Networks & Deep Learning',
                    'Naive Bayes & KNN',
                ]
            },
            {
                'title': '📊 BEST PRACTICES',
                'items': [
                    'Understand your data first',
                    'Handle missing values appropriately',
                    'Avoid data leakage',
                    'Hyperparameter tuning systematically',
                    'Monitor for overfitting/underfitting',
                    'Document experiments thoroughly',
                ]
            },
            {
                'title': '⚙️ WORKFLOW',
                'items': [
                    '1. Problem Definition',
                    '2. Data Collection & Cleaning',
                    '3. Exploratory Data Analysis',
                    '4. Feature Engineering',
                    '5. Model Training & Evaluation',
                    '6. Hyperparameter Tuning & Deployment',
                ]
            },
            {
                'title': '🚫 COMMON PITFALLS',
                'items': [
                    'Using entire dataset for tuning',
                    'Ignoring class imbalance',
                    'Not scaling features',
                    'Overfitting to training data',
                    'Ignoring domain expertise',
                    'Poor baseline comparisons',
                ]
            },
            {
                'title': '📈 PERFORMANCE METRICS',
                'items': [
                    'Classification: Accuracy, F1-Score, ROC-AUC',
                    'Regression: MSE, RMSE, R-squared',
                    'Clustering: Silhouette, Davies-Bouldin',
                    'Business Metrics: ROI, Throughput',
                    'Speed: Latency, Inference Time',
                    'Resources: Memory, CPU Usage',
                ]
            }
        ]
        
        # Draw sections in grid (3 columns, 2 rows)
        col_width = WIDTH // 3 - 120
        start_y = 400
        row_height = 780
        
        for idx, section in enumerate(sections):
            col = idx % 3
            row = idx // 3
            x = 80 + col * (WIDTH // 3)
            y = start_y + row * row_height
            
            # Card background
            self._draw_rounded_rectangle(
                draw,
                (x, y, x + col_width, y + 700),
                radius=30,
                fill=self._hex_to_rgb(COLORS['card_bg']),
                outline=self._hex_to_rgb(COLORS['accent1']),
                width=3
            )
            
            # Section title
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(COLORS['accent1']))
            
            # Items
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        # Footer
        footer = "LearningBot 2026 • Comprehensive ML Fundamentals Guide • For Full Details Visit LearningBot Documentation"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / "01-ML-Fundamentals-4K.png"
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_cloud_ai_platform(self):
        """Generate Cloud AI Platform cheat sheet"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        
        self._create_gradient_background(img, '#0F1419', '#1F3A5F')
        draw = ImageDraw.Draw(img)
        
        # Title
        title = "CLOUD AI PLATFORM & VERTEX AI"
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(COLORS['accent2']))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        sections = [
            {
                'title': '☁️ VERTEX AI SERVICES',
                'items': [
                    'AutoML: AutoML Vision, NLP, Tabular',
                    'Workbench: Jupyter notebooks, IDEs',
                    'Model Registry: Version & Lineage tracking',
                    'Pipelines: ML workflow orchestration',
                    'Explainable AI: Feature importance analysis',
                    'Model Monitoring: Production performance',
                ]
            },
            {
                'title': '🧠 GENERATIVE AI',
                'items': [
                    'PaLM API: Text & Embedding generation',
                    'Imagen: AI image generation service',
                    'Text-to-Speech: Neural TTS synthesis',
                    'Speech-to-Text: Audio transcription',
                    'Translation API: 100+ languages',
                    'Document AI: Form/invoice processing',
                ]
            },
            {
                'title': '📊 DATA & ANALYTICS',
                'items': [
                    'BigQuery: Serverless data warehouse',
                    'Dataflow: Apache Beam processing',
                    'Pub/Sub: Message queuing',
                    'Dataproc: Managed Spark clusters',
                    'Cloud SQL: Managed databases',
                    'Firestore: NoSQL document DB',
                ]
            },
            {
                'title': '🚀 DEPLOYMENT OPTIONS',
                'items': [
                    'Cloud Run: Serverless containers',
                    'App Engine: Fully managed PaaS',
                    'GKE: Kubernetes orchestration',
                    'Compute Engine: VMs',
                    'Cloud Functions: FaaS',
                    'AI Platform Predictions: Model serving',
                ]
            },
            {
                'title': '🔒 SECURITY & COMPLIANCE',
                'items': [
                    'IAM: Identity & Access Management',
                    'VPC Service Controls: Network security',
                    'Cloud KMS: Key management',
                    'Data Loss Prevention: Sensitive data',
                    'HIPAA, GDPR compliant',
                    'Audit Logging: Full compliance trail',
                ]
            },
            {
                'title': '💰 COST OPTIMIZATION',
                'items': [
                    'Committed Use Discounts',
                    'Auto-scaling: Only pay for usage',
                    'Spot Instances: Up to 90% savings',
                    'BigQuery Slots: Predictable costs',
                    'Reserved Instances: Long-term',
                    'Budget Alerts: Cost monitoring',
                ]
            }
        ]
        
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
                outline=self._hex_to_rgb(COLORS['accent2']),
                width=3
            )
            
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(COLORS['accent2']))
            
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        footer = "LearningBot 2026 • Cloud AI Platform & Vertex AI Comprehensive Guide"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / "02-Cloud-AI-Platform-4K.png"
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_llm_essentials(self):
        """Generate LLM Essentials cheat sheet"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        
        self._create_gradient_background(img, '#0F1419', '#2F1A4E')
        draw = ImageDraw.Draw(img)
        
        title = "LLM ESSENTIALS & TRANSFORMERS"
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(COLORS['accent3']))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        sections = [
            {
                'title': '🤖 TRANSFORMER ARCHITECTURE',
                'items': [
                    'Attention Mechanism: Self-attention',
                    'Multi-Head Attention: Parallel heads',
                    'Positional Encoding: Position info',
                    'Feed-Forward Networks: Non-linear layers',
                    'Layer Normalization: Gradient stability',
                    'Residual Connections: Skip connections',
                ]
            },
            {
                'title': '📚 POPULAR LLM MODELS',
                'items': [
                    'GPT Series: OpenAI autoregressive',
                    'BERT: Bidirectional encoder',
                    'T5: Text-to-Text Transfer',
                    'LLaMA: Meta open models',
                    'PaLM: Google dense models',
                    'Claude: Anthropic trained models',
                ]
            },
            {
                'title': '🎓 TRAINING TECHNIQUES',
                'items': [
                    'Pre-training: Unsupervised learning',
                    'Fine-tuning: Task-specific training',
                    'Prompt Engineering: Effective prompts',
                    'Few-Shot Learning: In-context examples',
                    'Reinforcement Learning from Human Feedback',
                    'Instruction Tuning: Follow instructions',
                ]
            },
            {
                'title': '⚡ OPTIMIZATION & INFERENCE',
                'items': [
                    'Quantization: 8/4-bit precision',
                    'Knowledge Distillation: Smaller models',
                    'Flash Attention: Faster computation',
                    'Speculative Decoding: Token prediction',
                    'KV Cache Optimization: Memory',
                    'Batch Processing: Throughput',
                ]
            },
            {
                'title': '🛡️ SAFETY & ALIGNMENT',
                'items': [
                    'Bias Detection: Fairness metrics',
                    'Hallucination Prevention: Fact-checking',
                    'Jailbreak Prevention: Robustness',
                    'Content Filtering: Harmful outputs',
                    'Output Moderation: Policy compliance',
                    'Watermarking: Authenticity',
                ]
            },
            {
                'title': '📊 EVALUATION METRICS',
                'items': [
                    'BLEU: Translation quality',
                    'ROUGE: Summary similarity',
                    'Perplexity: Language modeling',
                    'Human Evaluation: Quality assessment',
                    'MMLU: Multi-task accuracy',
                    'HumanEval: Code generation',
                ]
            }
        ]
        
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
                outline=self._hex_to_rgb(COLORS['accent3']),
                width=3
            )
            
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(COLORS['accent3']))
            
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        footer = "LearningBot 2026 • LLM Essentials & Transformers Architecture Guide"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / "03-LLM-Essentials-4K.png"
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_rag_essentials(self):
        """Generate RAG Essentials cheat sheet"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        
        self._create_gradient_background(img, '#0F1419', '#4E1F2E')
        draw = ImageDraw.Draw(img)
        
        title = "RETRIEVAL AUGMENTED GENERATION (RAG)"
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(COLORS['accent4']))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        sections = [
            {
                'title': '🎯 RAG ARCHITECTURE',
                'items': [
                    'Retriever: Document search & ranking',
                    'Indexer: Vector DB storage',
                    'Generator: LLM context augmentation',
                    'Re-ranker: Relevance refinement',
                    'Query Expansion: Multiple queries',
                    'Fusion: Ensemble retrieval',
                ]
            },
            {
                'title': '🔍 RETRIEVAL METHODS',
                'items': [
                    'Semantic Search: Vector similarity',
                    'Dense Retrieval: Learned representations',
                    'Sparse Retrieval: BM25 keyword match',
                    'Hybrid Retrieval: Combine both',
                    'Knowledge Graph: Entity relationships',
                    'Multi-hop: Complex reasoning',
                ]
            },
            {
                'title': '📦 VECTOR DATABASES',
                'items': [
                    'Pinecone: Managed vector DB',
                    'Weaviate: Open-source vector DB',
                    'Milvus: Scalable vector search',
                    'Chroma: Embeddings database',
                    'FAISS: Facebook AI similarity',
                    'Qdrant: Vector similarity engine',
                ]
            },
            {
                'title': '🧠 EMBEDDING MODELS',
                'items': [
                    'OpenAI: text-embedding-3-large',
                    'Google: text-embedding-004',
                    'Cohere: Embed API v3',
                    'Sentence-BERT: Open-source models',
                    'BGE: Alibaba embedding models',
                    'E5: ELEuthER embedding models',
                ]
            },
            {
                'title': '⚙️ RAG PIPELINE STEPS',
                'items': [
                    '1. Document Ingestion & Chunking',
                    '2. Embedding Generation',
                    '3. Vector Indexing',
                    '4. Query Processing & Search',
                    '5. Re-ranking & Filtering',
                    '6. LLM Generation with Context',
                ]
            },
            {
                'title': '📊 OPTIMIZATION & EVAL',
                'items': [
                    'Chunk Size Tuning: 256-1024 tokens',
                    'Retrieval Recall: Hit rate metrics',
                    'Latency Optimization: <100ms target',
                    'Relevance Scoring: NDCG metrics',
                    'User Feedback Loop: Continuous improve',
                    'A/B Testing: Multiple strategies',
                ]
            }
        ]
        
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
                outline=self._hex_to_rgb(COLORS['accent4']),
                width=3
            )
            
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(COLORS['accent4']))
            
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        footer = "LearningBot 2026 • Retrieval Augmented Generation (RAG) Comprehensive Guide"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / "05-RAG-Essentials-4K.png"
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_mlops_automation(self):
        """Generate MLOps Automation cheat sheet"""
        img = Image.new('RGB', (WIDTH, HEIGHT), self._hex_to_rgb(COLORS['bg']))
        
        self._create_gradient_background(img, '#0F1419', '#1F4E2F')
        draw = ImageDraw.Draw(img)
        
        title = "MLOPS & AUTOMATION"
        draw.text((100, 80), title, font=self.fonts['title'], fill=self._hex_to_rgb(COLORS['accent5']))
        draw.text((100, 220), datetime.now().strftime("%B %d, %Y"), font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        sections = [
            {
                'title': '🔄 CI/CD PIPELINES',
                'items': [
                    'GitHub Actions: Workflow automation',
                    'Jenkins: Build & deployment',
                    'GitLab CI: Integrated pipeline',
                    'Cloud Build: GCP build service',
                    'ArgoCD: GitOps deployment',
                    'Tekton: Cloud-native pipeline',
                ]
            },
            {
                'title': '🧪 TESTING & VALIDATION',
                'items': [
                    'Unit Tests: Code functionality',
                    'Integration Tests: Component flow',
                    'Model Tests: Accuracy/performance',
                    'Data Tests: Quality & drift',
                    'Contract Tests: API compatibility',
                    'Load Tests: Scalability checks',
                ]
            },
            {
                'title': '📊 MONITORING & LOGGING',
                'items': [
                    'Prometheus: Metrics collection',
                    'Grafana: Visualization dashboards',
                    'ELK Stack: Centralized logging',
                    'Datadog: APM & monitoring',
                    'New Relic: Application insights',
                    'CloudTrace: Distributed tracing',
                ]
            },
            {
                'title': '🚀 DEPLOYMENT STRATEGIES',
                'items': [
                    'Blue-Green: Zero-downtime deploy',
                    'Canary: Gradual rollout',
                    'Rolling: Sequential updates',
                    'Shadow: Parallel testing',
                    'Feature Flags: Runtime control',
                    'A/B Testing: User experimentation',
                ]
            },
            {
                'title': '🛠️ INFRASTRUCTURE AS CODE',
                'items': [
                    'Terraform: HCL infrastructure',
                    'Ansible: Configuration management',
                    'Docker: Container images',
                    'Kubernetes: Orchestration',
                    'Helm: K8s package manager',
                    'Pulumi: IaC SDK approach',
                ]
            },
            {
                'title': '📈 PERFORMANCE TUNING',
                'items': [
                    'Model Optimization: Quantization',
                    'Batch Inference: Throughput',
                    'Caching: Reduce latency',
                    'Async Processing: Non-blocking',
                    'Resource Scaling: Auto-scale',
                    'Cost Optimization: Efficient',
                ]
            }
        ]
        
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
                outline=self._hex_to_rgb(COLORS['accent5']),
                width=3
            )
            
            draw.text((x + 30, y + 30), section['title'], font=self.fonts['subsection'], 
                     fill=self._hex_to_rgb(COLORS['accent5']))
            
            item_y = y + 120
            for item in section['items']:
                draw.text((x + 30, item_y), f"• {item}", font=self.fonts['small'], 
                         fill=self._hex_to_rgb(COLORS['text_primary']))
                item_y += 85
        
        footer = "LearningBot 2026 • MLOps & Automation Excellence Guide"
        draw.text((100, HEIGHT - 100), footer, font=self.fonts['tiny'], fill=self._hex_to_rgb(COLORS['text_secondary']))
        
        filepath = self.output_dir / "06-MLOps-Automation-4K.png"
        img.save(filepath, 'PNG', quality=95)
        print(f"✓ Generated: {filepath}")
        return filepath
    
    def generate_all(self):
        """Generate all cheat sheets"""
        print("\n🚀 Starting 4K Cheat Sheet Generation...\n")
        print(f"📍 Output Directory: {self.output_dir.absolute()}\n")
        
        files_generated = []
        
        print("📋 Generating Cheat Sheets:")
        print("─" * 50)
        
        files_generated.append(self.generate_ml_fundamentals())
        files_generated.append(self.generate_cloud_ai_platform())
        files_generated.append(self.generate_llm_essentials())
        files_generated.append(self.generate_rag_essentials())
        files_generated.append(self.generate_mlops_automation())
        
        print("─" * 50)
        print(f"\n✅ Generated {len(files_generated)} 4K cheat sheets!")
        print(f"\n📊 Image Specifications:")
        print(f"   • Resolution: 3840x2160 (4K)")
        print(f"   • DPI: 300 (Print quality)")
        print(f"   • Format: PNG")
        print(f"   • Color Space: RGB")
        print(f"\n💾 Files saved to: {self.output_dir.absolute()}\n")
        
        return files_generated


if __name__ == '__main__':
    generator = CheatSheetGenerator(output_dir='4k_cheatsheets')
    files = generator.generate_all()
    
    print("\n🎉 All 4K cheat sheets generated successfully!")
    print(f"\nFiles created:")
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  ✓ {f.name} ({size_mb:.1f} MB)")
