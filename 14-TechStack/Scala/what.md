# Scala: Comprehensive Guide

## Core Language Features

### Scala Fundamentals

Scala combines object-oriented and functional programming paradigms, running on the JVM. It provides concise syntax, powerful type inference, and seamless Java interoperability.

**Key Characteristics:**
- **Object-Oriented**: Everything is an object
- **Functional**: First-class functions, immutability, pattern matching
- **Statically Typed**: Type-safe with powerful type inference
- **JVM-Based**: Interoperable with Java libraries and frameworks
- **Concise**: Expressive syntax with less boilerplate

```scala
// Basic syntax and types
object HelloWorld {
  def main(args: Array[String]): Unit = {
    println("Hello, Scala!")

    // Variables and values
    val immutableValue: String = "Cannot change"
    var mutableVariable: Int = 42

    // Type inference
    val inferredString = "Scala infers types"
    val inferredNumber = 3.14

    // Basic data types
    val byteVal: Byte = 127
    val shortVal: Short = 32767
    val intVal: Int = 2147483647
    val longVal: Long = 9223372036854775807L
    val floatVal: Float = 3.14f
    val doubleVal: Double = 3.141592653589793
    val booleanVal: Boolean = true
    val charVal: Char = 'A'
    val stringVal: String = "Scala"
  }
}
```

### Control Structures

```scala
object ControlStructures {
  def main(args: Array[String]): Unit = {
    val x = 10
    val y = 20

    // If expressions (return values)
    val max = if (x > y) x else y
    val result = if (x % 2 == 0) "even" else "odd"

    // While loops
    var i = 0
    while (i < 5) {
      println(s"Count: $i")
      i += 1
    }

    // For comprehensions
    val numbers = List(1, 2, 3, 4, 5)

    // Basic for loop
    for (num <- numbers) {
      println(num)
    }

    // For with guards
    for (num <- numbers if num % 2 == 0) {
      println(s"Even: $num")
    }

    // For with multiple generators
    for {
      i <- 1 to 3
      j <- 1 to 3
      if i != j
    } yield (i, j)

    // Match expressions (pattern matching)
    def describeNumber(n: Int): String = n match {
      case 0 => "zero"
      case 1 => "one"
      case 2 => "two"
      case x if x > 0 => "positive"
      case x if x < 0 => "negative"
      case _ => "unknown"
    }

    println(describeNumber(5))  // "positive"
    println(describeNumber(-1)) // "negative"
  }
}
```

## Object-Oriented Programming

### Classes and Objects

```scala
// Case classes (immutable data structures)
case class Person(name: String, age: Int, email: Option[String] = None)

case class Address(street: String, city: String, zipCode: String)

case class Employee(
  person: Person,
  employeeId: String,
  department: String,
  salary: Double,
  address: Address
) {
  // Method definitions
  def fullName: String = person.name

  def isAdult: Boolean = person.age >= 18

  def monthlySalary: Double = salary / 12

  def promote(newSalary: Double): Employee = {
    this.copy(salary = newSalary)
  }

  def move(newAddress: Address): Employee = {
    this.copy(address = newAddress)
  }

  override def toString: String = {
    s"Employee(${person.name}, $employeeId, $department, $$${salary})"
  }
}

// Companion object (static methods and factory)
object Employee {
  def apply(name: String, age: Int, employeeId: String, department: String, salary: Double): Employee = {
    val person = Person(name, age)
    val defaultAddress = Address("Unknown", "Unknown", "00000")
    Employee(person, employeeId, department, salary, defaultAddress)
  }

  def createManager(name: String, age: Int, employeeId: String, department: String): Employee = {
    Employee(name, age, employeeId, department, 75000.0)
  }

  def createIntern(name: String, age: Int, employeeId: String, department: String): Employee = {
    require(age >= 18, "Intern must be at least 18 years old")
    Employee(name, age, employeeId, department, 25000.0)
  }
}

// Abstract classes
abstract class Vehicle(make: String, model: String, year: Int) {
  def start(): Unit
  def stop(): Unit
  def fuelEfficiency: Double // Abstract method

  def description: String = s"$year $make $model"
}

// Concrete implementation
class Car(make: String, model: String, year: Int, fuelType: String)
  extends Vehicle(make, model, year) {

  override def start(): Unit = println(s"Starting $make $model engine")
  override def stop(): Unit = println(s"Stopping $make $model engine")
  override def fuelEfficiency: Double = fuelType match {
    case "gasoline" => 25.0
    case "diesel" => 30.0
    case "electric" => 100.0
    case _ => 20.0
  }
}

// Usage example
object OOPExample {
  def main(args: Array[String]): Unit = {
    // Using case classes
    val person = Person("John Doe", 30, Some("john@example.com"))
    val address = Address("123 Main St", "Anytown", "12345")

    val employee = Employee(person, "EMP001", "Engineering", 80000.0, address)
    println(employee.fullName) // "John Doe"
    println(employee.isAdult)  // true

    // Using companion object factory methods
    val manager = Employee.createManager("Jane Smith", 35, "MGR001", "Engineering")
    val intern = Employee.createIntern("Bob Wilson", 22, "INT001", "Engineering")

    // Using abstract class
    val car = new Car("Toyota", "Camry", 2023, "gasoline")
    car.start()
    println(s"Fuel efficiency: ${car.fuelEfficiency} mpg")
    car.stop()
  }
}
```

### Inheritance and Polymorphism

```scala
// Base class
abstract class Animal(name: String, age: Int) {
  def speak(): String
  def move(): String
  def eat(food: String): String

  def describe: String = s"$name is $age years old"
}

// Interface-like behavior with traits
trait Pet {
  def play(): String
  def beFriendly(): String = "Wagging tail and being cute"
}

trait Domestic {
  def trained: Boolean
  def obedienceLevel: Int
}

// Concrete classes
class Dog(name: String, age: Int, breed: String)
  extends Animal(name, age) with Pet with Domestic {

  override def speak(): String = "Woof!"
  override def move(): String = "Running on four legs"
  override def eat(food: String): String = s"Eating $food hungrily"

  override def play(): String = "Fetching ball and chasing tail"
  override def trained: Boolean = true
  override def obedienceLevel: Int = 8

  def fetch(item: String): String = s"Fetching $item"
}

class Cat(name: String, age: Int, furColor: String)
  extends Animal(name, age) with Pet {

  override def speak(): String = "Meow!"
  override def move(): String = "Sneaking quietly"
  override def eat(food: String): String = s"Eating $food delicately"

  override def play(): String = "Chasing laser pointer"
  override def beFriendly(): String = "Purring and rubbing against legs"

  def scratch(): String = "Sharpening claws on furniture"
}

class WildAnimal(name: String, age: Int, species: String)
  extends Animal(name, age) {

  override def speak(): String = species match {
    case "lion" => "Roar!"
    case "elephant" => "Trumpet!"
    case "monkey" => "Chatter!"
    case _ => "Unknown sound"
  }

  override def move(): String = "Moving in natural habitat"
  override def eat(food: String): String = s"Hunting and eating $food"
}

// Polymorphism example
object PolymorphismExample {
  def interactWithAnimal(animal: Animal): Unit = {
    println(animal.describe)
    println(animal.speak())
    println(animal.move())
    println(animal.eat("food"))

    // Check if it's a pet
    animal match {
      case pet: Pet =>
        println(pet.play())
        println(pet.beFriendly())
      case _ =>
        println("This is a wild animal")
    }

    // Check if it's domestic
    animal match {
      case domestic: Domestic =>
        println(s"Trained: ${domestic.trained}, Obedience: ${domestic.obedienceLevel}")
      case _ =>
        println("Not a domestic animal")
    }

    println("---")
  }

  def main(args: Array[String]): Unit = {
    val dog = new Dog("Buddy", 3, "Golden Retriever")
    val cat = new Cat("Whiskers", 2, "Black")
    val lion = new WildAnimal("Simba", 5, "lion")

    val animals: List[Animal] = List(dog, cat, lion)

    animals.foreach(interactWithAnimal)
  }
}
```

## Functional Programming

### Higher-Order Functions

```scala
object HigherOrderFunctions {
  // Function types
  val add: (Int, Int) => Int = (a, b) => a + b
  val multiply: (Int, Int) => Int = _ * _
  val isEven: Int => Boolean = _ % 2 == 0
  val square: Int => Int = x => x * x

  // Function that takes a function as parameter
  def applyOperation(a: Int, b: Int, operation: (Int, Int) => Int): Int = {
    operation(a, b)
  }

  // Function that returns a function
  def getOperation(op: String): (Int, Int) => Int = op match {
    case "add" => _ + _
    case "multiply" => _ * _
    case "subtract" => _ - _
    case "divide" => _ / _
    case _ => throw new IllegalArgumentException(s"Unknown operation: $op")
  }

  // Currying
  def curriedAdd(a: Int)(b: Int): Int = a + b
  def curriedMultiply(a: Int)(b: Int): Int = a * b

  // Partial application
  val addFive = curriedAdd(5) _
  val multiplyByTen = curriedMultiply(_)(10)

  def main(args: Array[String]): Unit = {
    // Using higher-order functions
    println(applyOperation(5, 3, add))        // 8
    println(applyOperation(5, 3, multiply))   // 15

    // Using function from factory
    val subtractOp = getOperation("subtract")
    println(applyOperation(10, 3, subtractOp)) // 7

    // Currying and partial application
    println(curriedAdd(5)(3))    // 8
    println(addFive(3))          // 8
    println(multiplyByTen(5))    // 50

    // Function composition
    val addThenSquare = square compose add
    val squareThenAdd = add compose square

    println(addThenSquare(3, 4))  // (3+4)^2 = 49
    println(squareThenAdd(3, 4))  // 3^2 + 4 = 13
  }
}
```

### Collections and Immutability

```scala
object CollectionsExample {
  def main(args: Array[String]): Unit = {
    // Immutable collections (default)
    val numbers = List(1, 2, 3, 4, 5)
    val fruits = Set("apple", "banana", "orange")
    val capitals = Map("US" -> "Washington", "UK" -> "London", "France" -> "Paris")

    // Mutable collections (import scala.collection.mutable)
    // val mutableList = scala.collection.mutable.ListBuffer(1, 2, 3)
    // val mutableSet = scala.collection.mutable.HashSet("a", "b", "c")
    // val mutableMap = scala.collection.mutable.HashMap("key" -> "value")

    // List operations
    println("List operations:")
    println(numbers.head)        // 1
    println(numbers.tail)        // List(2, 3, 4, 5)
    println(numbers.last)        // 5
    println(numbers.init)        // List(1, 2, 3, 4)
    println(numbers.take(3))     // List(1, 2, 3)
    println(numbers.drop(2))     // List(3, 4, 5)
    println(numbers.filter(_ % 2 == 0))  // List(2, 4)
    println(numbers.map(_ * 2))           // List(2, 4, 6, 8, 10)
    println(numbers.reduce(_ + _))        // 15

    // Set operations
    println("\nSet operations:")
    val set1 = Set(1, 2, 3, 4)
    val set2 = Set(3, 4, 5, 6)
    println(set1 union set2)        // Set(1, 2, 3, 4, 5, 6)
    println(set1 intersect set2)    // Set(3, 4)
    println(set1 diff set2)         // Set(1, 2)
    println(set1 subsetOf Set(1, 2, 3, 4, 5))  // true

    // Map operations
    println("\nMap operations:")
    println(capitals.get("US"))           // Some(Washington)
    println(capitals.get("Germany"))      // None
    println(capitals.getOrElse("Germany", "Unknown"))  // Unknown
    println(capitals.keys)                // Set(US, UK, France)
    println(capitals.values)              // MapLike(Washington, London, Paris)

    // Advanced operations
    println("\nAdvanced operations:")

    // FlatMap
    val nestedLists = List(List(1, 2), List(3, 4), List(5, 6))
    println(nestedLists.flatMap(identity))  // List(1, 2, 3, 4, 5, 6)

    // GroupBy
    val words = List("hello", "world", "scala", "is", "awesome")
    val groupedByLength = words.groupBy(_.length)
    println(groupedByLength)  // Map(5 -> List(hello, world, scala), 2 -> List(is), 7 -> List(awesome))

    // Fold
    val sum = numbers.fold(0)(_ + _)
    val product = numbers.fold(1)(_ * _)
    println(s"Sum: $sum, Product: $product")  // Sum: 15, Product: 120

    // For comprehensions with collections
    val combinations = for {
      x <- List(1, 2, 3)
      y <- List(4, 5, 6)
      if x + y > 5
    } yield (x, y)

    println(combinations)  // List((1,5), (1,6), (2,4), (2,5), (2,6), (3,4), (3,5), (3,6))
  }
}
```

### Pattern Matching

```scala
// Sealed traits for exhaustive pattern matching
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(a: Double, b: Double, c: Double) extends Shape

sealed trait Expression
case class Number(value: Double) extends Expression
case class Variable(name: String) extends Expression
case class BinaryOp(left: Expression, op: String, right: Expression) extends Expression
case class FunctionCall(name: String, args: List[Expression]) extends Expression

object PatternMatchingExample {
  // Pattern matching on shapes
  def area(shape: Shape): Double = shape match {
    case Circle(r) => Math.PI * r * r
    case Rectangle(w, h) => w * h
    case Triangle(a, b, c) =>
      // Using Heron's formula
      val s = (a + b + c) / 2
      Math.sqrt(s * (s - a) * (s - b) * (s - c))
  }

  def perimeter(shape: Shape): Double = shape match {
    case Circle(r) => 2 * Math.PI * r
    case Rectangle(w, h) => 2 * (w + h)
    case Triangle(a, b, c) => a + b + c
  }

  // Pattern matching on expressions
  def evaluate(expr: Expression, variables: Map[String, Double] = Map()): Double = expr match {
    case Number(n) => n
    case Variable(name) => variables.getOrElse(name, 0.0)
    case BinaryOp(left, "+", right) => evaluate(left, variables) + evaluate(right, variables)
    case BinaryOp(left, "-", right) => evaluate(left, variables) - evaluate(right, variables)
    case BinaryOp(left, "*", right) => evaluate(left, variables) * evaluate(right, variables)
    case BinaryOp(left, "/", right) => evaluate(left, variables) / evaluate(right, variables)
    case FunctionCall("sin", List(arg)) => Math.sin(evaluate(arg, variables))
    case FunctionCall("cos", List(arg)) => Math.cos(evaluate(arg, variables))
    case FunctionCall("sqrt", List(arg)) => Math.sqrt(evaluate(arg, variables))
    case FunctionCall("pow", List(base, exp)) => Math.pow(evaluate(base, variables), evaluate(exp, variables))
    case _ => throw new IllegalArgumentException(s"Unknown expression: $expr")
  }

  // Pattern matching with guards
  def describeNumber(n: Int): String = n match {
    case x if x < 0 => s"$x is negative"
    case 0 => "zero"
    case 1 => "one"
    case 2 => "two"
    case 3 => "three"
    case x if x % 2 == 0 => s"$x is even"
    case x => s"$x is odd"
  }

  // Pattern matching on collections
  def processList(list: List[Int]): String = list match {
    case Nil => "Empty list"
    case head :: Nil => s"Single element: $head"
    case head :: tail => s"List starts with $head, has ${tail.length} more elements"
  }

  def processTuple(tuple: (Int, String)): String = tuple match {
    case (0, _) => "Zero with any string"
    case (_, "hello") => "Any number with hello"
    case (x, s) if x > 10 => s"Large number $x with $s"
    case (x, s) => s"Number $x with string $s"
  }

  // Extractor patterns
  object Email {
    def unapply(email: String): Option[(String, String)] = {
      val parts = email.split("@")
      if (parts.length == 2) Some((parts(0), parts(1))) else None
    }
  }

  def processEmail(email: String): String = email match {
    case Email(user, "gmail.com") => s"Gmail user: $user"
    case Email(user, domain) => s"User $user from domain $domain"
    case _ => "Invalid email"
  }

  def main(args: Array[String]): Unit = {
    // Shape examples
    val shapes = List(
      Circle(5.0),
      Rectangle(4.0, 6.0),
      Triangle(3.0, 4.0, 5.0)
    )

    shapes.foreach { shape =>
      println(f"Shape: $shape, Area: ${area(shape)}%.2f, Perimeter: ${perimeter(shape)}%.2f")
    }

    // Expression evaluation
    val expr = BinaryOp(
      BinaryOp(Number(3), "+", Variable("x")),
      "*",
      FunctionCall("sin", List(Number(Math.PI / 2)))
    )

    val variables = Map("x" -> 5.0)
    println(s"Expression result: ${evaluate(expr, variables)}")

    // Other pattern matching examples
    println(describeNumber(15))    // "15 is odd"
    println(describeNumber(8))     // "8 is even"
    println(processList(List(1, 2, 3)))  // "List starts with 1, has 2 more elements"
    println(processTuple((25, "world"))) // "Large number 25 with world"
    println(processEmail("john@gmail.com")) // "Gmail user: john"
  }
}
```

## Advanced Scala Features

### Implicits and Type Classes

```scala
// Type classes
trait Show[T] {
  def show(value: T): String
}

object Show {
  // Type class instances
  implicit val intShow: Show[Int] = (value: Int) => value.toString
  implicit val stringShow: Show[String] = (value: String) => s""""$value""""
  implicit val booleanShow: Show[Boolean] = (value: Boolean) => value.toString

  implicit def listShow[T](implicit showT: Show[T]): Show[List[T]] =
    (value: List[T]) => value.map(showT.show).mkString("[", ", ", "]")

  implicit def optionShow[T](implicit showT: Show[T]): Show[Option[T]] =
    (value: Option[T]) => value.map(showT.show).getOrElse("None")

  // Interface methods
  def show[T](value: T)(implicit showInstance: Show[T]): String =
    showInstance.show(value)
}

// Custom type class for ordering
trait Ord[T] {
  def compare(a: T, b: T): Int // -1 if a < b, 0 if equal, 1 if a > b

  def lt(a: T, b: T): Boolean = compare(a, b) < 0
  def gt(a: T, b: T): Boolean = compare(a, b) > 0
  def lte(a: T, b: T): Boolean = compare(a, b) <= 0
  def gte(a: T, b: T): Boolean = compare(a, b) >= 0
  def equiv(a: T, b: T): Boolean = compare(a, b) == 0
}

object Ord {
  implicit val intOrd: Ord[Int] = (a: Int, b: Int) => a.compare(b)
  implicit val stringOrd: Ord[String] = (a: String, b: String) => a.compare(b)

  implicit def optionOrd[T](implicit ordT: Ord[T]): Ord[Option[T]] = (a: Option[T], b: Option[T]) => (a, b) match {
    case (None, None) => 0
    case (None, Some(_)) => -1
    case (Some(_), None) => 1
    case (Some(x), Some(y)) => ordT.compare(x, y)
  }
}

// Implicit conversions
case class Celsius(value: Double)
case class Fahrenheit(value: Double)

object TemperatureConversions {
  implicit def celsiusToFahrenheit(c: Celsius): Fahrenheit =
    Fahrenheit(c.value * 9/5 + 32)

  implicit def fahrenheitToCelsius(f: Fahrenheit): Celsius =
    Celsius((f.value - 32) * 5/9)

  implicit class TemperatureOps(temp: Celsius) {
    def toFahrenheit: Fahrenheit = temp
    def isHot: Boolean = temp.value > 30
    def isCold: Boolean = temp.value < 10
  }
}

// Context bounds and implicit parameters
class Container[T: Show] {
  def showItems(items: List[T]): String = {
    Show.show(items)
  }
}

object TypeClassesExample {
  def main(args: Array[String]): Unit = {
    import TemperatureConversions._

    // Using Show type class
    println(Show.show(42))                    // "42"
    println(Show.show("hello"))               // ""hello""
    println(Show.show(List(1, 2, 3)))         // "[1, 2, 3]"
    println(Show.show(Some("test")))          // "Some("test")"
    println(Show.show(None))                  // "None"

    // Using Ord type class
    val ordInt = implicitly[Ord[Int]]
    println(ordInt.lt(5, 10))                 // true
    println(ordInt.gte(10, 5))                // true

    // Implicit conversions
    val celsius: Celsius = Celsius(25.0)
    val fahrenheit: Fahrenheit = celsius      // implicit conversion
    println(s"25°C = ${fahrenheit.value}°F")  // "25°C = 77.0°F"

    val temp: Celsius = Fahrenheit(77.0)      // implicit conversion
    println(temp.isHot)                       // false
    println(temp.isCold)                      // false

    // Context bounds
    val container = new Container[Int]
    println(container.showItems(List(1, 2, 3)))  // "[1, 2, 3]"
  }
}
```

### Futures and Concurrency

```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.duration._
import scala.util.{Success, Failure}
import ExecutionContext.Implicits.global

object FuturesExample {
  // Basic future creation
  def fetchUserData(userId: String): Future[User] = Future {
    // Simulate database call
    Thread.sleep(100)
    User(userId, s"User $userId", s"$userId@example.com")
  }

  def fetchUserPosts(userId: String): Future[List[Post]] = Future {
    // Simulate API call
    Thread.sleep(150)
    List(
      Post("1", userId, "First post", System.currentTimeMillis()),
      Post("2", userId, "Second post", System.currentTimeMillis())
    )
  }

  def fetchUserComments(userId: String): Future[List[Comment]] = Future {
    // Simulate API call
    Thread.sleep(80)
    List(
      Comment("1", userId, "Great post!", System.currentTimeMillis())
    )
  }

  // Sequential composition
  def getUserProfile(userId: String): Future[UserProfile] = {
    for {
      user <- fetchUserData(userId)
      posts <- fetchUserPosts(userId)
      comments <- fetchUserComments(userId)
    } yield UserProfile(user, posts, comments)
  }

  // Parallel composition
  def getUserProfileParallel(userId: String): Future[UserProfile] = {
    val userFuture = fetchUserData(userId)
    val postsFuture = fetchUserPosts(userId)
    val commentsFuture = fetchUserComments(userId)

    for {
      user <- userFuture
      posts <- postsFuture
      comments <- commentsFuture
    } yield UserProfile(user, posts, comments)
  }

  // Error handling
  def safeFetchUserData(userId: String): Future[User] = {
    if (userId.isEmpty) {
      Future.failed(new IllegalArgumentException("User ID cannot be empty"))
    } else {
      Future {
        if (userId == "error") {
          throw new RuntimeException("Simulated error")
        }
        Thread.sleep(100)
        User(userId, s"User $userId", s"$userId@example.com")
      }
    }
  }

  // Recovery and fallback
  def resilientFetchUserData(userId: String): Future[User] = {
    safeFetchUserData(userId).recover {
      case _: IllegalArgumentException =>
        User("default", "Default User", "default@example.com")
      case ex: RuntimeException =>
        println(s"Error fetching user $userId: ${ex.getMessage}")
        User("error", "Error User", "error@example.com")
    }
  }

  // Future combinators
  def findBestUser(userIds: List[String]): Future[Option[User]] = {
    val userFutures = userIds.map(id => resilientFetchUserData(id))

    Future.sequence(userFutures).map { users =>
      users.find(_.name.startsWith("User 1"))
    }
  }

  // Timeout handling
  def fetchWithTimeout[T](future: Future[T], timeout: FiniteDuration): Future[T] = {
    val timeoutFuture = Future {
      Thread.sleep(timeout.toMillis)
      throw new RuntimeException("Operation timed out")
    }

    Future.firstCompletedOf(List(future, timeoutFuture))
  }

  // Async/await style with for comprehensions
  def complexUserOperation(userId: String): Future[String] = {
    for {
      user <- resilientFetchUserData(userId)
      posts <- fetchUserPosts(userId) if user.email.contains("@example.com")
      comments <- fetchUserComments(userId)
    } yield {
      s"User ${user.name} has ${posts.length} posts and ${comments.length} comments"
    }
  }

  def main(args: Array[String]): Unit = {
    // Example usage
    val userId = "user123"

    // Sequential
    val profileFuture = getUserProfile(userId)
    profileFuture.onComplete {
      case Success(profile) =>
        println(s"Sequential: ${profile.user.name} has ${profile.posts.length} posts")
      case Failure(ex) =>
        println(s"Sequential failed: ${ex.getMessage}")
    }

    // Parallel
    val parallelProfileFuture = getUserProfileParallel(userId)
    parallelProfileFuture.onComplete {
      case Success(profile) =>
        println(s"Parallel: ${profile.user.name} has ${profile.posts.length} posts")
      case Failure(ex) =>
        println(s"Parallel failed: ${ex.getMessage}")
    }

    // Error handling
    val errorFuture = resilientFetchUserData("error")
    errorFuture.onComplete {
      case Success(user) => println(s"Error handling: ${user.name}")
      case Failure(ex) => println(s"Unexpected error: ${ex.getMessage}")
    }

    // Best user search
    val bestUserFuture = findBestUser(List("user1", "user2", "user3"))
    bestUserFuture.onComplete {
      case Success(Some(user)) => println(s"Best user: ${user.name}")
      case Success(None) => println("No best user found")
      case Failure(ex) => println(s"Search failed: ${ex.getMessage}")
    }

    // Complex operation
    val complexFuture = complexUserOperation(userId)
    complexFuture.onComplete {
      case Success(result) => println(s"Complex operation: $result")
      case Failure(ex) => println(s"Complex operation failed: ${ex.getMessage}")
    }

    // Keep the main thread alive
    Thread.sleep(2000)
  }
}

// Supporting case classes
case class User(id: String, name: String, email: String)
case class Post(id: String, userId: String, content: String, timestamp: Long)
case class Comment(id: String, userId: String, content: String, timestamp: Long)
case class UserProfile(user: User, posts: List[Post], comments: List[Comment])
```

### Scala Ecosystem

### Akka Actor System

```scala
import akka.actor.{Actor, ActorSystem, Props, ActorRef}
import akka.pattern.ask
import akka.util.Timeout
import scala.concurrent.duration._
import scala.concurrent.{Future, ExecutionContext}
import ExecutionContext.Implicits.global

// Messages
case class ProcessOrder(orderId: String, items: List[String])
case class OrderProcessed(orderId: String, total: Double)
case class PaymentRequest(amount: Double)
case class PaymentProcessed(success: Boolean)

// Order Processor Actor
class OrderProcessorActor extends Actor {
  def receive: Receive = {
    case ProcessOrder(orderId, items) =>
      println(s"Processing order $orderId with ${items.length} items")

      // Calculate total (simplified)
      val total = items.length * 10.0

      // Send payment request
      val paymentActor = context.actorOf(Props[PaymentActor], s"payment-$orderId")
      paymentActor ! PaymentRequest(total)

      // Become waiting for payment
      context.become(waitingForPayment(sender(), orderId, total))
  }

  def waitingForPayment(originalSender: ActorRef, orderId: String, total: Double): Receive = {
    case PaymentProcessed(true) =>
      println(s"Payment successful for order $orderId")
      originalSender ! OrderProcessed(orderId, total)
      context.stop(self)

    case PaymentProcessed(false) =>
      println(s"Payment failed for order $orderId")
      originalSender ! "Payment failed"
      context.stop(self)
  }
}

// Payment Actor
class PaymentActor extends Actor {
  def receive: Receive = {
    case PaymentRequest(amount) =>
      println(f"Processing payment of $$$amount%.2f")

      // Simulate payment processing
      val success = scala.util.Random.nextBoolean()

      // Simulate processing time
      Thread.sleep(100)

      sender() ! PaymentProcessed(success)
      context.stop(self)
  }
}

// Inventory Manager Actor
class InventoryManagerActor extends Actor {
  private var inventory = Map(
    "item1" -> 100,
    "item2" -> 50,
    "item3" -> 75
  )

  def receive: Receive = {
    case CheckInventory(itemId) =>
      val quantity = inventory.getOrElse(itemId, 0)
      sender() ! InventoryStatus(itemId, quantity)

    case ReserveItem(itemId, quantity) =>
      inventory.get(itemId) match {
        case Some(current) if current >= quantity =>
          inventory = inventory.updated(itemId, current - quantity)
          sender() ! ReservationSuccess(itemId, quantity)
        case _ =>
          sender() ! ReservationFailed(itemId, quantity)
      }
  }
}

// Messages for inventory
case class CheckInventory(itemId: String)
case class InventoryStatus(itemId: String, quantity: Int)
case class ReserveItem(itemId: String, quantity: Int)
case class ReservationSuccess(itemId: String, quantity: Int)
case class ReservationFailed(itemId: String, quantity: Int)

// Supervisor Actor
class OrderSupervisorActor extends Actor {
  val orderProcessor = context.actorOf(Props[OrderProcessorActor], "order-processor")
  val inventoryManager = context.actorOf(Props[InventoryManagerActor], "inventory-manager")

  def receive: Receive = {
    case order: ProcessOrder =>
      // Check inventory first
      val items = order.items
      val inventoryChecks = items.map(item => (inventoryManager ? CheckInventory(item)).mapTo[InventoryStatus])

      Future.sequence(inventoryChecks).onComplete {
        case scala.util.Success(statuses) =>
          val allAvailable = statuses.forall(_.quantity > 0)
          if (allAvailable) {
            // Reserve items
            val reservations = items.map(item => inventoryManager ? ReserveItem(item, 1))
            Future.sequence(reservations).onComplete {
              case scala.util.Success(_) =>
                orderProcessor ! order
              case scala.util.Failure(ex) =>
                sender() ! s"Reservation failed: ${ex.getMessage}"
            }
          } else {
            sender() ! "Items not available in inventory"
          }
        case scala.util.Failure(ex) =>
          sender() ! s"Inventory check failed: ${ex.getMessage}"
      }
  }
}

object AkkaExample {
  def main(args: Array[String]): Unit = {
    val system = ActorSystem("EcommerceSystem")

    val supervisor = system.actorOf(Props[OrderSupervisorActor], "supervisor")

    implicit val timeout = Timeout(5.seconds)

    // Process an order
    val order = ProcessOrder("order123", List("item1", "item2", "item3"))

    import scala.concurrent.ExecutionContext.Implicits.global

    (supervisor ? order).onComplete {
      case scala.util.Success(result) =>
        println(s"Order result: $result")
        system.terminate()
      case scala.util.Failure(ex) =>
        println(s"Order failed: ${ex.getMessage}")
        system.terminate()
    }

    // Keep main thread alive
    Thread.sleep(3000)
  }
}
```

### Play Framework Web Application

```scala
// app/controllers/HomeController.scala
package controllers

import javax.inject._
import play.api.mvc._
import play.api.data._
import play.api.data.Forms._
import scala.concurrent.{ExecutionContext, Future}
import models.User

case class LoginData(username: String, password: String)

@Singleton
class HomeController @Inject()(
  val controllerComponents: ControllerComponents
)(implicit ec: ExecutionContext) extends BaseController {

  // Form definition
  val loginForm = Form(
    mapping(
      "username" -> nonEmptyText,
      "password" -> nonEmptyText(minLength = 6)
    )(LoginData.apply)(LoginData.unapply)
  )

  // Action methods
  def index = Action { implicit request: Request[AnyContent] =>
    Ok(views.html.index("Welcome to Play Framework"))
  }

  def login = Action { implicit request =>
    Ok(views.html.login(loginForm))
  }

  def authenticate = Action.async { implicit request =>
    loginForm.bindFromRequest.fold(
      formWithErrors => {
        // Form validation failed
        Future.successful(BadRequest(views.html.login(formWithErrors)))
      },
      loginData => {
        // Simulate user authentication
        authenticateUser(loginData.username, loginData.password).map {
          case Some(user) =>
            Redirect(routes.HomeController.dashboard())
              .withSession("username" -> user.username)
          case None =>
            val formWithError = loginForm.fill(loginData)
              .withError("authentication", "Invalid username or password")
            BadRequest(views.html.login(formWithError))
        }
      }
    )
  }

  def dashboard = Action { implicit request =>
    request.session.get("username") match {
      case Some(username) =>
        Ok(views.html.dashboard(username))
      case None =>
        Redirect(routes.HomeController.login())
    }
  }

  def logout = Action { implicit request =>
    Redirect(routes.HomeController.index()).withNewSession
  }

  // API endpoints
  def users = Action.async {
    getAllUsers().map { users =>
      Ok(Json.toJson(users))
    }
  }

  def user(id: Long) = Action.async {
    getUserById(id).map {
      case Some(user) => Ok(Json.toJson(user))
      case None => NotFound(Json.obj("error" -> "User not found"))
    }
  }

  def createUser = Action.async(parse.json) { implicit request =>
    request.body.validate[User].fold(
      errors => {
        Future.successful(BadRequest(Json.obj("error" -> "Invalid JSON")))
      },
      user => {
        createUserInDb(user).map { createdUser =>
          Created(Json.toJson(createdUser))
        }
      }
    )
  }

  // Helper methods (would typically use a service layer)
  private def authenticateUser(username: String, password: String): Future[Option[User]] = {
    // Simulate database lookup
    Future.successful {
      if (username == "admin" && password == "password") {
        Some(User(1, username, s"$username@example.com"))
      } else {
        None
      }
    }
  }

  private def getAllUsers(): Future[List[User]] = {
    Future.successful(List(
      User(1, "john", "john@example.com"),
      User(2, "jane", "jane@example.com")
    ))
  }

  private def getUserById(id: Long): Future[Option[User]] = {
    Future.successful {
      if (id == 1) Some(User(1, "john", "john@example.com"))
      else if (id == 2) Some(User(2, "jane", "jane@example.com"))
      else None
    }
  }

  private def createUserInDb(user: User): Future[User] = {
    // Simulate database insertion
    Future.successful(user.copy(id = scala.util.Random.nextLong().abs))
  }
}

// app/models/User.scala
package models

import play.api.libs.json._

case class User(id: Long, username: String, email: String)

object User {
  implicit val userFormat: OFormat[User] = Json.format[User]
}

// conf/routes
# Routes
# This file defines all application routes (Higher priority routes first)
# https://www.playframework.com/documentation/latest/ScalaRouting

GET     /                           controllers.HomeController.index
GET     /login                     controllers.HomeController.login
POST    /authenticate              controllers.HomeController.authenticate
GET     /dashboard                 controllers.HomeController.dashboard
GET     /logout                    controllers.HomeController.logout

# API routes
GET     /api/users                 controllers.HomeController.users
GET     /api/users/:id             controllers.HomeController.user(id: Long)
POST    /api/users                 controllers.HomeController.createUser

# Map static resources from the /public folder to the /assets URL path
GET     /assets/*file               controllers.Assets.versioned(path="/public", file: Asset)
```

### Apache Spark with Scala

```scala
import org.apache.spark.sql.{SparkSession, DataFrame, Dataset}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import scala.util.Try

object SparkExample {
  def main(args: Array[String]): Unit = {
    // Create Spark session
    val spark = SparkSession.builder()
      .appName("Scala Spark Example")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    try {
      // Create sample data
      val salesData = Seq(
        ("2023-01-01", "product1", "customer1", 100.0, 2),
        ("2023-01-01", "product2", "customer1", 50.0, 1),
        ("2023-01-02", "product1", "customer2", 100.0, 1),
        ("2023-01-02", "product3", "customer2", 75.0, 3),
        ("2023-01-03", "product2", "customer3", 50.0, 2)
      )

      val salesDF = salesData.toDF("date", "product_id", "customer_id", "price", "quantity")

      // DataFrame operations
      println("=== Basic DataFrame Operations ===")

      // Show data
      salesDF.show()

      // Select specific columns
      salesDF.select("date", "product_id", "customer_id").show()

      // Filter data
      salesDF.filter($"price" > 60).show()

      // Group by and aggregate
      val salesByProduct = salesDF.groupBy("product_id")
        .agg(
          sum($"price" * $"quantity").as("total_sales"),
          sum($"quantity").as("total_quantity"),
          avg($"price").as("avg_price"),
          count("*").as("transaction_count")
        )
        .orderBy(desc("total_sales"))

      println("=== Sales by Product ===")
      salesByProduct.show()

      // Window functions
      val windowSpec = Window.partitionBy("customer_id").orderBy("date")

      val customerSalesWithRank = salesDF
        .withColumn("running_total", sum($"price" * $"quantity").over(windowSpec))
        .withColumn("rank", rank().over(windowSpec))

      println("=== Customer Sales with Running Total ===")
      customerSalesWithRank.show()

      // Dataset operations (typed)
      case class Sale(date: String, productId: String, customerId: String, price: Double, quantity: Int)

      val salesDS: Dataset[Sale] = salesDF.as[Sale]

      // Functional operations on Dataset
      val highValueSales = salesDS.filter(sale => sale.price * sale.quantity > 150)

      println("=== High Value Sales ===")
      highValueSales.show()

      // Complex transformations
      val customerSummary = salesDS
        .groupByKey(_.customerId)
        .mapGroups { (customerId, sales) =>
          val salesList = sales.toList
          val totalSpent = salesList.map(s => s.price * s.quantity).sum
          val totalItems = salesList.map(_.quantity).sum
          val uniqueProducts = salesList.map(_.productId).distinct.length
          val avgOrderValue = totalSpent / salesList.length

          CustomerSummary(customerId, totalSpent, totalItems, uniqueProducts, avgOrderValue)
        }

      println("=== Customer Summary ===")
      customerSummary.show()

      // SQL operations
      salesDF.createOrReplaceTempView("sales")

      val sqlResult = spark.sql("""
        SELECT
          customer_id,
          COUNT(*) as order_count,
          SUM(price * quantity) as total_spent,
          AVG(price * quantity) as avg_order_value,
          MAX(price * quantity) as max_order_value
        FROM sales
        GROUP BY customer_id
        ORDER BY total_spent DESC
      """)

      println("=== SQL Query Results ===")
      sqlResult.show()

      // DataFrame to RDD operations
      val salesRDD = salesDF.rdd

      val productRevenue = salesRDD
        .map(row => (row.getString(1), row.getDouble(3) * row.getInt(4)))
        .reduceByKey(_ + _)
        .sortBy(_._2, ascending = false)

      println("=== Product Revenue (RDD) ===")
      productRevenue.collect().foreach { case (product, revenue) =>
        println(f"$product: $$$revenue%.2f")
      }

      // Error handling with Try
      def safeDivision(a: Double, b: Double): Try[Double] = Try(a / b)

      val calculations = salesDS.map { sale =>
        val total = sale.price * sale.quantity
        val divisionResult = safeDivision(total, sale.quantity).getOrElse(0.0)
        (sale.productId, total, divisionResult)
      }

      println("=== Safe Calculations ===")
      calculations.show()

    } finally {
      spark.stop()
    }
  }
}

// Supporting case classes
case class CustomerSummary(
  customerId: String,
  totalSpent: Double,
  totalItems: Int,
  uniqueProducts: Int,
  avgOrderValue: Double
)
```

This comprehensive guide covers Scala fundamentals, object-oriented programming, functional programming, advanced features like implicits and type classes, concurrency with Futures, and key Scala ecosystem components including Akka actors, Play Framework, and Apache Spark integration.
