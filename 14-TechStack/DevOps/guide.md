# DevOps Guide

## Table of Contents
1. [Introduction](#introduction)
2. [History](#history)
3. [Relevant Metrics](#relevant-metrics)
4. [Relationship to Other Approaches](#relationship-to-other-approaches)
   - [Platform Engineering](#platform-engineering)
   - [Agile](#agile)
   - [ArchOps](#archops)
   - [CI/CD](#cicd)
   - [Database DevOps](#database-devops)
   - [Mobile DevOps](#mobile-devops)
   - [Site-Reliability Engineering](#site-reliability-engineering)
   - [Toyota Production System](#toyota-production-system)
   - [DevSecOps](#devsecops)
5. [Culture](#culture)
6. [GitOps](#gitops)
7. [Best Practices for Cloud Systems](#best-practices-for-cloud-systems)

## Introduction
DevOps integrates and automates software development and IT operations, shortening development time and improving the life cycle.

```mermaid
graph TD
    A[Software Development] --> B[DevOps]
    C[IT Operations] --> B
    B --> D[Automation]
    B --> E[Integration]
```

## History
Proposals began in late 80s and early 90s. DevOps Days in 2009, State of DevOps report in 2012, DORA metrics in 2016.

```mermaid
timeline
    1980s-90s : Proposals for Integration
    2009 : DevOps Days
    2012 : State of DevOps Report
    2014 : Adoption Accelerating
    2016 : DORA Metrics
```

## Relevant Metrics
Deployment Frequency, Lead Time for Changes, Change Failure Rate, Failed Deployment Recovery Time.

```mermaid
graph TD
    A[Metrics] --> B[Deployment Frequency]
    A --> C[Lead Time for Changes]
    A --> D[Change Failure Rate]
    A --> E[Failed Deployment Recovery Time]
```

## Relationship to Other Approaches

### Platform Engineering
Builds internal developer platforms with CI/CD, infrastructure, observability, security.

```mermaid
graph TD
    A[Platform Engineering] --> B[IDPs]
    B --> C[CI/CD]
    B --> D[Infrastructure]
    B --> E[Observability]
    B --> F[Security]
```

### Agile
Originated from Agile, focuses on deployment and operations.

```mermaid
graph TD
    A[Agile] --> B[Continuous Integration]
    A --> C[Continuous Delivery]
    B --> D[DevOps]
    C --> D
```

### ArchOps
Starts from software architecture artifacts for operation deployment.

```mermaid
graph TD
    A[ArchOps] --> B[Architecture Artifacts]
    B --> C[Operation Deployment]
```

### CI/CD
Automation for build, test, deployment. Critical for DevOps success.

```mermaid
graph LR
    A[Code] --> B[Build]
    B --> C[Test]
    C --> D[Deploy]
    D --> E[Monitor]
```

### Database DevOps
Applies DevOps to database development, using CI/CD for schema changes.

```mermaid
graph TD
    A[Database DevOps] --> B[Version Control]
    A --> C[Automated Tests]
    A --> D[CI/CD Pipelines]
```

### Mobile DevOps
Applies DevOps to mobile app development, tailored for mobile challenges.

```mermaid
graph TD
    A[Mobile DevOps] --> B[Mobile-Specific Practices]
    B --> C[Streamlined Delivery]
```

### Site-Reliability Engineering
Related to SRE, focuses on high-availability systems.

```mermaid
graph TD
    A[SRE] --> B[High-Availability]
    A --> C[Continuous Features]
    B --> D[DevOps]
    C --> D
```

### Toyota Production System
Inspired by TPS, lean thinking, kaizen, continuous improvement.

```mermaid
graph TD
    A[TPS] --> B[Lean Thinking]
    A --> C[Kaizen]
    B --> D[DevOps]
    C --> D
```

### DevSecOps
Integrates security practices, shifting security left.

```mermaid
graph TD
    A[DevSecOps] --> B[Security Integration]
    A --> C[Shift Left]
    B --> D[SAST]
    B --> E[DAST]
    B --> F[SCA]
```

## Culture
Shared ownership, workflow automation, rapid feedback. Supports consistency, reliability, efficiency.

```mermaid
graph TD
    A[Culture] --> B[Shared Ownership]
    A --> C[Workflow Automation]
    A --> D[Rapid Feedback]
    B --> E[Collaboration]
    C --> F[Efficiency]
    D --> G[Improvement]
```

## GitOps
Deployment configuration version-controlled using Git. Changes managed via code review.

```mermaid
graph TD
    A[GitOps] --> B[Version Control]
    A --> C[Code Review]
    A --> D[Rollback]
    B --> E[Deployment State]
```

## Best Practices for Cloud Systems
Small teams use one repository and pipeline. Larger organizations separate by team or service. Principle of least privilege for permissions.

```mermaid
graph TD
    A[Best Practices] --> B[One Repo/Pipeline for Small Teams]
    A --> C[Separate for Large Orgs]
    A --> D[Least Privilege Permissions]
```
