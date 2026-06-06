# Scala Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Scala
# Download from scala-lang.org

# Install sbt
# Download from scala-sbt.org

# Create project
sbt new scala/hello-world.g8
```

### 2. **Basic Syntax**
```scala
// Variables
val name = "John"  // Immutable
var age = 30      // Mutable

// Functions
def greet(name: String): String = {
    s"Hello, $name!"
}

// Classes
class Person(val name: String, val age: Int)
```

### 3. **Collections**
```scala
val list = List(1, 2, 3)
val map = Map("key" -> "value")
val set = Set(1, 2, 3)
```

## Level 2 – Production Patterns

### Functional Programming
```scala
val result = list
    .filter(_ > 1)
    .map(_ * 2)
    .reduce(_ + _)
```

### Pattern Matching
```scala
val result = value match {
    case 1 => "one"
    case 2 => "two"
    case _ => "other"
}
```

## Level 3 – Architect Playbook

### Akka
```scala
import akka.actor.Actor

class MyActor extends Actor {
    def receive = {
        case msg: String => println(msg)
    }
}
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Compile | `sbt compile` | Compile project |
| Run | `sbt run` | Run application |
| Test | `sbt test` | Run tests |

## Checklist Before Production

- [ ] Set up sbt project
- [ ] Implement proper error handling
- [ ] Set up logging
- [ ] Write tests
- [ ] Document code
- [ ] Set up CI/CD
- [ ] Optimize performance
