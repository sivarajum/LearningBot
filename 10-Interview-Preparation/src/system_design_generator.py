"""
System Design Interview Preparation
Generates system design walkthroughs for POCs
"""
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SystemDesignQuestion:
    """System design question structure"""
    title: str
    description: str
    requirements: List[str]
    constraints: Dict[str, Any]
    components: List[str]
    scale_estimates: Dict[str, Any]


class SystemDesignGenerator:
    """Generates system design walkthroughs"""
    
    def __init__(self):
        """Initialize system design generator"""
        self.questions: Dict[str, SystemDesignQuestion] = {}
        self._load_default_questions()
    
    def _load_default_questions(self):
        """Load default system design questions"""
        # ML Pipeline Design
        self.questions["ml_pipeline"] = SystemDesignQuestion(
            title="Design a Real-Time ML Pipeline",
            description="Design a system for real-time machine learning predictions at scale",
            requirements=[
                "Handle 1M requests per day",
                "Latency < 100ms for predictions",
                "Support model updates without downtime",
                "Monitor model performance and drift"
            ],
            constraints={
                "storage": "BigQuery",
                "compute": "GCP Vertex AI",
                "serving": "Cloud Run"
            },
            components=[
                "Data Ingestion Layer (Pub/Sub)",
                "Feature Store (BigQuery)",
                "Model Training (Vertex AI)",
                "Model Serving (Vertex AI Endpoints)",
                "API Gateway (Cloud Run)",
                "Monitoring (Cloud Monitoring)"
            ],
            scale_estimates={
                "qps": 12,  # 1M / 86400 seconds
                "data_volume": "100GB/day",
                "model_size": "500MB",
                "replicas": 3
            }
        )
        
        # RAG System Design
        self.questions["rag_system"] = SystemDesignQuestion(
            title="Design a RAG System for Enterprise Documentation",
            description="Build a retrieval-augmented generation system for querying enterprise knowledge",
            requirements=[
                "Support 10M documents",
                "Query latency < 3 seconds",
                "Handle 1000 concurrent users",
                "Maintain document freshness"
            ],
            constraints={
                "vector_db": "Pinecone",
                "llm": "OpenAI GPT-4",
                "embedding": "OpenAI embeddings"
            },
            components=[
                "Document Ingestion Pipeline",
                "Vector Database (Pinecone)",
                "Embedding Service",
                "Retrieval Service",
                "LLM Generation Service",
                "API Gateway",
                "Caching Layer (Redis)"
            ],
            scale_estimates={
                "documents": 10000000,
                "vector_dim": 1536,
                "index_size": "15GB",
                "qps": 100
            }
        )
    
    def generate_walkthrough(self, question_id: str) -> Dict[str, Any]:
        """
        Generate system design walkthrough
        
        Args:
            question_id: Question ID
            
        Returns:
            Complete walkthrough
        """
        if question_id not in self.questions:
            raise ValueError(f"Question {question_id} not found")
        
        question = self.questions[question_id]
        
        walkthrough = {
            "question": question,
            "approach": self._generate_approach(question),
            "architecture": self._generate_architecture(question),
            "scalability": self._generate_scalability(question),
            "tradeoffs": self._generate_tradeoffs(question)
        }
        
        return walkthrough
    
    def _generate_approach(self, question: SystemDesignQuestion) -> List[str]:
        """Generate approach steps"""
        return [
            "1. Clarify requirements and constraints",
            "2. Estimate scale and capacity",
            "3. Design high-level architecture",
            "4. Deep dive into components",
            "5. Discuss scalability and bottlenecks",
            "6. Address tradeoffs and alternatives"
        ]
    
    def _generate_architecture(self, question: SystemDesignQuestion) -> Dict[str, Any]:
        """Generate architecture details"""
        return {
            "components": question.components,
            "data_flow": "Describe how data flows through the system",
            "interactions": "Explain component interactions",
            "technology_stack": question.constraints
        }
    
    def _generate_scalability(self, question: SystemDesignQuestion) -> Dict[str, Any]:
        """Generate scalability considerations"""
        return {
            "horizontal_scaling": "Add more replicas for stateless services",
            "vertical_scaling": "Increase resources for compute-intensive tasks",
            "caching": "Implement Redis for frequently accessed data",
            "database_sharding": "Partition data across multiple shards",
            "load_balancing": "Distribute traffic across instances",
            "estimates": question.scale_estimates
        }
    
    def _generate_tradeoffs(self, question: SystemDesignQuestion) -> List[str]:
        """Generate tradeoffs discussion"""
        return [
            "Consistency vs Availability (CAP theorem)",
            "Latency vs Throughput",
            "Cost vs Performance",
            "Simplicity vs Flexibility"
        ]
    
    def create_custom_question(
        self,
        question_id: str,
        title: str,
        description: str,
        requirements: List[str],
        constraints: Dict[str, Any],
        components: List[str]
    ):
        """
        Create custom system design question
        
        Args:
            question_id: Unique question ID
            title: Question title
            description: Question description
            requirements: List of requirements
            constraints: System constraints
            components: System components
        """
        question = SystemDesignQuestion(
            title=title,
            description=description,
            requirements=requirements,
            constraints=constraints,
            components=components,
            scale_estimates={}
        )
        
        self.questions[question_id] = question
        logger.info(f"Created custom question: {question_id}")


class STARFrameworkHelper:
    """Helper for STAR framework interview responses"""
    
    @staticmethod
    def generate_response(
        situation: str,
        task: str,
        action: str,
        result: str
    ) -> Dict[str, str]:
        """
        Generate STAR framework response
        
        Args:
            situation: Situation description
            task: Task description
            action: Actions taken
            result: Results achieved
            
        Returns:
            STAR response
        """
        return {
            "Situation": situation,
            "Task": task,
            "Action": action,
            "Result": result
        }
    
    @staticmethod
    def get_common_questions() -> List[Dict[str, str]]:
        """Get common behavioral questions"""
        return [
            {
                "question": "Tell me about a time you led a difficult technical decision",
                "category": "Leadership"
            },
            {
                "question": "Describe a situation where you had to learn a new technology quickly",
                "category": "Learning"
            },
            {
                "question": "Give an example of how you handled a conflict in your team",
                "category": "Conflict Resolution"
            },
            {
                "question": "Tell me about a project where you had to work with cross-functional teams",
                "category": "Collaboration"
            }
        ]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    generator = SystemDesignGenerator()
    
    # Generate walkthrough
    walkthrough = generator.generate_walkthrough("ml_pipeline")
    print(f"Question: {walkthrough['question'].title}")
    print(f"Components: {walkthrough['architecture']['components']}")
    
    # STAR framework
    star = STARFrameworkHelper()
    response = star.generate_response(
        situation="Building ML pipeline for customer churn prediction",
        task="Design and implement end-to-end ML system",
        action="Used Vertex AI, BigQuery, FastAPI, MLflow",
        result="Deployed production system with 95% accuracy"
    )
    print(f"\nSTAR Response: {response}")

