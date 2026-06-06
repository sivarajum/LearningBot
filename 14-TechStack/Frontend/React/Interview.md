# React Interview Questions and Answers

## Beginner Level Questions

### Q1: What is React and what problem does it solve?

**Answer:**

React is a JavaScript library for building user interfaces, particularly web applications. It uses a component-based architecture and a virtual DOM for efficient rendering.

**Key Use Cases:**
- Use case 1
- Use case 2
- Use case 3

### Q2: What are the core features of React?

**Answer:**

The core features include:

## Beginner Level Questions

### What is React and what are its key features?

**Answer:**

React is a JavaScript library for building user interfaces. Key features include: component-based architecture, virtual DOM for performance, one-way data binding, JSX syntax, and a rich ecosystem. React allows developers to build reusable UI components and manage application state efficiently.

## Beginner Level Questions

### What is JSX and why is it used?

**Answer:**

JSX (JavaScript XML) is a syntax extension that allows writing HTML-like code in JavaScript. It makes React code more readable and expressive. JSX is transpiled to React.createElement() calls. It allows embedding expressions, using JavaScript logic, and creating component trees in a declarative way.

## Intermediate Level Questions

### Explain the difference between state and props in React.

**Answer:**

Props (properties) are read-only data passed from parent to child components. They are immutable and used for configuration. State is mutable data managed within a component using useState hook. State changes trigger re-renders. Props flow down, state is managed locally. Use props for configuration, state for dynamic data.

## Intermediate Level Questions

### What are React Hooks and why were they introduced?

**Answer:**

Hooks are functions that let you use state and other React features in functional components. They were introduced to allow functional components to have state and lifecycle methods. Common hooks: useState (state), useEffect (side effects), useContext (context), useMemo (memoization), useCallback (callback memoization).

## Advanced Level Questions

### Explain React's reconciliation algorithm and virtual DOM.

**Answer:**

React uses a virtual DOM (in-memory representation) to optimize rendering. When state changes, React creates a new virtual DOM tree and compares it with the previous one (diffing). It then updates only the changed nodes in the real DOM (reconciliation). This minimizes expensive DOM operations and improves performance.


## References

- Official documentation
- Community resources
