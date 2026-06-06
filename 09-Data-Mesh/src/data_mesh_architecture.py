"""
Data Mesh Architecture Implementation
Decentralized data architecture patterns
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DataProduct:
    """Data product definition"""
    name: str
    domain: str
    owner: str
    schema: Dict[str, Any]
    access_policy: str
    quality_metrics: Dict[str, float]
    version: str = "1.0.0"
    created_at: Optional[datetime] = None


@dataclass
class DataDomain:
    """Data domain definition"""
    name: str
    owner: str
    data_products: List[DataProduct]
    governance_policy: str
    access_control: Dict[str, List[str]]


class DataMeshArchitecture:
    """Data Mesh architecture implementation"""
    
    def __init__(self):
        """Initialize data mesh architecture"""
        self.domains: Dict[str, DataDomain] = {}
        self.data_products: Dict[str, DataProduct] = {}
        self.global_catalog: Dict[str, Any] = {}
    
    def create_domain(
        self,
        name: str,
        owner: str,
        governance_policy: str = "standard"
    ) -> DataDomain:
        """
        Create a new data domain
        
        Args:
            name: Domain name
            owner: Domain owner
            governance_policy: Governance policy
            
        Returns:
            Created domain
        """
        domain = DataDomain(
            name=name,
            owner=owner,
            data_products=[],
            governance_policy=governance_policy,
            access_control={}
        )
        
        self.domains[name] = domain
        logger.info(f"Created domain: {name}")
        
        return domain
    
    def register_data_product(
        self,
        name: str,
        domain: str,
        owner: str,
        schema: Dict[str, Any],
        access_policy: str = "public"
    ) -> DataProduct:
        """
        Register a data product
        
        Args:
            name: Product name
            domain: Domain name
            owner: Product owner
            schema: Data schema
            access_policy: Access policy
            
        Returns:
            Registered data product
        """
        if domain not in self.domains:
            raise ValueError(f"Domain {domain} does not exist")
        
        data_product = DataProduct(
            name=name,
            domain=domain,
            owner=owner,
            schema=schema,
            access_policy=access_policy,
            quality_metrics={},
            created_at=datetime.now()
        )
        
        self.data_products[name] = data_product
        self.domains[domain].data_products.append(data_product)
        self.global_catalog[name] = {
            "domain": domain,
            "owner": owner,
            "schema": schema,
            "access_policy": access_policy
        }
        
        logger.info(f"Registered data product: {name} in domain {domain}")
        
        return data_product
    
    def discover_data_products(
        self,
        domain: Optional[str] = None,
        owner: Optional[str] = None
    ) -> List[DataProduct]:
        """
        Discover data products
        
        Args:
            domain: Filter by domain (optional)
            owner: Filter by owner (optional)
            
        Returns:
            List of data products
        """
        products = list(self.data_products.values())
        
        if domain:
            products = [p for p in products if p.domain == domain]
        
        if owner:
            products = [p for p in products if p.owner == owner]
        
        return products
    
    def get_data_product(self, name: str) -> Optional[DataProduct]:
        """
        Get data product by name
        
        Args:
            name: Product name
            
        Returns:
            Data product or None
        """
        return self.data_products.get(name)
    
    def update_quality_metrics(
        self,
        product_name: str,
        metrics: Dict[str, float]
    ):
        """
        Update quality metrics for a data product
        
        Args:
            product_name: Product name
            metrics: Quality metrics
        """
        if product_name not in self.data_products:
            raise ValueError(f"Data product {product_name} does not exist")
        
        self.data_products[product_name].quality_metrics.update(metrics)
        logger.info(f"Updated quality metrics for {product_name}")
    
    def get_catalog(self) -> Dict[str, Any]:
        """
        Get global data catalog
        
        Returns:
            Global catalog
        """
        return self.global_catalog


class DataMeshGovernance:
    """Data Mesh governance framework"""
    
    def __init__(self, data_mesh: DataMeshArchitecture):
        """
        Initialize governance framework
        
        Args:
            data_mesh: Data mesh architecture instance
        """
        self.data_mesh = data_mesh
        self.policies: Dict[str, Dict[str, Any]] = {}
    
    def define_policy(
        self,
        policy_name: str,
        policy_rules: Dict[str, Any]
    ):
        """
        Define a governance policy
        
        Args:
            policy_name: Policy name
            policy_rules: Policy rules
        """
        self.policies[policy_name] = policy_rules
        logger.info(f"Defined policy: {policy_name}")
    
    def validate_data_product(self, product_name: str) -> Dict[str, Any]:
        """
        Validate data product against governance policies
        
        Args:
            product_name: Product name
            
        Returns:
            Validation result
        """
        product = self.data_mesh.get_data_product(product_name)
        if not product:
            return {"valid": False, "error": "Product not found"}
        
        # Check schema
        if not product.schema:
            return {"valid": False, "error": "Schema not defined"}
        
        # Check quality metrics
        if not product.quality_metrics:
            return {"valid": False, "warning": "Quality metrics not set"}
        
        # Check access policy
        if not product.access_policy:
            return {"valid": False, "error": "Access policy not defined"}
        
        return {"valid": True, "product": product}


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create data mesh
    mesh = DataMeshArchitecture()
    
    # Create domains
    customer_domain = mesh.create_domain("customer", "customer-team")
    product_domain = mesh.create_domain("product", "product-team")
    
    # Register data products
    customer_product = mesh.register_data_product(
        name="customer_profiles",
        domain="customer",
        owner="customer-team",
        schema={
            "customer_id": "string",
            "name": "string",
            "email": "string",
            "created_at": "timestamp"
        }
    )
    
    product_catalog = mesh.register_data_product(
        name="product_catalog",
        domain="product",
        owner="product-team",
        schema={
            "product_id": "string",
            "name": "string",
            "price": "float",
            "category": "string"
        }
    )
    
    # Discover products
    products = mesh.discover_data_products(domain="customer")
    print(f"Found {len(products)} products in customer domain")
    
    # Governance
    governance = DataMeshGovernance(mesh)
    validation = governance.validate_data_product("customer_profiles")
    print(f"Validation result: {validation['valid']}")
    
    print("Data Mesh architecture setup complete!")

