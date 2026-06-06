# Looker - Interview Questions & Answers

## Core LookML Concepts

### 1. Explain the difference between dimensions and measures in LookML.

**Answer:** Dimensions and measures are fundamental concepts in LookML:

- **Dimensions**: Descriptive attributes used for grouping and filtering data (e.g., customer_name, order_date, product_category). They represent "who, what, when, where" and are typically used in GROUP BY clauses.

- **Measures**: Quantitative values that can be aggregated (e.g., total_sales, average_order_value, count_orders). They represent "how many, how much" and use aggregation functions like SUM, COUNT, AVG.

Dimensions provide context, measures provide the numbers. A good rule: if you can GROUP BY it, it's a dimension; if you aggregate it, it's a measure.

### 2. How does Looker differ from traditional BI tools like Tableau or Power BI?

**Answer:** Looker differs in its approach:

- **Code-based modeling**: LookML provides version-controlled, reusable data models
- **Semantic layer**: Centralized business logic ensures consistency
- **API-first design**: Built for embedding and integration
- **Governed self-service**: Business users explore within defined boundaries
- **Real-time collaboration**: Live editing and commenting on analyses

Unlike drag-and-drop BI tools, Looker emphasizes governance and scalability through code.

### 3. What are Explores and how do they work?

**Answer:** Explores are the primary way users interact with data in Looker. They:

- **Join multiple views**: Combine related tables through defined relationships
- **Provide field suggestions**: Show relevant dimensions and measures
- **Enable ad-hoc analysis**: Allow users to build custom queries
- **Maintain performance**: Use optimized SQL generation

Explores are defined in model files and represent business domains (e.g., "Customer Analytics", "Sales Performance").

## Data Modeling & LookML

### 4. How would you design a LookML model for an e-commerce business?

**Answer:** My approach:
1. **Identify core entities**: Customers, orders, products, inventory
2. **Create base views**: One view per table with dimensions and measures
3. **Define relationships**: Primary/foreign key relationships
4. **Build explores**: Customer explore (joins customers + orders + products)
5. **Add business logic**: Calculated fields for metrics like customer lifetime value
6. **Implement security**: Row-level security for different user types
7. **Create derived tables**: For complex calculations or aggregations

Focus on reusability, performance, and business value.

### 5. Explain the concept of derived tables in LookML.

**Answer:** Derived tables create virtual tables from SQL queries. Types include:

- **SQL-based**: Custom SQL queries for complex transformations
- **Native derived tables (NDTs)**: Persistent cached tables for performance
- **Ephemeral**: Temporary tables for query-specific logic

Use cases:
- **Complex joins**: When standard joins aren't sufficient
- **Aggregations**: Pre-computed summaries for performance
- **Data transformations**: Cleaning or restructuring data
- **External data**: Incorporating data from APIs or other sources

### 6. How do you handle slowly changing dimensions in LookML?

**Answer:** For slowly changing dimensions (SCDs):
1. **Type 1**: Overwrite old values (simple, loses history)
2. **Type 2**: Add new rows with effective dates
3. **Type 3**: Add columns for previous values

In LookML:
- Use `sql` parameters with conditional logic
- Create separate views for current and historical data
- Use derived tables to handle complex SCD logic
- Implement date-based filtering for point-in-time analysis

## Performance Optimization

### 7. How do you optimize Looker query performance?

**Answer:** Performance optimization strategies:
1. **Use PDTs**: Cache expensive calculations in persistent derived tables
2. **Optimize joins**: Use appropriate join types and conditions
3. **Filter pushdown**: Ensure filters are applied at the database level
4. **Aggregate awareness**: Use summary tables for high-level queries
5. **Query caching**: Leverage Looker's result caching
6. **Database tuning**: Optimize database indexes and configurations

Monitor query performance using Looker's system activity dashboard.

### 8. Explain the caching strategy in Looker.

**Answer:** Looker uses multiple caching layers:
- **Result cache**: Caches query results (default 1 hour)
- **PDT cache**: Persistent derived tables for complex calculations
- **Datagroups**: Control cache refresh timing based on data changes
- **Database cache**: Leverages underlying database caching

Best practices:
- Set appropriate cache durations
- Use datagroups for data-driven cache invalidation
- Monitor cache hit rates
- Balance performance vs. data freshness

### 9. How do you handle large datasets in Looker?

**Answer:** For large datasets:
1. **Use sampling**: For exploratory analysis
2. **Implement pagination**: For large result sets
3. **Create aggregates**: Pre-compute summaries
4. **Use PDTs**: Cache complex queries
5. **Optimize queries**: Reduce data scanned
6. **Set row limits**: Prevent runaway queries
7. **Use BigQuery**: For massive datasets with BI Engine

## Security & Governance

### 10. How do you implement row-level security in Looker?

**Answer:** Row-level security (RLS) in LookML:
1. **User attributes**: Store user-specific values (department, region)
2. **SQL filters**: Apply WHERE clauses based on user attributes
3. **Access filters**: Define filters in model files
4. **Groups**: Organize users for easier management

Example:
```lookml
access_filter: {
  field: region
  user_attribute: allowed_regions
}
```

This ensures users only see data they're authorized to access.

### 11. What are some best practices for LookML development?

**Answer:** LookML best practices:
1. **Consistent naming**: Use clear, consistent field names
2. **Documentation**: Document all views, fields, and logic
3. **Version control**: Use Git for all LookML changes
4. **Testing**: Write tests for critical business logic
5. **Modular design**: Break complex models into smaller, reusable views
6. **Performance**: Optimize queries and use appropriate caching
7. **Security**: Implement proper access controls
8. **Code review**: Review all changes before deployment

### 12. How do you manage LookML deployments across environments?

**Answer:** Deployment strategy:
1. **Git workflow**: Feature branches for development
2. **Environments**: Development, staging, production instances
3. **CI/CD**: Automated deployment pipelines
4. **Testing**: Automated tests before deployment
5. **Rollback plan**: Ability to quickly revert changes
6. **Change management**: Document and communicate changes
7. **Monitoring**: Track performance impact of changes

## Dashboard & Visualization

### 13. How do you design an effective Looker dashboard?

**Answer:** Effective dashboard design:
1. **User-centered**: Design for specific user needs and workflows
2. **Clear hierarchy**: Use size and position to show importance
3. **Consistent styling**: Maintain visual consistency
4. **Performance**: Optimize for fast loading
5. **Mobile-friendly**: Ensure usability on all devices
6. **Actionable**: Include insights that drive decisions
7. **Context**: Provide necessary filters and explanations

### 14. Explain the difference between Looks and dashboards.

**Answer:**
- **Looks**: Individual visualizations or data explorations that can be saved and shared
- **Dashboards**: Collections of Looks organized on a single page

Looks are building blocks, dashboards are curated experiences. Looks can exist independently, dashboards provide context and narrative.

### 15. How do you create custom visualizations in Looker?

**Answer:** Custom visualizations:
1. **Use Visualization API**: JavaScript-based custom charts
2. **HTML/CSS**: For completely custom layouts
3. **Third-party libraries**: Integrate D3.js, Chart.js, etc.
4. **Looker components**: Use pre-built visualization components

Process:
- Create visualization file with JavaScript
- Define data handling and rendering logic
- Add to LookML project
- Reference in dashboard elements

## Integration & Embedding

### 16. How do you embed Looker content in applications?

**Answer:** Embedding methods:
1. **iFrame embedding**: Simple URL-based embedding
2. **JavaScript embedding**: Programmatic embedding with customization
3. **API embedding**: Server-side embedding for full control
4. **SSO integration**: Single sign-on with application authentication

Considerations:
- **Security**: Ensure proper authentication and authorization
- **Theming**: Match application design
- **Performance**: Optimize for user experience
- **Mobile**: Ensure mobile compatibility

### 17. Explain Looker's API capabilities.

**Answer:** Looker APIs provide:
- **Query API**: Execute LookML queries programmatically
- **Dashboard API**: Create, modify, and embed dashboards
- **User API**: Manage users and permissions
- **Content API**: Access Looks, dashboards, and folders
- **System API**: Administrative functions

Use cases:
- **Custom applications**: Build analytics into applications
- **ETL processes**: Extract data for other systems
- **Automation**: Automate Looker management tasks
- **Integration**: Connect with other business systems

## Advanced Analytics

### 18. How do you implement A/B testing analysis in Looker?

**Answer:** A/B testing in Looker:
1. **Data collection**: Store experiment data (user_id, variant, metrics)
2. **Statistical analysis**: Use LookML for significance testing
3. **Visualization**: Create dashboards showing test results
4. **Automated alerts**: Notify when tests reach statistical significance

Key metrics:
- **Conversion rates**: Primary success metrics
- **Confidence intervals**: Statistical significance bounds
- **Sample size**: Ensure adequate statistical power
- **Duration**: Monitor test duration and results over time

### 19. How do you handle data quality monitoring in Looker?

**Answer:** Data quality monitoring:
1. **Validation rules**: Define expected data patterns
2. **Automated checks**: Schedule data quality queries
3. **Alerting**: Set up alerts for data quality issues
4. **Dashboards**: Create data quality monitoring dashboards
5. **Documentation**: Track data quality incidents and resolutions

Monitor:
- **Completeness**: Missing data checks
- **Accuracy**: Data validation rules
- **Consistency**: Cross-field validation
- **Timeliness**: Data freshness checks

## Troubleshooting

### 20. A Looker query is running slowly. How do you troubleshoot?

**Answer:** Performance troubleshooting:
1. **Check query**: Review generated SQL for inefficiencies
2. **Examine joins**: Look for Cartesian products or unnecessary joins
3. **Review filters**: Ensure filters are pushed to database
4. **Check caching**: See if query is hitting cache
5. **Database performance**: Check database query execution
6. **PDT usage**: Consider using persistent derived tables
7. **Query limits**: Check if hitting row or time limits

### 21. How do you handle LookML syntax errors?

**Answer:** Handling LookML errors:
1. **Validation**: Use Looker's validation tools
2. **Error messages**: Read error messages carefully
3. **Common issues**: Check for missing commas, incorrect field references
4. **Testing**: Test changes in development environment
5. **Version control**: Use Git to track changes and revert if needed
6. **Documentation**: Refer to LookML documentation for syntax

### 22. What are some common LookML anti-patterns?

**Answer:** Anti-patterns to avoid:
1. **Over-complex views**: Views with too many fields
2. **Redundant logic**: Duplicate calculations across views
3. **Poor naming**: Inconsistent or unclear field names
4. **Missing documentation**: Undocumented business logic
5. **No testing**: Critical logic without tests
6. **Security gaps**: Missing access controls
7. **Performance issues**: Unoptimized queries and joins
8. **Hardcoded values**: Values that should be configurable

## Architecture & Best Practices

### 23. How do you scale Looker for enterprise use?

**Answer:** Enterprise scaling:
1. **Model organization**: Break large models into smaller, focused models
2. **User management**: Implement groups and roles effectively
3. **Content organization**: Use folders and boards for content management
4. **Performance optimization**: Use PDTs, caching, and query optimization
5. **Governance**: Establish development and deployment processes
6. **Training**: Provide user training and documentation
7. **Support**: Set up internal support processes
8. **Integration**: Connect with enterprise systems and workflows

Focus on governance, performance, and user adoption for successful enterprise deployment.
