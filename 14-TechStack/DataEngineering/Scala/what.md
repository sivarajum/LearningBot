# Scala for Data Engineering: Comprehensive Guide

## Overview

Scala is a modern multi-paradigm programming language that combines object-oriented and functional programming. It runs on the JVM and is the primary language for Apache Spark, making it essential for big data processing and distributed computing.

## Core Concepts

### What is Scala for Data Engineering?

Scala is a modern multi-paradigm programming language that combines object-oriented and functional programming. It runs on the JVM and is the primary language for Apache Spark, making it essential for big data processing and distributed computing.

## Key Features

**JVM Compatibility**: Runs on Java Virtual Machine

**Functional Programming**: Immutability and higher-order functions

**Type Safety**: Strong static typing with type inference

**Spark Integration**: Native support for Apache Spark

**Concurrency**: Actor model with Akka

**Expressiveness**: Concise syntax for complex operations

## Installation

# Install Scala
# macOS
brew install scala

# Ubuntu/Debian
sudo apt install scala

# Install sbt (Scala Build Tool)
# macOS
brew install sbt

# Ubuntu/Debian
echo "deb https://repo.scala-sbt.org/scalasbt/debian all main" | sudo tee /etc/apt/sources.list.d/sbt.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
sudo apt update
sudo apt install sbt

# Verify
scala -version
sbt sbtVersion

## Getting Started

```scala
// Basic Scala class
case class Person(name: String, age: Int)

// Functional programming
val numbers = List(1, 2, 3, 4, 5)
val doubled = numbers.map(_ * 2)
val evens = numbers.filter(_ % 2 == 0)
val sum = numbers.reduce(_ + _)

// Pattern matching
def process(person: Person): String = person match {
  case Person(name, age) if age < 18 => s"$name is a minor"
  case Person(name, age) => s"$name is an adult"
}
```

## Advanced Usage

```scala
// Spark with Scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession.builder()
  .appName("DataProcessing")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

val df = spark.read
  .option("header", "true")
  .csv("data.csv")

df.filter($"age" > 18)
  .groupBy("city")
  .agg(avg("salary"))
  .show()
```

## Best Practices

1. Prefer immutability (val over var, case classes)
2. Use pattern matching for control flow
3. Leverage higher-order functions (map, filter, reduce)
4. Use Option for nullable values
5. Follow functional programming principles
6. Use sbt for dependency management
7. Write idiomatic Scala code, not Java in Scala syntax

## References

- Official documentation: 
- GitHub repository:
