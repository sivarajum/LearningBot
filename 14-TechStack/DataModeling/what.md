# Data Modeling: Comprehensive Guide

## Core Concepts

### Data Modeling Fundamentals

Data modeling is the process of creating a conceptual representation of data structures, relationships, and constraints within an information system. It serves as a blueprint for database design and data management, ensuring data integrity, performance, and usability.

**Key Principles:**
- **Abstraction**: Representing real-world entities and relationships
- **Normalization**: Eliminating data redundancy and improving integrity
- **Denormalization**: Optimizing for read performance when needed
- **Scalability**: Designing for growth and changing requirements
- **Flexibility**: Accommodating evolving business needs

**Modeling Levels:**
1. **Conceptual**: High-level business view (ER diagrams)
2. **Logical**: Technology-independent structure (normalized schemas)
3. **Physical**: Technology-specific implementation (actual database schemas)

### Entity-Relationship Modeling

```python
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

class RelationshipType(Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:N"

class Cardinality(Enum):
    ZERO_OR_ONE = "0..1"
    ONE = "1"
    ZERO_OR_MANY = "0..N"
    ONE_OR_MANY = "1..N"

@dataclass
class Entity:
    """Represents an entity in ER model"""
    name: str
    attributes: Dict[str, str] = field(default_factory=dict)  # attr_name -> data_type
    primary_key: List[str] = field(default_factory=list)
    unique_keys: List[List[str]] = field(default_factory=list)
    indexes: List[List[str]] = field(default_factory=list)
    description: str = ""

@dataclass
class Relationship:
    """Represents a relationship between entities"""
    name: str
    entity1: str
    entity2: str
    type: RelationshipType
    cardinality1: Cardinality
    cardinality2: Cardinality
    attributes: Dict[str, str] = field(default_factory=dict)
    description: str = ""

@dataclass
class ERModel:
    """Entity-Relationship model"""
    name: str
    entities: Dict[str, Entity] = field(default_factory=dict)
    relationships: List[Relationship] = field(default_factory=list)
    description: str = ""

    def add_entity(self, entity: Entity):
        """Add entity to model"""
        self.entities[entity.name] = entity

    def add_relationship(self, relationship: Relationship):
        """Add relationship to model"""
        # Validate entities exist
        if relationship.entity1 not in self.entities:
            raise ValueError(f"Entity {relationship.entity1} not found")
        if relationship.entity2 not in self.entities:
            raise ValueError(f"Entity {relationship.entity2} not found")

        self.relationships.append(relationship)

    def get_related_entities(self, entity_name: str) -> List[Relationship]:
        """Get relationships for an entity"""
        return [r for r in self.relationships
                if r.entity1 == entity_name or r.entity2 == entity_name]

    def validate_model(self) -> List[str]:
        """Validate the ER model"""
        errors = []

        # Check for isolated entities
        connected_entities = set()
        for rel in self.relationships:
            connected_entities.add(rel.entity1)
            connected_entities.add(rel.entity2)

        isolated_entities = set(self.entities.keys()) - connected_entities
        if isolated_entities:
            errors.append(f"Isolated entities: {isolated_entities}")

        # Check relationship cardinalities
        for rel in self.relationships:
            if rel.type == RelationshipType.ONE_TO_ONE:
                if rel.cardinality1 not in [Cardinality.ONE, Cardinality.ZERO_OR_ONE]:
                    errors.append(f"Invalid cardinality for 1:1 relationship {rel.name}")
            elif rel.type == RelationshipType.ONE_TO_MANY:
                if rel.cardinality1 not in [Cardinality.ONE, Cardinality.ZERO_OR_ONE]:
                    errors.append(f"Invalid cardinality for 1:N relationship {rel.name}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "entities": {
                name: {
                    "attributes": entity.attributes,
                    "primary_key": entity.primary_key,
                    "unique_keys": entity.unique_keys,
                    "indexes": entity.indexes,
                    "description": entity.description
                }
                for name, entity in self.entities.items()
            },
            "relationships": [
                {
                    "name": rel.name,
                    "entity1": rel.entity1,
                    "entity2": rel.entity2,
                    "type": rel.type.value,
                    "cardinality1": rel.cardinality1.value,
                    "cardinality2": rel.cardinality2.value,
                    "attributes": rel.attributes,
                    "description": rel.description
                }
                for rel in self.relationships
            ]
        }

# Example: E-commerce ER Model
def create_ecommerce_er_model() -> ERModel:
    """Create an e-commerce ER model"""

    model = ERModel(
        name="E-commerce Database",
        description="Entity-Relationship model for e-commerce platform"
    )

    # Entities
    customer = Entity(
        name="Customer",
        attributes={
            "customer_id": "INTEGER",
            "first_name": "VARCHAR(50)",
            "last_name": "VARCHAR(50)",
            "email": "VARCHAR(100)",
            "phone": "VARCHAR(20)",
            "registration_date": "DATE",
            "status": "VARCHAR(20)"
        },
        primary_key=["customer_id"],
        unique_keys=[["email"]],
        indexes=[["registration_date"], ["status"]],
        description="Customer information"
    )

    product = Entity(
        name="Product",
        attributes={
            "product_id": "INTEGER",
            "name": "VARCHAR(200)",
            "description": "TEXT",
            "price": "DECIMAL(10,2)",
            "category": "VARCHAR(50)",
            "stock_quantity": "INTEGER",
            "created_date": "DATE",
            "status": "VARCHAR(20)"
        },
        primary_key=["product_id"],
        indexes=[["category"], ["status"], ["price"]],
        description="Product catalog"
    )

    order_entity = Entity(
        name="Order",
        attributes={
            "order_id": "INTEGER",
            "customer_id": "INTEGER",
            "order_date": "DATETIME",
            "total_amount": "DECIMAL(10,2)",
            "status": "VARCHAR(20)",
            "shipping_address": "TEXT",
            "payment_method": "VARCHAR(50)"
        },
        primary_key=["order_id"],
        indexes=[["customer_id"], ["order_date"], ["status"]],
        description="Customer orders"
    )

    order_item = Entity(
        name="OrderItem",
        attributes={
            "order_item_id": "INTEGER",
            "order_id": "INTEGER",
            "product_id": "INTEGER",
            "quantity": "INTEGER",
            "unit_price": "DECIMAL(10,2)",
            "total_price": "DECIMAL(10,2)"
        },
        primary_key=["order_item_id"],
        indexes=[["order_id"], ["product_id"]],
        description="Order line items"
    )

    # Add entities
    model.add_entity(customer)
    model.add_entity(product)
    model.add_entity(order_entity)
    model.add_entity(order_item)

    # Relationships
    customer_order_rel = Relationship(
        name="Customer_Order",
        entity1="Customer",
        entity2="Order",
        type=RelationshipType.ONE_TO_MANY,
        cardinality1=Cardinality.ONE,
        cardinality2=Cardinality.ZERO_OR_MANY,
        description="Customer places orders"
    )

    order_item_rel = Relationship(
        name="Order_OrderItem",
        entity1="Order",
        entity2="OrderItem",
        type=RelationshipType.ONE_TO_MANY,
        cardinality1=Cardinality.ONE,
        cardinality2=Cardinality.ONE_OR_MANY,
        description="Order contains items"
    )

    product_item_rel = Relationship(
        name="Product_OrderItem",
        entity1="Product",
        entity2="OrderItem",
        type=RelationshipType.ONE_TO_MANY,
        cardinality1=Cardinality.ONE,
        cardinality2=Cardinality.ZERO_OR_MANY,
        description="Product is ordered in items"
    )

    # Add relationships
    model.add_relationship(customer_order_rel)
    model.add_relationship(order_item_rel)
    model.add_relationship(product_item_rel)

    return model
```

## Relational Data Modeling

### Normalization Theory

```python
from typing import Dict, List, Any, Set, Tuple, Optional
import re

class RelationalNormalizer:
    """Database normalization utility"""

    def __init__(self):
        self.functional_dependencies = {}  # attr -> set of determined attrs

    def add_functional_dependency(self, determinant: str, dependent: str):
        """Add functional dependency: determinant -> dependent"""
        if determinant not in self.functional_dependencies:
            self.functional_dependencies[determinant] = set()
        self.functional_dependencies[determinant].add(dependent)

    def get_closure(self, attributes: Set[str]) -> Set[str]:
        """Get attribute closure using Armstrong's axioms"""
        closure = attributes.copy()

        changed = True
        while changed:
            changed = False
            for determinant, dependents in self.functional_dependencies.items():
                # Reflexivity: if B ⊆ A, then A -> B
                if determinant.issubset(closure):
                    new_attrs = dependents - closure
                    if new_attrs:
                        closure.update(new_attrs)
                        changed = True

                # Augmentation: if A -> B, then AC -> BC
                # Transitivity: if A -> B and B -> C, then A -> C
                # (handled by iterative closure computation)

        return closure

    def find_candidate_keys(self, all_attributes: Set[str]) -> List[Set[str]]:
        """Find candidate keys using attribute closure"""
        candidate_keys = []

        # Try single attributes first
        for attr in all_attributes:
            closure = self.get_closure({attr})
            if closure == all_attributes:
                candidate_keys.append({attr})

        # Try combinations if no single-attribute keys found
        if not candidate_keys:
            from itertools import combinations
            for r in range(2, len(all_attributes) + 1):
                for combo in combinations(all_attributes, r):
                    closure = self.get_closure(set(combo))
                    if closure == all_attributes:
                        candidate_keys.append(set(combo))

        return candidate_keys

    def check_normal_form(self, relation: Dict[str, Any], primary_key: Set[str]) -> Dict[str, bool]:
        """Check normal forms for a relation"""
        attributes = set(relation.keys())
        non_key_attrs = attributes - primary_key

        results = {
            "1NF": True,  # Assume atomic values
            "2NF": True,
            "3NF": True,
            "BCNF": True
        }

        # Check 2NF: No partial dependencies
        for determinant, dependents in self.functional_dependencies.items():
            if determinant.issubset(primary_key) and determinant != primary_key:
                # Partial dependency exists
                if dependents.intersection(non_key_attrs):
                    results["2NF"] = False
                    results["3NF"] = False
                    results["BCNF"] = False
                    break

        # Check 3NF: No transitive dependencies
        if results["2NF"]:
            for determinant, dependents in self.functional_dependencies.items():
                if determinant.issubset(attributes) and determinant not in [primary_key]:
                    if dependents.intersection(non_key_attrs):
                        # Check if determinant is a candidate key
                        is_candidate_key = False
                        candidate_keys = self.find_candidate_keys(attributes)
                        for key in candidate_keys:
                            if determinant == key:
                                is_candidate_key = True
                                break

                        if not is_candidate_key:
                            results["3NF"] = False
                            results["BCNF"] = False
                            break

        # Check BCNF: All determinants are candidate keys
        if results["3NF"]:
            for determinant in self.functional_dependencies.keys():
                if determinant.issubset(attributes):
                    candidate_keys = self.find_candidate_keys(attributes)
                    is_candidate_key = any(determinant == key for key in candidate_keys)
                    if not is_candidate_key:
                        results["BCNF"] = False
                        break

        return results

    def decompose_to_3nf(self, relation_name: str, attributes: Set[str],
                        primary_key: Set[str]) -> List[Dict[str, Any]]:
        """Decompose relation to 3NF (simplified algorithm)"""
        relations = []

        # Step 1: Find minimal cover (simplified)
        # Step 2: Decompose based on dependencies

        # For each functional dependency X -> A where A is not in primary key
        for determinant, dependents in self.functional_dependencies.items():
            for dependent in dependents:
                if dependent not in primary_key and determinant.issubset(attributes):
                    # Create new relation
                    new_relation = {
                        "name": f"{relation_name}_{determinant}_{dependent}",
                        "attributes": determinant.union({dependent}),
                        "primary_key": determinant,
                        "foreign_keys": {}
                    }

                    # Check if we need to reference original relation
                    if primary_key.intersection(determinant):
                        new_relation["foreign_keys"] = {
                            relation_name: list(primary_key)
                        }

                    relations.append(new_relation)

        # Keep original relation with only key and dependent attributes
        remaining_attrs = primary_key.copy()
        for deps in self.functional_dependencies.values():
            remaining_attrs.update(deps)

        if remaining_attrs:
            original_relation = {
                "name": relation_name,
                "attributes": remaining_attrs,
                "primary_key": primary_key,
                "foreign_keys": {}
            }
            relations.insert(0, original_relation)

        return relations

# Example: University database normalization
def university_normalization_example():
    """Example of normalizing a university database"""

    normalizer = RelationalNormalizer()

    # Functional dependencies for Student-Course-Grade relation
    # student_id -> student_name, student_dept
    normalizer.add_functional_dependency({"student_id"}, "student_name")
    normalizer.add_functional_dependency({"student_id"}, "student_dept")

    # course_id -> course_name, course_credits
    normalizer.add_functional_dependency({"course_id"}, "course_name")
    normalizer.add_functional_dependency({"course_id"}, "course_credits")

    # (student_id, course_id) -> grade
    normalizer.add_functional_dependency({"student_id", "course_id"}, "grade")

    # All attributes
    all_attributes = {
        "student_id", "student_name", "student_dept",
        "course_id", "course_name", "course_credits", "grade"
    }

    # Primary key
    primary_key = {"student_id", "course_id"}

    # Check normal forms
    relation = {attr: "VARCHAR(100)" for attr in all_attributes}
    normal_forms = normalizer.check_normal_form(relation, primary_key)

    print("Normal Form Analysis:")
    for nf, satisfied in normal_forms.items():
        print(f"  {nf}: {'✓' if satisfied else '✗'}")

    # Decompose to 3NF
    decomposed = normalizer.decompose_to_3nf("StudentCourse", all_attributes, primary_key)

    print("\nDecomposed Relations:")
    for rel in decomposed:
        print(f"  {rel['name']}: {rel['attributes']} (PK: {rel['primary_key']})")

    return decomposed
```

### SQL Schema Generation

```python
from typing import Dict, List, Any, Optional
import sqlparse
from dataclasses import dataclass

@dataclass
class Column:
    """Database column definition"""
    name: str
    data_type: str
    nullable: bool = True
    default_value: Optional[str] = None
    auto_increment: bool = False
    primary_key: bool = False
    unique: bool = False
    references: Optional[Dict[str, str]] = None  # {"table": "column"}
    comment: str = ""

@dataclass
class Index:
    """Database index definition"""
    name: str
    columns: List[str]
    unique: bool = False
    type: str = "BTREE"  # BTREE, HASH, GIN, etc.

@dataclass
class Table:
    """Database table definition"""
    name: str
    columns: List[Column]
    indexes: List[Index] = None
    engine: str = "InnoDB"
    charset: str = "utf8mb4"
    comment: str = ""

    def __post_init__(self):
        if self.indexes is None:
            self.indexes = []

class SQLGenerator:
    """Generate SQL DDL from data model"""

    def __init__(self, dialect: str = "mysql"):
        self.dialect = dialect.lower()

    def generate_create_table(self, table: Table) -> str:
        """Generate CREATE TABLE statement"""

        lines = []
        lines.append(f"CREATE TABLE `{table.name}` (")

        column_defs = []
        primary_keys = []

        for column in table.columns:
            col_def = self._generate_column_definition(column)
            column_defs.append(f"  {col_def}")

            if column.primary_key:
                primary_keys.append(f"`{column.name}`")

        # Add primary key constraint
        if primary_keys:
            column_defs.append(f"  PRIMARY KEY ({', '.join(primary_keys)})")

        # Add foreign key constraints
        for column in table.columns:
            if column.references:
                ref_table = column.references["table"]
                ref_column = column.references["column"]
                fk_name = f"fk_{table.name}_{column.name}"
                fk_def = f"  CONSTRAINT `{fk_name}` FOREIGN KEY (`{column.name}`) REFERENCES `{ref_table}` (`{ref_column}`)"
                column_defs.append(fk_def)

        lines.append(",\n".join(column_defs))
        lines.append(")")

        # Add table options
        options = []
        if self.dialect == "mysql":
            options.append(f"ENGINE={table.engine}")
            options.append(f"DEFAULT CHARSET={table.charset}")
        elif self.dialect == "postgresql":
            options.append(f"WITH (autovacuum_enabled = true)")

        if options:
            lines.append(" ".join(options))

        if table.comment:
            if self.dialect == "mysql":
                lines.append(f"COMMENT '{table.comment}'")
            elif self.dialect == "postgresql":
                # PostgreSQL comments are separate statements
                pass

        return ";\n".join(lines) + ";"

    def _generate_column_definition(self, column: Column) -> str:
        """Generate column definition"""

        parts = [f"`{column.name}` {column.data_type}"]

        if not column.nullable:
            parts.append("NOT NULL")

        if column.auto_increment:
            if self.dialect == "mysql":
                parts.append("AUTO_INCREMENT")
            elif self.dialect == "postgresql":
                # Handled differently in PostgreSQL
                pass

        if column.unique and not column.primary_key:
            parts.append("UNIQUE")

        if column.default_value is not None:
            parts.append(f"DEFAULT {column.default_value}")

        if column.comment and self.dialect == "mysql":
            parts.append(f"COMMENT '{column.comment}'")

        return " ".join(parts)

    def generate_create_index(self, table_name: str, index: Index) -> str:
        """Generate CREATE INDEX statement"""

        unique_str = "UNIQUE " if index.unique else ""

        if self.dialect == "mysql":
            index_type = f" USING {index.type}" if index.type != "BTREE" else ""
            sql = f"CREATE {unique_str}INDEX `{index.name}` ON `{table_name}` ({', '.join(f'`{col}`' for col in index.columns)}){index_type}"
        elif self.dialect == "postgresql":
            index_type = f" USING {index.type.lower()}" if index.type != "BTREE" else ""
            sql = f"CREATE {unique_str}INDEX {index.name} ON {table_name} ({', '.join(index.columns)}){index_type}"
        else:
            sql = f"CREATE {unique_str}INDEX {index.name} ON {table_name} ({', '.join(index.columns)})"

        return sql + ";"

    def generate_schema(self, tables: List[Table]) -> str:
        """Generate complete schema DDL"""

        statements = []

        # Create tables
        for table in tables:
            statements.append(self.generate_create_table(table))

            # Create additional indexes
            for index in table.indexes:
                statements.append(self.generate_create_index(table.name, index))

        # Add comments for PostgreSQL
        if self.dialect == "postgresql":
            for table in tables:
                if table.comment:
                    statements.append(f"COMMENT ON TABLE {table.name} IS '{table.comment}';")

                for column in table.columns:
                    if column.comment:
                        statements.append(f"COMMENT ON COLUMN {table.name}.{column.name} IS '{column.comment}';")

        return "\n\n".join(statements)

# Example: Generate e-commerce schema
def generate_ecommerce_schema():
    """Generate SQL schema for e-commerce database"""

    generator = SQLGenerator("mysql")

    # Customer table
    customer_table = Table(
        name="customer",
        columns=[
            Column("customer_id", "INT", nullable=False, auto_increment=True, primary_key=True),
            Column("first_name", "VARCHAR(50)", nullable=False),
            Column("last_name", "VARCHAR(50)", nullable=False),
            Column("email", "VARCHAR(100)", nullable=False, unique=True),
            Column("phone", "VARCHAR(20)"),
            Column("registration_date", "DATE", nullable=False, default_value="CURRENT_DATE"),
            Column("status", "ENUM('active','inactive','suspended')", nullable=False, default_value="'active'")
        ],
        indexes=[
            Index("idx_customer_registration", ["registration_date"]),
            Index("idx_customer_status", ["status"])
        ],
        comment="Customer information"
    )

    # Product table
    product_table = Table(
        name="product",
        columns=[
            Column("product_id", "INT", nullable=False, auto_increment=True, primary_key=True),
            Column("name", "VARCHAR(200)", nullable=False),
            Column("description", "TEXT"),
            Column("price", "DECIMAL(10,2)", nullable=False),
            Column("category", "VARCHAR(50)", nullable=False),
            Column("stock_quantity", "INT", nullable=False, default_value="0"),
            Column("created_date", "DATE", nullable=False, default_value="CURRENT_DATE"),
            Column("status", "ENUM('active','inactive','discontinued')", nullable=False, default_value="'active'")
        ],
        indexes=[
            Index("idx_product_category", ["category"]),
            Index("idx_product_status", ["status"]),
            Index("idx_product_price", ["price"])
        ],
        comment="Product catalog"
    )

    # Order table
    order_table = Table(
        name="order",
        columns=[
            Column("order_id", "INT", nullable=False, auto_increment=True, primary_key=True),
            Column("customer_id", "INT", nullable=False,
                   references={"table": "customer", "column": "customer_id"}),
            Column("order_date", "DATETIME", nullable=False, default_value="CURRENT_TIMESTAMP"),
            Column("total_amount", "DECIMAL(10,2)", nullable=False),
            Column("status", "ENUM('pending','processing','shipped','delivered','cancelled')",
                   nullable=False, default_value="'pending'"),
            Column("shipping_address", "TEXT", nullable=False),
            Column("payment_method", "VARCHAR(50)", nullable=False)
        ],
        indexes=[
            Index("idx_order_customer", ["customer_id"]),
            Index("idx_order_date", ["order_date"]),
            Index("idx_order_status", ["status"])
        ],
        comment="Customer orders"
    )

    # Order item table
    order_item_table = Table(
        name="order_item",
        columns=[
            Column("order_item_id", "INT", nullable=False, auto_increment=True, primary_key=True),
            Column("order_id", "INT", nullable=False,
                   references={"table": "order", "column": "order_id"}),
            Column("product_id", "INT", nullable=False,
                   references={"table": "product", "column": "product_id"}),
            Column("quantity", "INT", nullable=False),
            Column("unit_price", "DECIMAL(10,2)", nullable=False),
            Column("total_price", "DECIMAL(10,2)", nullable=False)
        ],
        indexes=[
            Index("idx_order_item_order", ["order_id"]),
            Index("idx_order_item_product", ["product_id"])
        ],
        comment="Order line items"
    )

    tables = [customer_table, product_table, order_table, order_item_table]
    schema_sql = generator.generate_schema(tables)

    return schema_sql
```

## Dimensional Data Modeling

### Star Schema Design

```python
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Dimension:
    """Dimension table in star schema"""
    name: str
    attributes: Dict[str, str]  # attr_name -> data_type
    natural_key: List[str]  # business key
    surrogate_key: str = ""  # auto-generated
    hierarchies: List[List[str]] = None  # drill-down paths
    scd_type: int = 1  # Slowly Changing Dimension type
    description: str = ""

    def __post_init__(self):
        if not self.surrogate_key:
            self.surrogate_key = f"{self.name.lower()}_id"
        if self.hierarchies is None:
            self.hierarchies = []

@dataclass
class Fact:
    """Fact table in star schema"""
    name: str
    measures: Dict[str, str]  # measure_name -> data_type
    dimensions: List[str]  # dimension table names
    grain: str  # description of fact grain
    additive_measures: List[str] = None  # fully additive measures
    semi_additive_measures: List[str] = None  # semi-additive measures
    non_additive_measures: List[str] = None  # non-additive measures
    description: str = ""

    def __post_init__(self):
        if self.additive_measures is None:
            self.additive_measures = []
        if self.semi_additive_measures is None:
            self.semi_additive_measures = []
        if self.non_additive_measures is None:
            self.non_additive_measures = []

@dataclass
class StarSchema:
    """Star schema model"""
    name: str
    fact_table: Fact
    dimensions: Dict[str, Dimension]
    description: str = ""

    def validate_schema(self) -> List[str]:
        """Validate star schema"""
        errors = []

        # Check fact table references all dimensions
        fact_dims = set(self.fact_table.dimensions)
        schema_dims = set(self.dimensions.keys())

        missing_dims = fact_dims - schema_dims
        if missing_dims:
            errors.append(f"Fact table references missing dimensions: {missing_dims}")

        extra_dims = schema_dims - fact_dims
        if extra_dims:
            errors.append(f"Unused dimensions: {extra_dims}")

        # Check measure classifications
        all_measures = (self.fact_table.additive_measures +
                       self.fact_table.semi_additive_measures +
                       self.fact_table.non_additive_measures)
        defined_measures = set(self.fact_table.measures.keys())

        unclassified = defined_measures - set(all_measures)
        if unclassified:
            errors.append(f"Unclassified measures: {unclassified}")

        return errors

class DimensionalModeler:
    """Dimensional modeling utilities"""

    def __init__(self):
        self.schemas = {}

    def create_sales_star_schema(self) -> StarSchema:
        """Create a sales analysis star schema"""

        # Dimensions
        dimensions = {}

        # Date dimension
        date_dim = Dimension(
            name="Date",
            attributes={
                "date_key": "INT",
                "date": "DATE",
                "day_of_week": "VARCHAR(10)",
                "month": "VARCHAR(10)",
                "quarter": "VARCHAR(5)",
                "year": "INT",
                "is_weekend": "BOOLEAN",
                "is_holiday": "BOOLEAN"
            },
            natural_key=["date"],
            hierarchies=[
                ["year", "quarter", "month", "date"],
                ["day_of_week", "date"]
            ],
            description="Time dimension for analysis"
        )
        dimensions["Date"] = date_dim

        # Customer dimension
        customer_dim = Dimension(
            name="Customer",
            attributes={
                "customer_key": "INT",
                "customer_id": "VARCHAR(20)",
                "first_name": "VARCHAR(50)",
                "last_name": "VARCHAR(50)",
                "email": "VARCHAR(100)",
                "city": "VARCHAR(50)",
                "state": "VARCHAR(50)",
                "country": "VARCHAR(50)",
                "segment": "VARCHAR(20)",
                "registration_date": "DATE",
                "status": "VARCHAR(20)"
            },
            natural_key=["customer_id"],
            hierarchies=[
                ["country", "state", "city"]
            ],
            scd_type=2,  # Track changes over time
            description="Customer dimension"
        )
        dimensions["Customer"] = customer_dim

        # Product dimension
        product_dim = Dimension(
            name="Product",
            attributes={
                "product_key": "INT",
                "product_id": "VARCHAR(20)",
                "name": "VARCHAR(200)",
                "category": "VARCHAR(50)",
                "subcategory": "VARCHAR(50)",
                "brand": "VARCHAR(50)",
                "price": "DECIMAL(10,2)",
                "cost": "DECIMAL(10,2)",
                "status": "VARCHAR(20)"
            },
            natural_key=["product_id"],
            hierarchies=[
                ["category", "subcategory", "name"]
            ],
            scd_type=2,
            description="Product dimension"
        )
        dimensions["Product"] = product_dim

        # Store dimension
        store_dim = Dimension(
            name="Store",
            attributes={
                "store_key": "INT",
                "store_id": "VARCHAR(20)",
                "name": "VARCHAR(100)",
                "city": "VARCHAR(50)",
                "state": "VARCHAR(50)",
                "country": "VARCHAR(50)",
                "manager": "VARCHAR(100)",
                "type": "VARCHAR(20)",
                "area_sqft": "INT"
            },
            natural_key=["store_id"],
            hierarchies=[
                ["country", "state", "city", "name"]
            ],
            description="Store dimension"
        )
        dimensions["Store"] = store_dim

        # Fact table
        fact_table = Fact(
            name="Sales",
            measures={
                "sales_amount": "DECIMAL(10,2)",
                "cost_amount": "DECIMAL(10,2)",
                "profit_amount": "DECIMAL(10,2)",
                "quantity": "INT",
                "discount_amount": "DECIMAL(10,2)",
                "tax_amount": "DECIMAL(10,2)"
            },
            dimensions=["Date", "Customer", "Product", "Store"],
            grain="Individual sales transactions",
            additive_measures=["sales_amount", "cost_amount", "profit_amount", "quantity"],
            semi_additive_measures=["discount_amount", "tax_amount"],
            description="Sales fact table"
        )

        schema = StarSchema(
            name="SalesAnalysis",
            fact_table=fact_table,
            dimensions=dimensions,
            description="Star schema for sales analysis"
        )

        self.schemas[schema.name] = schema
        return schema

    def generate_etl_sql(self, schema: StarSchema) -> Dict[str, str]:
        """Generate ETL SQL for loading star schema"""

        etl_queries = {}

        # Dimension loading queries
        for dim_name, dimension in schema.dimensions.items():
            etl_queries[f"load_{dim_name.lower()}_dimension"] = self._generate_dimension_etl(dimension)

        # Fact loading query
        etl_queries["load_sales_fact"] = self._generate_fact_etl(schema.fact_table, schema.dimensions)

        return etl_queries

    def _generate_dimension_etl(self, dimension: Dimension) -> str:
        """Generate ETL SQL for dimension loading"""

        natural_key_cols = ", ".join(dimension.natural_key)
        all_cols = [dimension.surrogate_key] + list(dimension.attributes.keys())
        all_cols_str = ", ".join(all_cols)

        # SCD Type 1: Overwrite
        if dimension.scd_type == 1:
            sql = f"""
INSERT INTO {dimension.name}
({all_cols_str})
SELECT
    COALESCE(existing.{dimension.surrogate_key}, ROW_NUMBER() OVER (ORDER BY {natural_key_cols})) as {dimension.surrogate_key},
    src.*
FROM source_data src
LEFT JOIN {dimension.name} existing ON {' AND '.join(f'src.{k} = existing.{k}' for k in dimension.natural_key)}
ON DUPLICATE KEY UPDATE
    {', '.join(f'{attr} = VALUES({attr})' for attr in dimension.attributes.keys() if attr != dimension.surrogate_key)}
"""
        else:
            # SCD Type 2: Add new rows
            sql = f"""
INSERT INTO {dimension.name}
({all_cols_str}, effective_date, expiry_date, is_current)
SELECT
    COALESCE(existing.{dimension.surrogate_key}, ROW_NUMBER() OVER (ORDER BY {natural_key_cols})) as {dimension.surrogate_key},
    src.*,
    CURRENT_DATE as effective_date,
    NULL as expiry_date,
    1 as is_current
FROM source_data src
LEFT JOIN {dimension.name} existing ON {' AND '.join(f'src.{k} = existing.{k}' for k in dimension.natural_key)}
WHERE existing.{dimension.surrogate_key} IS NULL
   OR existing.is_current = 0
"""

        return sql.strip()

    def _generate_fact_etl(self, fact: Fact, dimensions: Dict[str, Dimension]) -> str:
        """Generate ETL SQL for fact loading"""

        # Build dimension key joins
        joins = []
        select_cols = []

        for dim_name in fact.dimensions:
            dim = dimensions[dim_name]
            join_condition = ' AND '.join(f'src.{k} = d_{dim_name}.{k}' for k in dim.natural_key)
            joins.append(f"LEFT JOIN {dim_name} d_{dim_name} ON {join_condition}")
            select_cols.append(f"d_{dim_name}.{dim.surrogate_key} as {dim_name.lower()}_key")

        # Add measures
        select_cols.extend(f"src.{measure}" for measure in fact.measures.keys())

        joins_str = "\n".join(joins)
        select_str = ",\n    ".join(select_cols)

        sql = f"""
INSERT INTO {fact.name}
(
    {', '.join(f'{dim.lower()}_key' for dim in fact.dimensions)},
    {', '.join(fact.measures.keys())}
)
SELECT
    {select_str}
FROM source_sales_data src
{joins_str}
WHERE src.transaction_date >= '2023-01-01'
"""

        return sql.strip()

    def analyze_query_performance(self, schema: StarSchema, query: str) -> Dict[str, Any]:
        """Analyze query performance characteristics"""

        analysis = {
            "dimensions_used": [],
            "measures_used": [],
            "joins_required": 0,
            "estimated_complexity": "low",
            "recommended_indexes": []
        }

        # Simple analysis based on schema
        query_lower = query.lower()

        # Check dimensions used
        for dim_name in schema.dimensions:
            if dim_name.lower() in query_lower:
                analysis["dimensions_used"].append(dim_name)

        # Check measures used
        for measure in schema.fact_table.measures:
            if measure in query_lower:
                analysis["measures_used"].append(measure)

        analysis["joins_required"] = len(analysis["dimensions_used"])

        # Complexity assessment
        if analysis["joins_required"] > 3:
            analysis["estimated_complexity"] = "high"
        elif analysis["joins_required"] > 1:
            analysis["estimated_complexity"] = "medium"

        # Index recommendations
        for dim_name in analysis["dimensions_used"]:
            dim = schema.dimensions[dim_name]
            analysis["recommended_indexes"].append({
                "table": dim_name,
                "columns": [dim.surrogate_key]
            })

        return analysis
```

## NoSQL Data Modeling

### Document Database Modeling

```python
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import uuid

@dataclass
class DocumentModel:
    """Document database model"""
    collection_name: str
    schema: Dict[str, Any]  # JSON schema-like structure
    indexes: List[Dict[str, Any]] = None
    validation_rules: Dict[str, Any] = None
    description: str = ""

    def __post_init__(self):
        if self.indexes is None:
            self.indexes = []

class DocumentModeler:
    """Document database modeling utilities"""

    def __init__(self):
        self.models = {}

    def create_user_profile_model(self) -> DocumentModel:
        """Create user profile document model"""

        schema = {
            "_id": {"type": "objectId", "required": True},
            "user_id": {"type": "string", "required": True},
            "username": {"type": "string", "required": True, "unique": True},
            "email": {"type": "string", "required": True, "unique": True},
            "personal_info": {
                "first_name": {"type": "string", "required": True},
                "last_name": {"type": "string", "required": True},
                "date_of_birth": {"type": "date"},
                "gender": {"type": "string", "enum": ["male", "female", "other"]}
            },
            "contact_info": {
                "phone": {"type": "string"},
                "address": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "zip_code": {"type": "string"},
                    "country": {"type": "string"}
                }
            },
            "preferences": {
                "language": {"type": "string", "default": "en"},
                "timezone": {"type": "string", "default": "UTC"},
                "notifications": {
                    "email": {"type": "boolean", "default": True},
                    "sms": {"type": "boolean", "default": False},
                    "push": {"type": "boolean", "default": True}
                }
            },
            "account_status": {
                "is_active": {"type": "boolean", "default": True},
                "is_verified": {"type": "boolean", "default": False},
                "last_login": {"type": "date"},
                "created_at": {"type": "date", "default": "now"},
                "updated_at": {"type": "date", "default": "now"}
            },
            "activity_log": {
                "type": "array",
                "items": {
                    "action": {"type": "string"},
                    "timestamp": {"type": "date"},
                    "ip_address": {"type": "string"},
                    "user_agent": {"type": "string"}
                }
            }
        }

        indexes = [
            {"key": {"user_id": 1}, "unique": True},
            {"key": {"username": 1}, "unique": True},
            {"key": {"email": 1}, "unique": True},
            {"key": {"account_status.is_active": 1}},
            {"key": {"account_status.created_at": 1}},
            {"key": {"personal_info.date_of_birth": 1}}
        ]

        validation_rules = {
            "validator": {
                "$jsonSchema": schema
            },
            "validationLevel": "moderate",
            "validationAction": "warn"
        }

        model = DocumentModel(
            collection_name="user_profiles",
            schema=schema,
            indexes=indexes,
            validation_rules=validation_rules,
            description="User profile and account information"
        )

        self.models[model.collection_name] = model
        return model

    def create_product_catalog_model(self) -> DocumentModel:
        """Create product catalog document model"""

        schema = {
            "_id": {"type": "objectId", "required": True},
            "product_id": {"type": "string", "required": True},
            "name": {"type": "string", "required": True},
            "description": {"type": "string"},
            "category": {"type": "string", "required": True},
            "subcategory": {"type": "string"},
            "brand": {"type": "string"},
            "pricing": {
                "base_price": {"type": "decimal", "required": True},
                "sale_price": {"type": "decimal"},
                "currency": {"type": "string", "default": "USD"},
                "discount_percentage": {"type": "number", "minimum": 0, "maximum": 100}
            },
            "inventory": {
                "total_quantity": {"type": "integer", "minimum": 0},
                "available_quantity": {"type": "integer", "minimum": 0},
                "reserved_quantity": {"type": "integer", "minimum": 0},
                "locations": {
                    "type": "array",
                    "items": {
                        "warehouse_id": {"type": "string"},
                        "quantity": {"type": "integer"}
                    }
                }
            },
            "attributes": {
                "type": "object",
                "additionalProperties": True
            },
            "images": {
                "type": "array",
                "items": {
                    "url": {"type": "string"},
                    "alt_text": {"type": "string"},
                    "is_primary": {"type": "boolean"}
                }
            },
            "reviews": {
                "type": "array",
                "items": {
                    "review_id": {"type": "string"},
                    "user_id": {"type": "string"},
                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                    "comment": {"type": "string"},
                    "created_at": {"type": "date"},
                    "verified_purchase": {"type": "boolean"}
                }
            },
            "metadata": {
                "created_at": {"type": "date", "default": "now"},
                "updated_at": {"type": "date", "default": "now"},
                "created_by": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "status": {"type": "string", "enum": ["active", "inactive", "discontinued"]}
            }
        }

        indexes = [
            {"key": {"product_id": 1}, "unique": True},
            {"key": {"category": 1}},
            {"key": {"subcategory": 1}},
            {"key": {"brand": 1}},
            {"key": {"pricing.base_price": 1}},
            {"key": {"inventory.available_quantity": 1}},
            {"key": {"metadata.status": 1}},
            {"key": {"metadata.tags": 1}},
            {"key": {"reviews.rating": 1}}
        ]

        model = DocumentModel(
            collection_name="product_catalog",
            schema=schema,
            indexes=indexes,
            description="Product catalog with inventory and reviews"
        )

        self.models[model.collection_name] = model
        return model

    def generate_sample_documents(self, model: DocumentModel, count: int = 5) -> List[Dict[str, Any]]:
        """Generate sample documents for testing"""

        samples = []

        for i in range(count):
            if model.collection_name == "user_profiles":
                doc = self._generate_user_sample(i)
            elif model.collection_name == "product_catalog":
                doc = self._generate_product_sample(i)
            else:
                continue

            samples.append(doc)

        return samples

    def _generate_user_sample(self, index: int) -> Dict[str, Any]:
        """Generate sample user document"""

        return {
            "_id": str(uuid.uuid4()),
            "user_id": f"USER{index:03d}",
            "username": f"user{index}",
            "email": f"user{index}@example.com",
            "personal_info": {
                "first_name": f"First{index}",
                "last_name": f"Last{index}",
                "date_of_birth": f"199{index % 10}-01-01",
                "gender": ["male", "female", "other"][index % 3]
            },
            "contact_info": {
                "phone": f"+1-555-010{index}",
                "address": {
                    "street": f"{index} Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip_code": "12345",
                    "country": "USA"
                }
            },
            "preferences": {
                "language": "en",
                "timezone": "America/Los_Angeles",
                "notifications": {
                    "email": True,
                    "sms": index % 2 == 0,
                    "push": True
                }
            },
            "account_status": {
                "is_active": True,
                "is_verified": index % 3 != 0,
                "last_login": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "activity_log": [
                {
                    "action": "login",
                    "timestamp": datetime.now().isoformat(),
                    "ip_address": f"192.168.1.{index}",
                    "user_agent": "Mozilla/5.0..."
                }
            ]
        }

    def _generate_product_sample(self, index: int) -> Dict[str, Any]:
        """Generate sample product document"""

        categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        brands = ["Apple", "Nike", "Penguin", "IKEA", "Adidas"]

        return {
            "_id": str(uuid.uuid4()),
            "product_id": f"PROD{index:03d}",
            "name": f"Product {index}",
            "description": f"Description for product {index}",
            "category": categories[index % len(categories)],
            "subcategory": f"Subcategory {index % 3}",
            "brand": brands[index % len(brands)],
            "pricing": {
                "base_price": 10.0 + index * 5,
                "sale_price": 8.0 + index * 4 if index % 2 == 0 else None,
                "currency": "USD",
                "discount_percentage": 20 if index % 2 == 0 else 0
            },
            "inventory": {
                "total_quantity": 100 + index * 10,
                "available_quantity": 80 + index * 8,
                "reserved_quantity": 10 + index * 2,
                "locations": [
                    {"warehouse_id": "WH001", "quantity": 50 + index * 5},
                    {"warehouse_id": "WH002", "quantity": 30 + index * 3}
                ]
            },
            "attributes": {
                "color": ["Red", "Blue", "Green"][index % 3],
                "size": ["S", "M", "L", "XL"][index % 4],
                "material": "Cotton"
            },
            "images": [
                {
                    "url": f"https://example.com/images/prod{index}_1.jpg",
                    "alt_text": f"Product {index} image 1",
                    "is_primary": True
                }
            ],
            "reviews": [
                {
                    "review_id": f"REV{index}001",
                    "user_id": f"USER{index:03d}",
                    "rating": (index % 5) + 1,
                    "comment": f"Great product! Rating: {(index % 5) + 1}/5",
                    "created_at": datetime.now().isoformat(),
                    "verified_purchase": True
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "created_by": "admin",
                "tags": ["featured", "bestseller"] if index % 3 == 0 else ["new"],
                "status": "active"
            }
        }

    def analyze_query_patterns(self, model: DocumentModel) -> Dict[str, Any]:
        """Analyze common query patterns for the model"""

        patterns = {
            "user_profiles": {
                "frequent_queries": [
                    {"username": "..."},  # Login
                    {"email": "..."},     # Password reset
                    {"account_status.is_active": True},  # Active users
                    {"personal_info.date_of_birth": {"$gte": "1990-01-01"}},  # Age-based queries
                ],
                "recommended_indexes": [
                    {"username": 1},
                    {"email": 1},
                    {"account_status.is_active": 1},
                    {"personal_info.date_of_birth": 1}
                ]
            },
            "product_catalog": {
                "frequent_queries": [
                    {"category": "..."},  # Category browsing
                    {"pricing.base_price": {"$lte": 100}},  # Price filtering
                    {"inventory.available_quantity": {"$gt": 0}},  # In-stock products
                    {"reviews.rating": {"$gte": 4}},  # High-rated products
                ],
                "recommended_indexes": [
                    {"category": 1},
                    {"pricing.base_price": 1},
                    {"inventory.available_quantity": 1},
                    {"reviews.rating": 1}
                ]
            }
        }

        return patterns.get(model.collection_name, {})
```

## Graph Data Modeling

### Property Graph Model

```python
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import networkx as nx

class NodeType(Enum):
    PERSON = "Person"
    PRODUCT = "Product"
    ORDER = "Order"
    CATEGORY = "Category"
    LOCATION = "Location"

class EdgeType(Enum):
    PURCHASED = "PURCHASED"
    BELONGS_TO = "BELONGS_TO"
    LOCATED_IN = "LOCATED_IN"
    FRIEND_OF = "FRIEND_OF"
    REVIEWED = "REVIEWED"

@dataclass
class Node:
    """Graph node"""
    id: str
    label: NodeType
    properties: Dict[str, Any]
    created_at: str = ""

@dataclass
class Edge:
    """Graph edge"""
    id: str
    source: str
    target: str
    label: EdgeType
    properties: Dict[str, Any]
    created_at: str = ""

@dataclass
class GraphSchema:
    """Property graph schema"""
    name: str
    node_types: Dict[NodeType, Dict[str, Any]]  # Node type -> property schema
    edge_types: Dict[EdgeType, Dict[str, Any]]  # Edge type -> property schema
    constraints: List[Dict[str, Any]] = None
    indexes: List[Dict[str, Any]] = None
    description: str = ""

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.indexes is None:
            self.indexes = []

class GraphModeler:
    """Graph data modeling utilities"""

    def __init__(self):
        self.schemas = {}

    def create_ecommerce_graph_schema(self) -> GraphSchema:
        """Create e-commerce graph schema"""

        node_types = {
            NodeType.PERSON: {
                "properties": {
                    "person_id": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "email": {"type": "string", "required": True},
                    "age": {"type": "integer"},
                    "gender": {"type": "string"},
                    "registration_date": {"type": "date"}
                }
            },
            NodeType.PRODUCT: {
                "properties": {
                    "product_id": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "category": {"type": "string", "required": True},
                    "price": {"type": "decimal", "required": True},
                    "description": {"type": "string"}
                }
            },
            NodeType.ORDER: {
                "properties": {
                    "order_id": {"type": "string", "required": True},
                    "total_amount": {"type": "decimal", "required": True},
                    "order_date": {"type": "date", "required": True},
                    "status": {"type": "string", "required": True}
                }
            },
            NodeType.CATEGORY: {
                "properties": {
                    "category_id": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "description": {"type": "string"},
                    "parent_category": {"type": "string"}
                }
            },
            NodeType.LOCATION: {
                "properties": {
                    "location_id": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "type": {"type": "string", "enum": ["country", "state", "city"]},
                    "parent_location": {"type": "string"}
                }
            }
        }

        edge_types = {
            EdgeType.PURCHASED: {
                "source_type": NodeType.PERSON,
                "target_type": NodeType.PRODUCT,
                "properties": {
                    "order_id": {"type": "string", "required": True},
                    "quantity": {"type": "integer", "required": True},
                    "unit_price": {"type": "decimal", "required": True},
                    "purchase_date": {"type": "date", "required": True}
                }
            },
            EdgeType.BELONGS_TO: {
                "source_type": NodeType.PRODUCT,
                "target_type": NodeType.CATEGORY,
                "properties": {}
            },
            EdgeType.LOCATED_IN: {
                "source_type": NodeType.PERSON,
                "target_type": NodeType.LOCATION,
                "properties": {
                    "address_type": {"type": "string", "enum": ["home", "work", "billing"]}
                }
            },
            EdgeType.FRIEND_OF: {
                "source_type": NodeType.PERSON,
                "target_type": NodeType.PERSON,
                "properties": {
                    "relationship_type": {"type": "string", "enum": ["friend", "family", "colleague"]},
                    "strength": {"type": "integer", "minimum": 1, "maximum": 10}
                }
            },
            EdgeType.REVIEWED: {
                "source_type": NodeType.PERSON,
                "target_type": NodeType.PRODUCT,
                "properties": {
                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                    "comment": {"type": "string"},
                    "review_date": {"type": "date"}
                }
            }
        }

        constraints = [
            {"type": "uniqueness", "node_type": NodeType.PERSON, "properties": ["person_id"]},
            {"type": "uniqueness", "node_type": NodeType.PRODUCT, "properties": ["product_id"]},
            {"type": "uniqueness", "node_type": NodeType.ORDER, "properties": ["order_id"]},
            {"type": "existence", "edge_type": EdgeType.PURCHASED, "properties": ["order_id", "quantity"]}
        ]

        indexes = [
            {"type": "node_property", "node_type": NodeType.PERSON, "property": "email"},
            {"type": "node_property", "node_type": NodeType.PRODUCT, "property": "category"},
            {"type": "edge_property", "edge_type": EdgeType.PURCHASED, "property": "purchase_date"}
        ]

        schema = GraphSchema(
            name="EcommerceGraph",
            node_types=node_types,
            edge_types=edge_types,
            constraints=constraints,
            indexes=indexes,
            description="E-commerce knowledge graph"
        )

        self.schemas[schema.name] = schema
        return schema

    def generate_cypher_schema(self, schema: GraphSchema) -> str:
        """Generate Cypher DDL for Neo4j"""

        cypher_statements = []

        # Create constraints
        for constraint in schema.constraints:
            if constraint["type"] == "uniqueness":
                node_label = constraint["node_type"].value
                props = constraint["properties"]
                for prop in props:
                    cypher = f"CREATE CONSTRAINT {node_label}_{prop}_unique IF NOT EXISTS FOR (n:{node_label}) REQUIRE n.{prop} IS UNIQUE"
                    cypher_statements.append(cypher)
            elif constraint["type"] == "existence":
                edge_type = constraint["edge_type"].value
                props = constraint["properties"]
                for prop in props:
                    cypher = f"CREATE CONSTRAINT {edge_type}_{prop}_exists IF NOT EXISTS FOR ()-[r:{edge_type}]-() REQUIRE r.{prop} IS NOT NULL"
                    cypher_statements.append(cypher)

        # Create indexes
        for index in schema.indexes:
            if index["type"] == "node_property":
                node_label = index["node_type"].value
                prop = index["property"]
                cypher = f"CREATE INDEX {node_label}_{prop}_idx IF NOT EXISTS FOR (n:{node_label}) ON (n.{prop})"
                cypher_statements.append(cypher)
            elif index["type"] == "edge_property":
                edge_type = index["edge_type"].value
                prop = index["property"]
                cypher = f"CREATE INDEX {edge_type}_{prop}_idx IF NOT EXISTS FOR ()-[r:{edge_type}]-() ON (r.{prop})"
                cypher_statements.append(cypher)

        return ";\n".join(cypher_statements) + ";"

    def generate_sample_queries(self, schema: GraphSchema) -> Dict[str, str]:
        """Generate sample Cypher queries"""

        queries = {}

        if schema.name == "EcommerceGraph":
            queries = {
                "find_customer_purchases": """
                MATCH (p:Person {person_id: $customer_id})-[r:PURCHASED]->(prod:Product)
                RETURN prod.name, r.quantity, r.unit_price, r.purchase_date
                ORDER BY r.purchase_date DESC
                """,

                "product_recommendations": """
                MATCH (p:Person {person_id: $customer_id})-[r1:PURCHASED]->(prod1:Product)
                MATCH (prod1)<-[r2:PURCHASED]-(other:Person)
                WHERE other.person_id <> $customer_id
                MATCH (other)-[r3:PURCHASED]->(prod2:Product)
                WHERE prod2.product_id <> prod1.product_id
                RETURN prod2.name, count(*) as frequency
                ORDER BY frequency DESC
                LIMIT 10
                """,

                "customer_social_network": """
                MATCH (p:Person {person_id: $customer_id})-[f:FRIEND_OF]-(friend:Person)
                OPTIONAL MATCH (friend)-[r:PURCHASED]->(prod:Product)
                RETURN friend.name, f.relationship_type, f.strength,
                       collect({product: prod.name, date: r.purchase_date}) as purchases
                """,

                "category_performance": """
                MATCH (cat:Category)<-[:BELONGS_TO]-(prod:Product)<-[r:PURCHASED]-()
                RETURN cat.name, count(r) as total_purchases,
                       sum(r.quantity * r.unit_price) as total_revenue
                ORDER BY total_revenue DESC
                """
            }

        return queries

    def analyze_graph_patterns(self, schema: GraphSchema) -> Dict[str, Any]:
        """Analyze common graph query patterns"""

        analysis = {
            "node_types_count": len(schema.node_types),
            "edge_types_count": len(schema.edge_types),
            "query_patterns": [],
            "performance_considerations": []
        }

        # Analyze edge patterns
        for edge_type, edge_schema in schema.edge_types.items():
            source_type = edge_schema["source_type"].value
            target_type = edge_schema["target_type"].value

            pattern = {
                "pattern": f"({source_type})-[:{edge_type.value}]->({target_type})",
                "use_cases": self._get_pattern_use_cases(edge_type),
                "traversal_complexity": self._assess_traversal_complexity(edge_type)
            }
            analysis["query_patterns"].append(pattern)

        # Performance considerations
        if len(schema.node_types) > 10:
            analysis["performance_considerations"].append("Consider partitioning for large node sets")

        if any(len(edge_schema["properties"]) > 5 for edge_schema in schema.edge_types.values()):
            analysis["performance_considerations"].append("Complex edge properties may impact traversal performance")

        return analysis

    def _get_pattern_use_cases(self, edge_type: EdgeType) -> List[str]:
        """Get use cases for edge patterns"""

        use_cases = {
            EdgeType.PURCHASED: ["Purchase history", "Customer segmentation", "Product recommendations"],
            EdgeType.BELONGS_TO: ["Product categorization", "Category browsing", "Inventory management"],
            EdgeType.FRIEND_OF: ["Social recommendations", "Network analysis", "Customer influence"],
            EdgeType.REVIEWED: ["Product ratings", "Review analysis", "Quality assessment"]
        }

        return use_cases.get(edge_type, [])

    def _assess_traversal_complexity(self, edge_type: EdgeType) -> str:
        """Assess traversal complexity"""

        complexities = {
            EdgeType.PURCHASED: "medium",  # Many-to-many with properties
            EdgeType.BELONGS_TO: "low",    # Hierarchical, one-to-many
            EdgeType.FRIEND_OF: "high",    # Complex social network patterns
            EdgeType.REVIEWED: "medium"    # One-to-many with ratings
        }

        return complexities.get(edge_type, "medium")
```

This comprehensive guide covers data modeling fundamentals including ER modeling, relational normalization, dimensional modeling, NoSQL document modeling, and graph data modeling. The code examples demonstrate practical implementations for creating and managing different types of data models with proper validation, schema generation, and query optimization.
