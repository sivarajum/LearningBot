# Java: Comprehensive Guide

## Core Language Features

### Java Fundamentals

Java is a high-level, object-oriented programming language that is platform-independent, thanks to the Java Virtual Machine (JVM). It emphasizes readability, simplicity, and robustness.

**Key Characteristics:**
- **Object-Oriented**: Everything revolves around objects and classes
- **Platform-Independent**: "Write once, run anywhere" via JVM
- **Statically Typed**: Type checking at compile time
- **Automatic Memory Management**: Garbage collection
- **Multithreaded**: Built-in support for concurrent programming
- **Secure**: Sandbox environment for applets and applications

```java
// Basic syntax and structure
public class HelloWorld {
    // Entry point of the application
    public static void main(String[] args) {
        System.out.println("Hello, Java!");

        // Variables and data types
        // Primitive types
        boolean isJavaFun = true;
        byte smallNumber = 127;
        short shortNumber = 32767;
        int integerNumber = 2147483647;
        long longNumber = 9223372036854775807L;
        float floatNumber = 3.14f;
        double doubleNumber = 3.141592653589793;
        char character = 'J';

        // Reference types
        String greeting = "Hello, World!";
        Object obj = new Object();

        // Arrays
        int[] numbers = {1, 2, 3, 4, 5};
        String[] names = new String[3];
        names[0] = "Java";
        names[1] = "Python";
        names[2] = "Scala";

        // Control structures
        if (isJavaFun) {
            System.out.println("Java is fun!");
        }

        for (int i = 0; i < numbers.length; i++) {
            System.out.println("Number: " + numbers[i]);
        }

        // Enhanced for loop
        for (String name : names) {
            System.out.println("Language: " + name);
        }

        // Switch statement (Java 14+ with arrows)
        String day = "MONDAY";
        String typeOfDay = switch (day) {
            case "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY" -> "Weekday";
            case "SATURDAY", "SUNDAY" -> "Weekend";
            default -> "Unknown";
        };
        System.out.println(day + " is a " + typeOfDay);
    }
}
```

### Object-Oriented Programming

#### Classes and Objects

```java
import java.time.LocalDate;
import java.util.Objects;

// Base class
public abstract class Person {
    // Instance variables
    private String name;
    private LocalDate dateOfBirth;
    protected String nationality;

    // Static variable
    public static final String SPECIES = "Homo sapiens";

    // Constructor
    public Person(String name, LocalDate dateOfBirth) {
        this.name = name;
        this.dateOfBirth = dateOfBirth;
        this.nationality = "Unknown";
    }

    // Copy constructor
    public Person(Person other) {
        this.name = other.name;
        this.dateOfBirth = other.dateOfBirth;
        this.nationality = other.nationality;
    }

    // Abstract method
    public abstract String getOccupation();

    // Concrete methods
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public LocalDate getDateOfBirth() {
        return dateOfBirth;
    }

    public int getAge() {
        return LocalDate.now().getYear() - dateOfBirth.getYear();
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    // Static method
    public static Person createAnonymous() {
        return new Person("Anonymous", LocalDate.now()) {
            @Override
            public String getOccupation() {
                return "Unknown";
            }
        };
    }

    // toString, equals, and hashCode
    @Override
    public String toString() {
        return String.format("Person{name='%s', age=%d, nationality='%s'}",
                           name, getAge(), nationality);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return Objects.equals(name, person.name) &&
               Objects.equals(dateOfBirth, person.dateOfBirth);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, dateOfBirth);
    }
}

// Concrete subclass
public class Employee extends Person {
    private String employeeId;
    private String department;
    private double salary;
    private Employee manager;

    // Constructor chaining
    public Employee(String name, LocalDate dateOfBirth, String employeeId,
                   String department, double salary) {
        super(name, dateOfBirth);
        this.employeeId = employeeId;
        this.department = department;
        this.salary = salary;
    }

    // Method overriding
    @Override
    public String getOccupation() {
        return "Employee in " + department;
    }

    // Additional methods
    public String getEmployeeId() {
        return employeeId;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public double getSalary() {
        return salary;
    }

    public void setSalary(double salary) {
        if (salary >= 0) {
            this.salary = salary;
        }
    }

    public Employee getManager() {
        return manager;
    }

    public void setManager(Employee manager) {
        this.manager = manager;
    }

    public void giveRaise(double percentage) {
        if (percentage > 0) {
            this.salary *= (1 + percentage / 100);
        }
    }

    @Override
    public String toString() {
        return String.format("Employee{employeeId='%s', name='%s', department='%s', salary=%.2f}",
                           employeeId, getName(), department, salary);
    }
}

// Usage example
public class OOPExample {
    public static void main(String[] args) {
        // Create objects
        Employee emp1 = new Employee("John Doe", LocalDate.of(1990, 5, 15),
                                   "EMP001", "Engineering", 75000.0);
        Employee emp2 = new Employee("Jane Smith", LocalDate.of(1985, 8, 20),
                                   "EMP002", "Marketing", 65000.0);

        // Set relationships
        emp1.setManager(emp2);

        // Demonstrate polymorphism
        Person[] people = {emp1, emp2};
        for (Person person : people) {
            System.out.println(person.getName() + " - " + person.getOccupation());
        }

        // Demonstrate inheritance
        System.out.println("John's age: " + emp1.getAge());
        emp1.giveRaise(10);
        System.out.println("John's new salary: $" + emp1.getSalary());

        // Static method usage
        Person anonymous = Person.createAnonymous();
        System.out.println("Anonymous person: " + anonymous);
    }
}
```

#### Interfaces and Abstract Classes

```java
import java.util.List;
import java.util.ArrayList;
import java.util.function.Predicate;

// Interface with default and static methods
interface Vehicle {
    // Abstract methods
    String getMake();
    String getModel();
    int getYear();
    void start();
    void stop();

    // Default methods (Java 8+)
    default String getDescription() {
        return String.format("%d %s %s", getYear(), getMake(), getModel());
    }

    default boolean isClassic() {
        return (2023 - getYear()) >= 25;
    }

    // Static methods (Java 8+)
    static Vehicle createDefault() {
        return new Vehicle() {
            @Override
            public String getMake() { return "Unknown"; }
            @Override
            public String getModel() { return "Unknown"; }
            @Override
            public int getYear() { return 2000; }
            @Override
            public void start() { System.out.println("Starting unknown vehicle"); }
            @Override
            public void stop() { System.out.println("Stopping unknown vehicle"); }
        };
    }
}

// Interface for comparable objects
interface Comparable<T> {
    int compareTo(T other);
}

// Interface with generics
interface Repository<T, ID> {
    T findById(ID id);
    List<T> findAll();
    T save(T entity);
    void deleteById(ID id);
    boolean existsById(ID id);
}

// Abstract class implementing interface
abstract class AbstractVehicle implements Vehicle {
    protected String make;
    protected String model;
    protected int year;

    public AbstractVehicle(String make, String model, int year) {
        this.make = make;
        this.model = model;
        this.year = year;
    }

    @Override
    public String getMake() { return make; }
    @Override
    public String getModel() { return model; }
    @Override
    public int getYear() { return year; }

    // Abstract method to be implemented by subclasses
    @Override
    public abstract void start();

    @Override
    public abstract void stop();

    // Additional abstract method
    public abstract double getFuelEfficiency();
}

// Concrete implementation
class Car extends AbstractVehicle implements Comparable<Car> {
    private String fuelType;
    private double fuelEfficiency;

    public Car(String make, String model, int year, String fuelType, double fuelEfficiency) {
        super(make, model, year);
        this.fuelType = fuelType;
        this.fuelEfficiency = fuelEfficiency;
    }

    @Override
    public void start() {
        System.out.println("Starting " + getDescription() + " with " + fuelType + " engine");
    }

    @Override
    public void stop() {
        System.out.println("Stopping " + getDescription());
    }

    @Override
    public double getFuelEfficiency() {
        return fuelEfficiency;
    }

    public String getFuelType() {
        return fuelType;
    }

    @Override
    public int compareTo(Car other) {
        // Compare by year, then by make, then by model
        int yearComparison = Integer.compare(this.year, other.year);
        if (yearComparison != 0) return yearComparison;

        int makeComparison = this.make.compareTo(other.make);
        if (makeComparison != 0) return makeComparison;

        return this.model.compareTo(other.model);
    }

    @Override
    public String toString() {
        return String.format("Car{make='%s', model='%s', year=%d, fuelType='%s', mpg=%.1f}",
                           make, model, year, fuelType, fuelEfficiency);
    }
}

// Generic repository implementation
class InMemoryRepository<T, ID> implements Repository<T, ID> {
    private List<T> entities = new ArrayList<>();
    private java.util.Map<ID, T> idToEntity = new java.util.HashMap<>();

    // This is a simplified implementation - in reality, you'd need proper ID extraction
    @Override
    public T findById(ID id) {
        return idToEntity.get(id);
    }

    @Override
    public List<T> findAll() {
        return new ArrayList<>(entities);
    }

    @Override
    public T save(T entity) {
        entities.add(entity);
        // Simplified - assuming ID can be derived or is part of entity
        return entity;
    }

    @Override
    public void deleteById(ID id) {
        T entity = idToEntity.remove(id);
        if (entity != null) {
            entities.remove(entity);
        }
    }

    @Override
    public boolean existsById(ID id) {
        return idToEntity.containsKey(id);
    }
}

// Usage example
public class InterfacesExample {
    public static void main(String[] args) {
        // Create vehicles
        Car car1 = new Car("Toyota", "Camry", 2020, "gasoline", 32.5);
        Car car2 = new Car("Honda", "Civic", 2019, "gasoline", 36.2);
        Car car3 = new Car("Tesla", "Model 3", 2021, "electric", 132.0);

        // Demonstrate interface methods
        Vehicle[] vehicles = {car1, car2, car3};
        for (Vehicle vehicle : vehicles) {
            System.out.println(vehicle.getDescription());
            vehicle.start();
            vehicle.stop();
            System.out.println("Is classic: " + vehicle.isClassic());
            System.out.println();
        }

        // Demonstrate comparable
        List<Car> cars = List.of(car1, car2, car3);
        cars.stream()
            .sorted()
            .forEach(System.out::println);

        // Demonstrate repository pattern
        Repository<Car, String> carRepo = new InMemoryRepository<>();
        carRepo.save(car1);
        carRepo.save(car2);

        System.out.println("All cars: " + carRepo.findAll().size());
        System.out.println("Car exists: " + carRepo.existsById("some-id"));
    }
}
```

## Collections Framework

### Core Collections

```java
import java.util.*;

public class CollectionsExample {
    public static void main(String[] args) {
        // List implementations
        List<String> arrayList = new ArrayList<>();
        List<String> linkedList = new LinkedList<>();
        List<String> vector = new Vector<>(); // Thread-safe

        // Set implementations
        Set<String> hashSet = new HashSet<>(); // No order
        Set<String> linkedHashSet = new LinkedHashSet<>(); // Insertion order
        Set<String> treeSet = new TreeSet<>(); // Sorted order

        // Map implementations
        Map<String, Integer> hashMap = new HashMap<>();
        Map<String, Integer> linkedHashMap = new LinkedHashMap<>();
        Map<String, Integer> treeMap = new TreeMap<>();

        // Queue implementations
        Queue<String> linkedListQueue = new LinkedList<>();
        Queue<String> priorityQueue = new PriorityQueue<>();
        Deque<String> arrayDeque = new ArrayDeque<>();

        // Working with ArrayList
        System.out.println("=== ArrayList Operations ===");
        arrayList.add("Apple");
        arrayList.add("Banana");
        arrayList.add("Cherry");
        arrayList.add(1, "Apricot"); // Insert at index

        System.out.println("List: " + arrayList);
        System.out.println("Size: " + arrayList.size());
        System.out.println("Contains 'Banana': " + arrayList.contains("Banana"));
        System.out.println("Index of 'Cherry': " + arrayList.indexOf("Cherry"));

        // Iteration methods
        System.out.println("For-each loop:");
        for (String fruit : arrayList) {
            System.out.println("  " + fruit);
        }

        System.out.println("Iterator:");
        Iterator<String> iterator = arrayList.iterator();
        while (iterator.hasNext()) {
            System.out.println("  " + iterator.next());
        }

        System.out.println("ListIterator (backward):");
        ListIterator<String> listIterator = arrayList.listIterator(arrayList.size());
        while (listIterator.hasPrevious()) {
            System.out.println("  " + listIterator.previous());
        }

        // Working with HashSet
        System.out.println("\n=== HashSet Operations ===");
        hashSet.add("Red");
        hashSet.add("Green");
        hashSet.add("Blue");
        hashSet.add("Red"); // Duplicate - will be ignored

        System.out.println("Set: " + hashSet);
        System.out.println("Size: " + hashSet.size());

        // Working with HashMap
        System.out.println("\n=== HashMap Operations ===");
        hashMap.put("John", 25);
        hashMap.put("Jane", 30);
        hashMap.put("Bob", 35);

        System.out.println("Map: " + hashMap);
        System.out.println("John's age: " + hashMap.get("John"));
        System.out.println("Contains key 'Alice': " + hashMap.containsKey("Alice"));
        System.out.println("Contains value 30: " + hashMap.containsValue(30));

        // Iterate over map
        System.out.println("Entry set:");
        for (Map.Entry<String, Integer> entry : hashMap.entrySet()) {
            System.out.println("  " + entry.getKey() + " -> " + entry.getValue());
        }

        // Working with PriorityQueue
        System.out.println("\n=== PriorityQueue Operations ===");
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        pq.add(30);
        pq.add(10);
        pq.add(20);
        pq.add(5);

        System.out.println("PriorityQueue: " + pq);
        System.out.println("Poll (removes head): " + pq.poll());
        System.out.println("After poll: " + pq);
        System.out.println("Peek (doesn't remove): " + pq.peek());
    }
}
```

### Advanced Collections Operations

```java
import java.util.*;
import java.util.stream.Collectors;

public class AdvancedCollectionsExample {
    public static void main(String[] args) {
        // Sample data
        List<Employee> employees = Arrays.asList(
            new Employee("John", "Engineering", 75000),
            new Employee("Jane", "Marketing", 65000),
            new Employee("Bob", "Engineering", 80000),
            new Employee("Alice", "HR", 55000),
            new Employee("Charlie", "Engineering", 70000)
        );

        // Traditional iteration and filtering
        System.out.println("=== Traditional Approach ===");
        List<Employee> engineeringEmployees = new ArrayList<>();
        for (Employee emp : employees) {
            if ("Engineering".equals(emp.getDepartment())) {
                engineeringEmployees.add(emp);
            }
        }
        System.out.println("Engineering employees: " + engineeringEmployees.size());

        // Using Collections utility methods
        System.out.println("\n=== Collections Utilities ===");

        // Sorting
        List<Employee> sortedBySalary = new ArrayList<>(employees);
        Collections.sort(sortedBySalary, Comparator.comparingDouble(Employee::getSalary));
        System.out.println("Sorted by salary (first 2): " +
                          sortedBySalary.subList(0, 2).stream()
                              .map(emp -> emp.getName() + ": $" + emp.getSalary())
                              .collect(Collectors.joining(", ")));

        // Binary search (requires sorted list)
        Collections.sort(sortedBySalary, Comparator.comparing(Employee::getName));
        int index = Collections.binarySearch(sortedBySalary,
                                           new Employee("Jane", "", 0),
                                           Comparator.comparing(Employee::getName));
        System.out.println("Jane found at index: " + index);

        // Reverse and shuffle
        Collections.reverse(sortedBySalary);
        System.out.println("Reversed order (first 2): " +
                          sortedBySalary.subList(0, 2).stream()
                              .map(Employee::getName)
                              .collect(Collectors.joining(", ")));

        Collections.shuffle(sortedBySalary);
        System.out.println("Shuffled order (first 2): " +
                          sortedBySalary.subList(0, 2).stream()
                              .map(Employee::getName)
                              .collect(Collectors.joining(", ")));

        // Finding min/max
        Employee highestPaid = Collections.max(employees, Comparator.comparingDouble(Employee::getSalary));
        Employee lowestPaid = Collections.min(employees, Comparator.comparingDouble(Employee::getSalary));
        System.out.println("Highest paid: " + highestPaid.getName() + " ($" + highestPaid.getSalary() + ")");
        System.out.println("Lowest paid: " + lowestPaid.getName() + " ($" + lowestPaid.getSalary() + ")");

        // Frequency
        List<String> departments = employees.stream()
                                          .map(Employee::getDepartment)
                                          .collect(Collectors.toList());
        int engineeringCount = Collections.frequency(departments, "Engineering");
        System.out.println("Engineering employees: " + engineeringCount);

        // Unmodifiable collections
        List<Employee> unmodifiableList = Collections.unmodifiableList(employees);
        try {
            unmodifiableList.add(new Employee("Test", "Test", 0));
        } catch (UnsupportedOperationException e) {
            System.out.println("Cannot modify unmodifiable collection: " + e.getMessage());
        }

        // Synchronized collections (thread-safe)
        List<Employee> synchronizedList = Collections.synchronizedList(new ArrayList<>(employees));
        System.out.println("Synchronized list created");

        // Custom comparators
        System.out.println("\n=== Custom Comparators ===");

        // Multiple field comparison
        Comparator<Employee> byDeptThenSalary = Comparator
            .comparing(Employee::getDepartment)
            .thenComparingDouble(Employee::getSalary);

        List<Employee> sortedByDeptAndSalary = new ArrayList<>(employees);
        sortedByDeptAndSalary.sort(byDeptThenSalary);

        System.out.println("Sorted by department then salary:");
        sortedByDeptAndSalary.forEach(emp ->
            System.out.println("  " + emp.getDepartment() + " - " + emp.getName() + ": $" + emp.getSalary()));

        // Null-safe comparison
        Comparator<Employee> nullSafeComparator = Comparator
            .nullsLast(Comparator.comparing(Employee::getDepartment,
                          Comparator.nullsLast(Comparator.naturalOrder())));

        // Grouping with Maps
        System.out.println("\n=== Grouping Operations ===");
        Map<String, List<Employee>> employeesByDept = employees.stream()
            .collect(Collectors.groupingBy(Employee::getDepartment));

        employeesByDept.forEach((dept, emps) -> {
            double avgSalary = emps.stream()
                                 .mapToDouble(Employee::getSalary)
                                 .average()
                                 .orElse(0.0);
            System.out.println(dept + ": " + emps.size() + " employees, avg salary: $" + String.format("%.2f", avgSalary));
        });

        // Partitioning
        Map<Boolean, List<Employee>> partitionedBySalary = employees.stream()
            .collect(Collectors.partitioningBy(emp -> emp.getSalary() > 65000));

        System.out.println("High salary (>65000): " +
                          partitionedBySalary.get(true).stream()
                              .map(Employee::getName)
                              .collect(Collectors.joining(", ")));
        System.out.println("Low salary (<=65000): " +
                          partitionedBySalary.get(false).stream()
                              .map(Employee::getName)
                              .collect(Collectors.joining(", ")));
    }

    static class Employee {
        private String name;
        private String department;
        private double salary;

        public Employee(String name, String department, double salary) {
            this.name = name;
            this.department = department;
            this.salary = salary;
        }

        public String getName() { return name; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }

        @Override
        public String toString() {
            return name + " (" + department + ", $" + salary + ")";
        }
    }
}
```

## Generics

### Generic Classes and Methods

```java
import java.util.*;
import java.util.function.Function;

// Generic class
public class Pair<T, U> {
    private T first;
    private U second;

    public Pair(T first, U second) {
        this.first = first;
        this.second = second;
    }

    public T getFirst() { return first; }
    public U getSecond() { return second; }

    public void setFirst(T first) { this.first = first; }
    public void setSecond(U second) { this.second = second; }

    public Pair<U, T> swap() {
        return new Pair<>(second, first);
    }

    @Override
    public String toString() {
        return "(" + first + ", " + second + ")";
    }

    // Static generic method
    public static <T, U> Pair<T, U> of(T first, U second) {
        return new Pair<>(first, second);
    }
}

// Generic interface
interface Processor<T, R> {
    R process(T input);
}

// Generic class with bounded types
class NumberProcessor<T extends Number> implements Processor<T, Double> {
    @Override
    public Double process(T input) {
        return input.doubleValue() * 2;
    }
}

// Generic method with wildcards
class CollectionUtils {
    // Upper bounded wildcard
    public static double sumOfList(List<? extends Number> list) {
        return list.stream().mapToDouble(Number::doubleValue).sum();
    }

    // Lower bounded wildcard
    public static void addNumbers(List<? super Integer> list) {
        list.add(1);
        list.add(2);
        list.add(3);
    }

    // Unbounded wildcard
    public static void printList(List<?> list) {
        list.forEach(System.out::println);
    }

    // Generic method
    public static <T> List<T> reverse(List<T> list) {
        List<T> reversed = new ArrayList<>(list);
        Collections.reverse(reversed);
        return reversed;
    }

    // Generic method with multiple type parameters
    public static <T, R> List<R> map(List<T> list, Function<T, R> mapper) {
        return list.stream().map(mapper).collect(java.util.stream.Collectors.toList());
    }
}

// Generic container with type erasure demonstration
class GenericContainer<T> {
    private T value;

    public GenericContainer(T value) {
        this.value = value;
    }

    public T getValue() {
        return value;
    }

    public void setValue(T value) {
        this.value = value;
    }

    // This method demonstrates type erasure - T is erased to Object at runtime
    public boolean isInstanceOf(Class<?> clazz) {
        return clazz.isInstance(clazz.cast(value));
    }
}

// Type inference examples
class TypeInference {
    public static <T> T pick(T a, T b) {
        return a; // Just return first one
    }

    public static <T> List<T> emptyList() {
        return new ArrayList<>();
    }

    // Diamond operator (Java 7+)
    public static List<String> createStringList() {
        return new ArrayList<>(); // Type inferred
    }
}

public class GenericsExample {
    public static void main(String[] args) {
        // Basic generic usage
        Pair<String, Integer> pair = new Pair<>("Age", 25);
        System.out.println("Pair: " + pair);
        System.out.println("Swapped: " + pair.swap());

        // Static factory method
        Pair<Double, String> anotherPair = Pair.of(3.14, "PI");
        System.out.println("Factory pair: " + anotherPair);

        // Bounded types
        NumberProcessor<Integer> intProcessor = new NumberProcessor<>();
        NumberProcessor<Double> doubleProcessor = new NumberProcessor<>();
        System.out.println("Integer processed: " + intProcessor.process(5));
        System.out.println("Double processed: " + doubleProcessor.process(3.5));

        // Wildcards
        List<Integer> integers = Arrays.asList(1, 2, 3, 4, 5);
        List<Double> doubles = Arrays.asList(1.1, 2.2, 3.3);
        List<Number> numbers = new ArrayList<>();

        System.out.println("Sum of integers: " + CollectionUtils.sumOfList(integers));
        System.out.println("Sum of doubles: " + CollectionUtils.sumOfList(doubles));

        CollectionUtils.addNumbers(numbers);
        CollectionUtils.printList(numbers);

        // Generic methods
        List<String> strings = Arrays.asList("a", "b", "c");
        List<String> reversed = CollectionUtils.reverse(strings);
        System.out.println("Reversed: " + reversed);

        List<Integer> lengths = CollectionUtils.map(strings, String::length);
        System.out.println("Lengths: " + lengths);

        // Type inference
        String result = TypeInference.pick("Hello", "World");
        List<String> emptyStrings = TypeInference.emptyList();
        List<String> stringList = TypeInference.createStringList();

        System.out.println("Picked: " + result);
        System.out.println("Empty list type: " + emptyStrings.getClass().getSimpleName());
        System.out.println("String list type: " + stringList.getClass().getSimpleName());
    }
}
```

## Exception Handling

### Exception Hierarchy and Handling

```java
import java.io.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;

// Custom exception classes
class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }

    public InvalidAgeException(String message, Throwable cause) {
        super(message, cause);
    }
}

class InsufficientFundsException extends Exception {
    private double amount;
    private double balance;

    public InsufficientFundsException(double amount, double balance) {
        super(String.format("Insufficient funds. Requested: $%.2f, Available: $%.2f", amount, balance));
        this.amount = amount;
        this.balance = balance;
    }

    public double getAmount() { return amount; }
    public double getBalance() { return balance; }
}

// Bank account class demonstrating exception handling
class BankAccount {
    private String accountNumber;
    private double balance;
    private List<String> transactionHistory;

    public BankAccount(String accountNumber, double initialBalance) throws InvalidAgeException {
        if (initialBalance < 0) {
            throw new InvalidAgeException("Initial balance cannot be negative: " + initialBalance);
        }
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
        this.transactionHistory = new ArrayList<>();
        transactionHistory.add("Account created with balance: $" + initialBalance);
    }

    public void deposit(double amount) throws IllegalArgumentException {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive: " + amount);
        }
        balance += amount;
        transactionHistory.add("Deposit: $" + amount + ", Balance: $" + balance);
    }

    public void withdraw(double amount) throws InsufficientFundsException, IllegalArgumentException {
        if (amount <= 0) {
            throw new IllegalArgumentException("Withdrawal amount must be positive: " + amount);
        }
        if (amount > balance) {
            throw new InsufficientFundsException(amount, balance);
        }
        balance -= amount;
        transactionHistory.add("Withdrawal: $" + amount + ", Balance: $" + balance);
    }

    public double getBalance() {
        return balance;
    }

    public List<String> getTransactionHistory() {
        return new ArrayList<>(transactionHistory);
    }
}

// Service class with comprehensive exception handling
class BankingService {
    private Map<String, BankAccount> accounts;

    public BankingService() {
        this.accounts = new HashMap<>();
    }

    public void createAccount(String accountNumber, double initialBalance) {
        try {
            BankAccount account = new BankAccount(accountNumber, initialBalance);
            accounts.put(accountNumber, account);
            System.out.println("Account created successfully: " + accountNumber);
        } catch (InvalidAgeException e) {
            System.err.println("Failed to create account: " + e.getMessage());
            throw new RuntimeException("Account creation failed", e);
        }
    }

    public void transfer(String fromAccount, String toAccount, double amount) {
        BankAccount sourceAccount = accounts.get(fromAccount);
        BankAccount targetAccount = accounts.get(toAccount);

        if (sourceAccount == null) {
            throw new IllegalArgumentException("Source account not found: " + fromAccount);
        }
        if (targetAccount == null) {
            throw new IllegalArgumentException("Target account not found: " + toAccount);
        }

        try {
            sourceAccount.withdraw(amount);
            targetAccount.deposit(amount);
            System.out.println("Transfer successful: $" + amount + " from " + fromAccount + " to " + toAccount);
        } catch (InsufficientFundsException e) {
            System.err.println("Transfer failed: " + e.getMessage());
            throw new RuntimeException("Transfer failed due to insufficient funds", e);
        } catch (IllegalArgumentException e) {
            System.err.println("Transfer failed: " + e.getMessage());
            throw e;
        }
    }

    public void processBatchTransactions(List<Runnable> transactions) {
        for (Runnable transaction : transactions) {
            try {
                transaction.run();
            } catch (Exception e) {
                System.err.println("Transaction failed: " + e.getMessage());
                // Continue processing other transactions
            }
        }
    }
}

// File processing with exception handling
class FileProcessor {
    public List<String> readFile(String filePath) throws IOException {
        List<String> lines = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + filePath);
            throw new IOException("Cannot read file", e);
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            throw e;
        }

        return lines;
    }

    public void writeFile(String filePath, List<String> lines) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            for (String line : lines) {
                writer.write(line);
                writer.newLine();
            }
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
            throw e;
        }
    }

    // Try-with-resources with multiple resources
    public void copyFile(String sourcePath, String destPath) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(sourcePath));
             BufferedWriter writer = new BufferedWriter(new FileWriter(destPath))) {

            String line;
            while ((line = reader.readLine()) != null) {
                writer.write(line);
                writer.newLine();
            }

        } catch (FileNotFoundException e) {
            throw new IOException("File copy failed: source or destination not accessible", e);
        } catch (IOException e) {
            throw new IOException("File copy failed due to I/O error", e);
        }
    }
}

public class ExceptionHandlingExample {
    public static void main(String[] args) {
        BankingService bankingService = new BankingService();
        FileProcessor fileProcessor = new FileProcessor();

        // Demonstrate checked exceptions
        try {
            bankingService.createAccount("ACC001", 1000.0);
            bankingService.createAccount("ACC002", 500.0);

            bankingService.transfer("ACC001", "ACC002", 200.0);
            System.out.println("Transfer completed successfully");

            // This will fail
            bankingService.transfer("ACC001", "ACC002", 1000.0);

        } catch (RuntimeException e) {
            System.err.println("Banking operation failed: " + e.getMessage());
        }

        // Demonstrate file processing with exceptions
        try {
            List<String> sampleData = Arrays.asList(
                "Line 1: Sample data",
                "Line 2: More data",
                "Line 3: Final line"
            );

            fileProcessor.writeFile("sample.txt", sampleData);
            List<String> readData = fileProcessor.readFile("sample.txt");

            System.out.println("File contents:");
            readData.forEach(System.out::println);

            fileProcessor.copyFile("sample.txt", "copy.txt");
            System.out.println("File copied successfully");

        } catch (IOException e) {
            System.err.println("File operation failed: " + e.getMessage());
        }

        // Demonstrate multi-catch and finally
        try {
            // Some operation that might throw different exceptions
            Integer.parseInt("not-a-number");
        } catch (NumberFormatException | IllegalArgumentException e) {
            System.err.println("Parsing failed: " + e.getMessage());
        } finally {
            System.out.println("Cleanup operations would go here");
        }

        // Demonstrate suppressed exceptions (Java 7+)
        try {
            tryWithSuppressedExceptions();
        } catch (Exception e) {
            System.err.println("Main exception: " + e.getMessage());
            for (Throwable suppressed : e.getSuppressed()) {
                System.err.println("Suppressed: " + suppressed.getMessage());
            }
        }
    }

    private static void tryWithSuppressedExceptions() throws Exception {
        try (AutoCloseable resource1 = () -> { throw new Exception("Resource1 close failed"); };
             AutoCloseable resource2 = () -> { throw new Exception("Resource2 close failed"); }) {

            throw new Exception("Main operation failed");
        }
    }
}
```

## Concurrency and Multithreading

### Thread Creation and Management

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.*;
import java.util.stream.IntStream;

// Basic thread creation
class SimpleThread extends Thread {
    private String name;

    public SimpleThread(String name) {
        this.name = name;
    }

    @Override
    public void run() {
        System.out.println(name + " is running");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            System.out.println(name + " was interrupted");
        }
        System.out.println(name + " is finished");
    }
}

// Runnable implementation
class Worker implements Runnable {
    private int id;

    public Worker(int id) {
        this.id = id;
    }

    @Override
    public void run() {
        System.out.println("Worker " + id + " started");
        try {
            // Simulate work
            Thread.sleep(500 + id * 100);
        } catch (InterruptedException e) {
            System.out.println("Worker " + id + " interrupted");
        }
        System.out.println("Worker " + id + " finished");
    }
}

// Shared resource with synchronization
class Counter {
    private int count = 0;

    // Synchronized method
    public synchronized void increment() {
        count++;
    }

    // Synchronized block
    public void incrementWithBlock() {
        synchronized (this) {
            count++;
        }
    }

    public int getCount() {
        return count;
    }
}

// Producer-Consumer pattern
class ProducerConsumer {
    private Queue<Integer> queue = new LinkedList<>();
    private int capacity = 5;
    private Lock lock = new ReentrantLock();
    private Condition notFull = lock.newCondition();
    private Condition notEmpty = lock.newCondition();

    public void produce(int item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                System.out.println("Queue is full, producer waiting");
                notFull.await();
            }
            queue.add(item);
            System.out.println("Produced: " + item);
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    public int consume() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                System.out.println("Queue is empty, consumer waiting");
                notEmpty.await();
            }
            int item = queue.remove();
            System.out.println("Consumed: " + item);
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }
}

// Atomic operations
class AtomicCounter {
    private AtomicInteger count = new AtomicInteger(0);
    private AtomicLong total = new AtomicLong(0);

    public void increment() {
        count.incrementAndGet();
    }

    public void addToTotal(long value) {
        total.addAndGet(value);
    }

    public int getCount() {
        return count.get();
    }

    public long getTotal() {
        return total.get();
    }
}

public class ConcurrencyExample {
    public static void main(String[] args) {
        System.out.println("=== Basic Threading ===");

        // Thread creation methods
        SimpleThread thread1 = new SimpleThread("Thread-1");
        Thread thread2 = new Thread(new Worker(1));
        Thread thread3 = new Thread(() -> {
            System.out.println("Lambda thread running");
            try {
                Thread.sleep(800);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            System.out.println("Lambda thread finished");
        });

        thread1.start();
        thread2.start();
        thread3.start();

        // Wait for threads to finish
        try {
            thread1.join();
            thread2.join();
            thread3.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("\n=== Synchronization Example ===");

        Counter counter = new Counter();
        Thread[] threads = new Thread[10];

        for (int i = 0; i < threads.length; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
            threads[i].start();
        }

        // Wait for all threads
        for (Thread t : threads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        System.out.println("Final count: " + counter.getCount()); // Should be 10000

        System.out.println("\n=== Producer-Consumer Pattern ===");

        ProducerConsumer pc = new ProducerConsumer();

        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 10; i++) {
                    pc.produce(i);
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        Thread consumer = new Thread(() -> {
            try {
                for (int i = 1; i <= 10; i++) {
                    pc.consume();
                    Thread.sleep(150);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        producer.start();
        consumer.start();

        try {
            producer.join();
            consumer.join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("\n=== Atomic Operations ===");

        AtomicCounter atomicCounter = new AtomicCounter();

        Thread[] atomicThreads = new Thread[5];
        for (int i = 0; i < atomicThreads.length; i++) {
            final int threadId = i;
            atomicThreads[i] = new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    atomicCounter.increment();
                    atomicCounter.addToTotal(threadId * j);
                }
            });
            atomicThreads[i].start();
        }

        for (Thread t : atomicThreads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        System.out.println("Atomic count: " + atomicCounter.getCount());
        System.out.println("Atomic total: " + atomicCounter.getTotal());
    }
}
```

## Java 8+ Features

### Streams and Functional Programming

```java
import java.util.*;
import java.util.stream.*;
import java.util.function.*;
import java.time.*;
import java.time.temporal.ChronoUnit;

public class StreamsExample {
    public static void main(String[] args) {
        // Sample data
        List<Employee> employees = Arrays.asList(
            new Employee("John", "Engineering", 75000, LocalDate.of(2018, 1, 15)),
            new Employee("Jane", "Marketing", 65000, LocalDate.of(2019, 3, 20)),
            new Employee("Bob", "Engineering", 80000, LocalDate.of(2017, 6, 10)),
            new Employee("Alice", "HR", 55000, LocalDate.of(2020, 8, 5)),
            new Employee("Charlie", "Engineering", 70000, LocalDate.of(2019, 11, 12)),
            new Employee("Diana", "Sales", 60000, LocalDate.of(2020, 2, 28))
        );

        System.out.println("=== Basic Stream Operations ===");

        // Filtering and mapping
        List<String> engineeringNames = employees.stream()
            .filter(emp -> "Engineering".equals(emp.getDepartment()))
            .map(Employee::getName)
            .collect(Collectors.toList());

        System.out.println("Engineering employees: " + engineeringNames);

        // Finding elements
        Optional<Employee> highestPaid = employees.stream()
            .max(Comparator.comparingDouble(Employee::getSalary));

        highestPaid.ifPresent(emp ->
            System.out.println("Highest paid: " + emp.getName() + " ($" + emp.getSalary() + ")"));

        // Statistics
        DoubleSummaryStatistics salaryStats = employees.stream()
            .mapToDouble(Employee::getSalary)
            .summaryStatistics();

        System.out.println("Salary statistics:");
        System.out.println("  Count: " + salaryStats.getCount());
        System.out.println("  Average: $" + String.format("%.2f", salaryStats.getAverage()));
        System.out.println("  Min: $" + salaryStats.getMin());
        System.out.println("  Max: $" + salaryStats.getMax());

        System.out.println("\n=== Grouping and Partitioning ===");

        // Group by department
        Map<String, List<Employee>> byDepartment = employees.stream()
            .collect(Collectors.groupingBy(Employee::getDepartment));

        byDepartment.forEach((dept, emps) -> {
            double avgSalary = emps.stream()
                                 .mapToDouble(Employee::getSalary)
                                 .average()
                                 .orElse(0.0);
            System.out.println(dept + ": " + emps.size() + " employees, avg salary: $" +
                             String.format("%.2f", avgSalary));
        });

        // Partition by salary range
        Map<Boolean, List<Employee>> highEarners = employees.stream()
            .collect(Collectors.partitioningBy(emp -> emp.getSalary() > 65000));

        System.out.println("High earners (>65000): " +
                          highEarners.get(true).stream()
                              .map(Employee::getName)
                              .collect(Collectors.joining(", ")));

        System.out.println("\n=== Advanced Stream Operations ===");

        // FlatMap example
        List<List<String>> nestedSkills = Arrays.asList(
            Arrays.asList("Java", "Python"),
            Arrays.asList("JavaScript", "SQL"),
            Arrays.asList("Java", "C++", "Scala")
        );

        Set<String> allSkills = nestedSkills.stream()
            .flatMap(List::stream)
            .collect(Collectors.toSet());

        System.out.println("All skills: " + allSkills);

        // Complex reduction
        double totalEngineeringSalary = employees.stream()
            .filter(emp -> "Engineering".equals(emp.getDepartment()))
            .mapToDouble(Employee::getSalary)
            .reduce(0.0, Double::sum);

        System.out.println("Total engineering salaries: $" + totalEngineeringSalary);

        // Collecting to custom objects
        Map<String, Double> deptAvgSalary = employees.stream()
            .collect(Collectors.groupingBy(
                Employee::getDepartment,
                Collectors.averagingDouble(Employee::getSalary)
            ));

        System.out.println("Department average salaries: " + deptAvgSalary);

        System.out.println("\n=== Parallel Streams ===");

        // Sequential vs Parallel performance comparison
        long startTime = System.nanoTime();
        long sequentialResult = employees.stream()
            .mapToLong(emp -> fibonacci((int)(emp.getSalary() / 10000)))
            .sum();
        long sequentialTime = System.nanoTime() - startTime;

        startTime = System.nanoTime();
        long parallelResult = employees.parallelStream()
            .mapToLong(emp -> fibonacci((int)(emp.getSalary() / 10000)))
            .sum();
        long parallelTime = System.nanoTime() - startTime;

        System.out.println("Sequential time: " + sequentialTime / 1_000_000 + "ms");
        System.out.println("Parallel time: " + parallelTime / 1_000_000 + "ms");
        System.out.println("Results match: " + (sequentialResult == parallelResult));

        System.out.println("\n=== Optional and Streams ===");

        // Safe navigation with Optional
        Optional<String> managerName = employees.stream()
            .filter(emp -> "Engineering".equals(emp.getDepartment()))
            .findFirst()
            .map(Employee::getName);

        System.out.println("First engineering employee: " +
                          managerName.orElse("No engineering employees found"));

        // Complex Optional chaining
        Optional<Double> avgHighEarnerSalary = employees.stream()
            .filter(emp -> emp.getSalary() > 65000)
            .mapToDouble(Employee::getSalary)
            .average();

        avgHighEarnerSalary.ifPresent(avg ->
            System.out.println("Average high earner salary: $" + String.format("%.2f", avg)));
    }

    // Expensive computation for parallel stream demo
    private static long fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }

    static class Employee {
        private String name;
        private String department;
        private double salary;
        private LocalDate hireDate;

        public Employee(String name, String department, double salary, LocalDate hireDate) {
            this.name = name;
            this.department = department;
            this.salary = salary;
            this.hireDate = hireDate;
        }

        public String getName() { return name; }
        public String getDepartment() { return department; }
        public double getSalary() { return salary; }
        public LocalDate getHireDate() { return hireDate; }

        public long getYearsOfService() {
            return ChronoUnit.YEARS.between(hireDate, LocalDate.now());
        }

        @Override
        public String toString() {
            return String.format("%s (%s, $%.2f)", name, department, salary);
        }
    }
}
```

This comprehensive guide covers Java fundamentals, object-oriented programming, collections framework, generics, exception handling, concurrency, and modern Java 8+ features. The code examples demonstrate practical implementations of these concepts with proper error handling and best practices.
