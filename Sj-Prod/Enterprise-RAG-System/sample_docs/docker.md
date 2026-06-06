# Docker

## Overview

Docker is a platform for building, shipping, and running applications in containers. Containers package an application with all its dependencies into a standardized unit, ensuring it runs consistently across development, testing, and production environments.

## Key Concepts

### Images
A Docker image is a read-only template containing the application code, runtime, libraries, and system tools. Images are built from Dockerfiles using a layered filesystem. Each instruction in a Dockerfile creates a new layer, and layers are cached to speed up builds.

### Containers
A container is a running instance of an image. Containers are isolated from each other and the host system using Linux namespaces and cgroups. They share the host OS kernel, making them lightweight compared to virtual machines.

### Dockerfile
A Dockerfile is a text file with instructions for building an image. Common instructions include FROM (base image), COPY (add files), RUN (execute commands), EXPOSE (declare ports), and CMD (default command).

### Volumes
Volumes provide persistent storage for containers. Data in volumes survives container restarts and can be shared between containers. Bind mounts map a host directory into the container, while named volumes are managed by Docker.

## Docker Compose

Docker Compose is a tool for defining and running multi-container applications. You define services, networks, and volumes in a `docker-compose.yml` file and bring everything up with `docker-compose up`. This is ideal for local development environments and CI/CD pipelines.

## Best Practices

- Use multi-stage builds to keep images small
- Never store secrets in images; use environment variables or secret management tools
- Pin base image versions for reproducible builds
- Use `.dockerignore` to exclude unnecessary files from the build context
- Run containers as non-root users for security

## Container vs Virtual Machine

Containers share the host kernel and start in milliseconds, while VMs include a full guest OS and take minutes to boot. Containers use less memory and disk space, making them ideal for microservices. VMs provide stronger isolation and are better for running different operating systems.
