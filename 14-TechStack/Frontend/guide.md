# Frontend Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Tools Used for Front-End Development](#tools-used-for-front-end-development)
   - [HyperText Markup Language](#hypertext-markup-language)
   - [Cascading Style Sheets](#cascading-style-sheets)
   - [JavaScript](#javascript)
   - [WebAssembly](#webassembly)
3. [Goals for Development](#goals-for-development)
   - [Accessibility](#accessibility)
   - [Performance](#performance)
   - [Speedy Development](#speedy-development)

## Introduction
Front-end web development creates the graphical user interface of websites using HTML, CSS, and JavaScript for user interaction.

```mermaid
graph TD
    A[Website] --> B[GUI]
    B --> C[HTML]
    B --> D[CSS]
    B --> E[JavaScript]
    C --> F[Structure]
    D --> G[Style]
    E --> H[Interaction]
```

## Tools Used for Front-End Development

### HyperText Markup Language
HTML structures web content, defines elements and arrangement. Latest is HTML5.

```mermaid
graph TD
    A[HTML] --> B[Structure Content]
    A --> C[Define Elements]
    A --> D[Arrange Display]
    B --> E[Web Browsers Interpret]
```

### Cascading Style Sheets
CSS controls presentation and style, uses cascading for conflicts. Applied externally, internally, or inline.

```mermaid
graph TD
    A[CSS] --> B[Presentation]
    A --> C[Style]
    A --> D[Cascading System]
    D --> E[Specificity]
    D --> F[Inheritance]
    D --> G[Importance]
```

### JavaScript
Event-based language for dynamic interfaces, manipulates DOM, uses AJAX for content retrieval.

```mermaid
graph TD
    A[JavaScript] --> B[Event-Based]
    A --> C[Imperative]
    A --> D[DOM Manipulation]
    A --> E[AJAX]
    D --> F[Dynamic Interface]
    E --> G[Server Events]
```

### WebAssembly
Alternative to JavaScript for running code in browsers, compiled from languages like Rust, C, C++.

```mermaid
graph TD
    A[WebAssembly] --> B[Browser Code]
    A --> C[No Plug-ins]
    A --> D[Compiled from Languages]
    D --> E[Rust]
    D --> F[C]
    D --> G[C++]
```

## Goals for Development

### Accessibility
Ensure site works on all devices, using responsive web design with CSS media queries.

```mermaid
graph TD
    A[Accessibility] --> B[Mobile Devices]
    A --> C[Responsive Design]
    B --> D[Smartphones]
    B --> E[Tablets]
    C --> F[CSS Media Queries]
```

### Performance
Concerned with render time, manipulate HTML, CSS, JS for quick loading.

```mermaid
graph TD
    A[Performance] --> B[Render Time]
    A --> C[Manipulate HTML/CSS/JS]
    B --> D[Quick Open]
```

### Speedy Development
Enables fast development and saves time using available tools.

```mermaid
graph TD
    A[Speedy Development] --> B[Fast Creation]
    A --> C[Time Saving]
    B --> D[Tools Utilization]
```
