# Java Programming Language Guide

## Table of Contents
1. [Introduction](#introduction)
2. [History](#history)
3. [Principles](#principles)
4. [Versions](#versions)
5. [Editions](#editions)
6. [Execution System](#execution-system)
7. [Syntax](#syntax)
8. [Special Classes](#special-classes)
9. [Class Libraries](#class-libraries)
10. [Implementations](#implementations)

## Introduction
Java is a high-level, general-purpose, memory-safe, object-oriented programming language designed for write once, run anywhere (WORA) functionality.

```mermaid
graph TD
    A[Java Language] --> B[Compiled to Bytecode]
    B --> C[Runs on JVM]
    C --> D[Any Platform]
```

## History
Java was created by James Gosling at Sun Microsystems in 1991, initially for interactive television, but evolved into a general-purpose language.

```mermaid
timeline
    title Java History Timeline
    1991 : Oak Project Started
    1995 : Java 1.0 Released
    1998 : Java 2 (J2SE)
    2004 : Java 5.0 with Generics
    2011 : Java 7
    2014 : Java 8 (LTS)
    2018 : Java 11 (LTS)
    2021 : Java 17 (LTS)
    2023 : Java 21 (LTS)
    2025 : Java 25 (LTS)
```

## Principles
Five primary goals: simple, object-oriented, robust, secure, architecture-neutral, portable, high-performance, interpreted, threaded, dynamic.

```mermaid
mindmap
  root((Java Principles))
    Simple
    Object-Oriented
    Robust
    Secure
    Architecture-Neutral
    Portable
    High-Performance
    Interpreted
    Threaded
    Dynamic
```

## Versions
Major versions include Java 8, 11, 17, 21, 25 as LTS versions.

```mermaid
gantt
    title Java LTS Versions
    dateFormat YYYY
    section LTS Versions
    Java 8     :done, 2014, 2014
    Java 11    :done, 2018, 2018
    Java 17    :done, 2021, 2021
    Java 21    :done, 2023, 2023
    Java 25    :done, 2025, 2025
```

## Editions
Java Card for smart-cards, Java ME for limited resources, Java SE for workstations, Java EE for enterprise environments.

```mermaid
graph LR
    A[Java Editions] --> B[Java Card]
    A --> C[Java ME]
    A --> D[Java SE]
    A --> E[Java EE]
```

## Execution System
Java uses JVM for portability, bytecode compilation, JIT compilation, automatic garbage collection.

```mermaid
flowchart TD
    A[Java Source] --> B[Compiler]
    B --> C[Bytecode]
    C --> D[JVM]
    D --> E[Machine Code]
    D --> F[Garbage Collector]
```

## Syntax
Influenced by C/C++, object-oriented, no operator overloading or multiple inheritance for classes.

```mermaid
stateDiagram-v2
    [*] --> Class
    Class --> Method
    Method --> Statement
    Statement --> [*]
    note right of Class : public class HelloWorld
    note right of Method : public static void main
    note right of Statement : System.out.println
```

## Special Classes
Includes Applets (deprecated), Servlets for web, JSP for server-side, Swing for GUI, JavaFX for rich apps, Generics for type safety.

```mermaid
graph TD
    A[Special Classes] --> B[Applet]
    A --> C[Servlet]
    A --> D[JSP]
    A --> E[Swing]
    A --> F[JavaFX]
    A --> G[Generics]
```

## Class Libraries
Core libraries: I/O, Networking, Reflection, Concurrent, Generics, Functional. Integration: JDBC, JNDI, RMI, JMX. UI: AWT, Swing, JavaFX.

```mermaid
mindmap
  root((Class Libraries))
    Core
      I/O
      Networking
      Reflection
      Concurrent
      Generics
      Functional
    Integration
      JDBC
      JNDI
      RMI
      JMX
    UI
      AWT
      Swing
      JavaFX
```

## Implementations
Oracle provides official JDK/JRE, OpenJDK is open-source reference implementation.

```mermaid
graph LR
    A[Implementations] --> B[Oracle JDK]
    A --> C[OpenJDK]
    B --> D[Proprietary]
    C --> E[GPL License]
```
