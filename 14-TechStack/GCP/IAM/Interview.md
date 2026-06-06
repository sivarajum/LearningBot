# IAM - Interview Questions & Answers

## Core IAM Concepts

### 1. Explain the difference between authentication and authorization in GCP.

**Answer:** Authentication and authorization are distinct security concepts:

- **Authentication**: Verifying identity ("Who are you?")
  - Methods: Google accounts, service accounts, SAML, OIDC
  - GCP services: Cloud Identity, Google Workspace

- **Authorization**: Granting permissions ("What can you do?")
  - Methods: IAM roles, policies, permissions
  - GCP service: Cloud IAM

Authentication confirms identity, authorization determines access rights. IAM handles both, but they're separate processes.

### 2. What are the three types of IAM roles and when would you use each?

**Answer:** The three role types:

- **Basic roles**: Owner, Editor, Viewer
  - Use: Simple projects, small teams
  - Scope: Project-level only
  - Permissions: Broad, all-or-nothing access

- **Predefined roles**: Google-curated roles (e.g., `roles/storage.admin`)
  - Use: Most common scenarios
  - Scope: Service-specific permissions
  - Permissions: Curated by Google for security

- **Custom roles**: User-defined permission combinations
  - Use: Specific organizational requirements
  - Scope: Fine-grained control
  - Permissions: Exact permissions needed

Use predefined roles when possible, custom roles for specific needs.

### 3. How does IAM policy inheritance work in GCP?

**Answer:** IAM policy inheritance follows the resource hierarchy:

```
Organization → Folders → Projects → Resources
```

- **Inheritance flow**: Policies flow down from parent to child
- **Restriction rule**: Child policies can only restrict, not expand permissions
- **Precedence**: More specific policies override general ones
- **Resource-level**: Most specific policies apply to individual resources

Example: Organization grants broad access, project restricts to specific users.

## Role Design & Permissions

### 4. How would you design IAM roles for a development team?

**Answer:** Development team role design:

1. **Separate environments**: Different roles for dev/staging/prod
2. **Least privilege**: Grant minimal required permissions
3. **Job functions**: Different roles for developers, testers, DevOps
4. **Service accounts**: Separate accounts for CI/CD pipelines

Example roles:
- `Developer`: Editor access to dev project
- `Tester`: Viewer + limited edit in staging
- `DevOps`: Deployment permissions across environments

### 5. What permissions are included in the `roles/viewer` role?

**Answer:** The `roles/viewer` role includes read-only permissions for most GCP services:

- **Compute Engine**: View instances, disks, networks
- **Storage**: List and view objects
- **BigQuery**: View datasets, tables, query jobs
- **Monitoring**: View metrics and logs

It does NOT include:
- Any write/modify/create permissions
- IAM policy management
- Billing account access

### 6. How do you create and manage custom roles?

**Answer:** Custom role creation process:

1. **Identify permissions**: List exact permissions needed
2. **Create role**: Use gcloud or Console
3. **Test role**: Assign to test user/service account
4. **Deploy role**: Assign to production users
5. **Monitor usage**: Track role effectiveness
6. **Update as needed**: Modify permissions based on requirements

Custom roles are project/organization-specific and support up to 64KB of permissions.

## Service Accounts

### 7. When should you use service accounts vs user accounts?

**Answer:** Use service accounts for:

- **Application authentication**: API access from code
- **Automated processes**: CI/CD pipelines, batch jobs
- **Cross-project access**: Accessing resources across projects
- **Headless operations**: No human interaction required

Use user accounts for:
- **Interactive access**: Console, gcloud CLI usage
- **Human operations**: Manual tasks and troubleshooting
- **Personal accountability**: Audit trails with individual users

### 8. How do you secure service account keys?

**Answer:** Service account key security:

1. **Use Google-managed keys**: Auto-rotated, no manual management
2. **Workload Identity**: Use for GKE pods instead of keys
3. **Short-lived credentials**: Use OAuth 2.0 tokens
4. **Key rotation**: Rotate user-managed keys every 90 days
5. **Access control**: Restrict who can create/use keys
6. **Monitoring**: Audit service account usage

Avoid long-lived keys when possible.

### 9. Explain Workload Identity and when to use it.

**Answer:** Workload Identity allows Kubernetes service accounts to act as GCP service accounts:

- **How it works**: Binds K8s service account to GCP service account
- **Benefits**: No key management, automatic token rotation
- **Use cases**: GKE applications needing GCP access
- **Setup**: Enable on GKE cluster, create IAM policy binding

Use for containerized applications in GKE instead of service account keys.

## Access Control Scenarios

### 10. How do you implement least privilege access?

**Answer:** Least privilege implementation:

1. **Assess requirements**: Document exactly what access is needed
2. **Start minimal**: Grant basic permissions, add as needed
3. **Use predefined roles**: Prefer curated roles over custom
4. **Regular audits**: Review and remove unused access
5. **Just-in-time access**: Grant temporary elevated access
6. **Separation of duties**: Different people for different functions

Monitor usage and adjust permissions based on actual needs.

### 11. How do you handle access for contractors or temporary employees?

**Answer:** Temporary access management:

1. **Time-bound access**: Use conditional IAM policies with expiration
2. **Separate accounts**: Don't use personal accounts
3. **Limited scope**: Grant access only to required resources
4. **Monitoring**: Enable detailed audit logging
5. **Automated revocation**: Set up automatic access removal
6. **Approval workflow**: Require manager approval for access

Use Google Cloud Identity for external user management.

### 12. Explain how to implement multi-environment access control.

**Answer:** Multi-environment access:

- **Development**: Broad editor access for developers
- **Staging**: Limited access, focus on testing
- **Production**: Read-only + approved changes only
- **Service accounts**: Separate accounts per environment
- **Cross-environment access**: Restricted to CI/CD systems

Use project-level policies with different permission levels per environment.

## Security Best Practices

### 13. What are some common IAM security mistakes and how to avoid them?

**Answer:** Common mistakes:

1. **Over-permissive roles**: Using Owner role everywhere
   - Fix: Use least privilege, audit with IAM Recommender

2. **Shared service accounts**: Multiple applications using same account
   - Fix: Create separate service accounts per application

3. **Long-lived keys**: Never-rotated service account keys
   - Fix: Use Workload Identity or short-lived tokens

4. **No MFA**: Missing multi-factor authentication
   - Fix: Enable MFA for all users

5. **No access reviews**: Unused access never removed
   - Fix: Regular access reviews and automated cleanup

### 14. How do you detect and respond to IAM security incidents?

**Answer:** IAM incident response:

1. **Detection**: Monitor for unusual access patterns
2. **Investigation**: Review audit logs for suspicious activity
3. **Containment**: Revoke compromised credentials immediately
4. **Recovery**: Rotate affected keys and passwords
5. **Analysis**: Determine root cause and attack vector
6. **Prevention**: Implement additional security controls

Use Security Command Center for automated detection.

### 15. How do you implement conditional access policies?

**Answer:** Conditional access implementation:

```json
{
  "role": "roles/storage.admin",
  "members": ["user:alice@domain.com"],
  "condition": {
    "title": "Business Hours Only",
    "expression": "request.time.getHours() >= 9 && request.time.getHours() <= 17"
  }
}
```

Use for:
- **Time-based access**: Business hours only
- **IP restrictions**: Corporate network only
- **Device compliance**: Approved devices only

## Compliance & Auditing

### 16. How do you ensure IAM compliance with regulations like SOX or GDPR?

**Answer:** IAM compliance:

1. **Access reviews**: Regular review of all access rights
2. **Audit logging**: Enable detailed audit logs
3. **Separation of duties**: Different people for different roles
4. **Access controls**: Implement least privilege
5. **Monitoring**: Continuous monitoring of access patterns
6. **Documentation**: Maintain access control documentation

Use IAM Policy Analyzer for compliance checking.

### 17. What audit logs are available for IAM and how do you use them?

**Answer:** IAM audit logs:

- **Admin Activity**: IAM policy changes, role assignments
- **Data Access**: Resource access by authenticated users
- **System Event**: GCP system changes affecting access

Use for:
- **Security monitoring**: Detect unauthorized access attempts
- **Compliance reporting**: Prove access controls are working
- **Troubleshooting**: Debug access issues
- **Forensic analysis**: Investigate security incidents

### 18. How do you implement automated IAM policy management?

**Answer:** Automated IAM management:

1. **Infrastructure as Code**: Use Terraform for IAM policies
2. **CI/CD integration**: Automated policy deployment
3. **Policy as Code**: Define policies in version control
4. **Automated testing**: Test policies before deployment
5. **Drift detection**: Monitor for policy changes outside automation

Benefits: Consistency, auditability, faster deployment.

## Advanced Scenarios

### 19. How do you handle IAM in a multi-cloud environment?

**Answer:** Multi-cloud IAM:

1. **Central identity**: Use Cloud Identity for unified identities
2. **Federation**: Connect to other cloud providers
3. **Consistent roles**: Map permissions across clouds
4. **SSO integration**: Single sign-on across all clouds
5. **Access monitoring**: Unified monitoring and auditing

Use Google Cloud Identity as the central identity provider.

### 20. Explain how to implement just-in-time access.

**Answer:** Just-in-time (JIT) access:

1. **Normal state**: Minimal permissions for daily work
2. **Elevation request**: User requests temporary elevated access
3. **Approval workflow**: Manager or automated approval
4. **Time-limited access**: Automatic revocation after time expires
5. **Audit logging**: Full audit trail of access elevation

Use conditional IAM policies or third-party tools for JIT implementation.

### 21. How do you manage IAM for microservices architectures?

**Answer:** Microservices IAM:

1. **Service accounts**: Each service has its own account
2. **Workload Identity**: Use for containerized services
3. **Service mesh**: Istio integration for service-to-service auth
4. **API gateways**: Centralized authentication and authorization
5. **Token-based auth**: Short-lived tokens between services

Implement zero-trust security with continuous verification.

### 22. What are some IAM anti-patterns to avoid?

**Answer:** IAM anti-patterns:

1. **Role explosion**: Too many custom roles
2. **Permission creep**: Gradually accumulating excessive permissions
3. **Shared credentials**: Multiple users sharing accounts
4. **Hardcoded secrets**: API keys in code
5. **No key rotation**: Never-rotated credentials
6. **Over-reliance on basic roles**: Using Owner/Editor everywhere
7. **No access monitoring**: Not monitoring who accesses what

### 23. How do you migrate IAM policies from another cloud provider?

**Answer:** IAM migration process:

1. **Assess current state**: Document existing permissions
2. **Map identities**: Create corresponding GCP identities
3. **Translate roles**: Map permissions to GCP roles
4. **Create policies**: Implement IAM policies in GCP
5. **Test access**: Verify functionality in GCP
6. **Migrate applications**: Update code to use GCP authentication
7. **Cutover**: Switch to GCP with minimal downtime
8. **Audit and optimize**: Review and refine permissions

Focus on maintaining security while enabling functionality.
