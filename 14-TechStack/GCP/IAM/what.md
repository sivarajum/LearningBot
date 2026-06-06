# IAM - What is it?

## Overview

Identity and Access Management (IAM) is Google Cloud's unified system for managing access to Google Cloud resources. It provides fine-grained access control and visibility for managing Google Cloud resources centrally. IAM lets you grant granular access to specific Google Cloud resources and helps prevent access to other resources.

## Core Concepts

### Identity Types
```
Google Cloud identities:
├── Google Account: Personal Google account
├── Service Account: Application identity for API access
├── Google Group: Collection of Google accounts and service accounts
├── Google Workspace Domain: All users in a Workspace domain
└── Cloud Identity Domain: Managed identities for organizations
```

### Resources and Permissions
- **Resources**: GCP services, projects, folders, organizations
- **Permissions**: Fine-grained actions on resources (e.g., `storage.objects.get`)
- **Roles**: Collections of permissions for common use cases

### Role Types
```
Three types of roles:
├── Basic roles: Owner, Editor, Viewer (project-level only)
├── Predefined roles: Curated by Google (e.g., roles/storage.admin)
└── Custom roles: User-defined combinations of permissions
```

## Role-Based Access Control (RBAC)

### Basic Roles
- **Owner**: Full access to all resources, can manage IAM policies
- **Editor**: Full access to all resources, cannot manage IAM policies
- **Viewer**: Read-only access to all resources

### Predefined Roles
Google provides curated roles for specific services:
- **Compute Engine roles**: `roles/compute.instanceAdmin`
- **Storage roles**: `roles/storage.objectAdmin`
- **BigQuery roles**: `roles/bigquery.dataEditor`

### Custom Roles
Create custom roles for specific organizational needs:
```json
{
  "title": "Custom Storage Role",
  "description": "Custom role for storage operations",
  "permissions": [
    "storage.buckets.get",
    "storage.objects.get",
    "storage.objects.list"
  ]
}
```

## IAM Policy Structure

### Policy Components
```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "user:alice@example.com",
        "serviceAccount:my-service@project.iam.gserviceaccount.com",
        "group:developers@example.com"
      ]
    }
  ]
}
```

### Policy Inheritance
- **Organization level**: Policies apply to all projects/folders
- **Folder level**: Policies apply to child folders/projects
- **Project level**: Policies apply to project resources
- **Resource level**: Policies apply to specific resources

Child policies can only restrict, not expand, parent permissions.

## Service Accounts

### Service Account Types
- **User-managed**: Created and managed by users
- **Google-managed**: Created by Google for GCP services
- **Default compute service account**: Automatic for Compute Engine

### Service Account Keys
- **Google-managed keys**: Automatically rotated by Google
- **User-managed keys**: Created by users (less secure, requires rotation)
- **Workload Identity**: Use Kubernetes service accounts

### Best Practices
- Use separate service accounts for different applications
- Grant minimal required permissions
- Rotate keys regularly
- Use Workload Identity for GKE

## Access Control Best Practices

### Principle of Least Privilege
- Grant only necessary permissions
- Use predefined roles when possible
- Regularly audit and remove unused access
- Implement just-in-time access for sensitive operations

### Separation of Duties
- Different roles for development, testing, production
- Separate security administration from system administration
- Use different service accounts for different environments

### Access Review Process
- Regular review of IAM policies
- Remove access for departed employees
- Audit service account usage
- Monitor for privilege escalation

## Advanced IAM Features

### Conditional Access
Apply conditions to role bindings:
```json
{
  "role": "roles/storage.objectViewer",
  "members": ["user:alice@example.com"],
  "condition": {
    "title": "Expires_2024",
    "expression": "request.time < timestamp('2024-01-01T00:00:00Z')"
  }
}
```

### IAM Recommender
- **Automated suggestions**: Identifies over-permissive access
- **Unused roles**: Detects roles not used in 90 days
- **Role recommendations**: Suggests appropriate predefined roles

### Policy Analyzer
- **Access analysis**: Shows effective permissions for principals
- **Policy insights**: Identifies overly permissive policies
- **Compliance checking**: Validates policies against requirements

## Security Features

### Multi-Factor Authentication (MFA)
- **Required for sensitive operations**: Enforced MFA for high-risk actions
- **Security key enforcement**: Require physical security keys
- **Context-aware access**: Risk-based access decisions

### Audit Logging
- **Admin Activity logs**: Track IAM policy changes
- **Data Access logs**: Monitor resource access
- **System Event logs**: Track system-level changes

### Integration with Security Tools
- **Security Command Center**: Centralized security monitoring
- **Access Transparency**: Independent audit of Google access
- **VPC Service Controls**: Network-level access control

## Organization and Project Structure

### Resource Hierarchy
```
Organization
├── Folders (optional)
│   ├── Projects
│   │   ├── Resources
│   └── Projects
└── Projects
    └── Resources
```

### Policy Inheritance Rules
- Policies flow down the hierarchy
- Child policies can only restrict permissions
- More specific policies take precedence
- Resource-level policies override project policies

## Integration with Identity Providers

### Google Workspace Integration
- **Automatic provisioning**: Workspace users get GCP access
- **Group-based access**: Use Workspace groups for IAM
- **SSO integration**: Single sign-on across Google services

### External Identity Providers
- **SAML 2.0**: Integration with enterprise identity providers
- **OIDC**: OpenID Connect for modern applications
- **LDAP**: Directory integration for legacy systems

## Compliance and Governance

### Compliance Features
- **Audit trails**: Complete access logging
- **Access reviews**: Automated and manual review processes
- **Compliance reporting**: Generate compliance reports
- **Data residency**: Control data location and access

### Governance Best Practices
- **Centralized IAM administration**: Use organization-level policies
- **Automated provisioning**: Use Terraform or Cloud Deployment Manager
- **Regular audits**: Automated policy analysis and reviews
- **Incident response**: Quick revocation of compromised credentials

## Common Use Cases

### Development Environment Access
- **Developers**: Editor access to development projects
- **Testers**: Viewer access with limited edit permissions
- **CI/CD systems**: Service accounts with deployment permissions

### Production Environment Security
- **Operators**: Limited production access with approval workflows
- **Security team**: Audit access to security tools
- **Application teams**: Access to their application resources only

### Multi-Cloud Access Management
- **Unified identity**: Use Cloud Identity for multi-cloud access
- **Federated access**: Single identity for GCP, AWS, Azure
- **Cross-cloud permissions**: Consistent access policies

### Service-to-Service Authentication
- **Service accounts**: Application-to-application authentication
- **Workload Identity**: Kubernetes pod authentication
- **Short-lived tokens**: Reduced credential exposure

## Cost and Management

### IAM Costs
- **Free for basic usage**: No cost for standard IAM operations
- **Audit log storage**: Costs for long-term audit log retention
- **Security Command Center**: Additional costs for advanced security features

### Management Tools
- **gcloud CLI**: Command-line IAM management
- **Cloud Console**: Web-based IAM interface
- **APIs**: Programmatic IAM administration
- **Terraform**: Infrastructure-as-code IAM management

IAM provides the foundation for secure, governed access to Google Cloud resources, enabling organizations to implement least-privilege access while maintaining operational efficiency and compliance requirements.
