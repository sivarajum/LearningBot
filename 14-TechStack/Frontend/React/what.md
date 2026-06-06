# React Frontend Development Guide

## What is React?

React is a JavaScript library for building user interfaces, particularly web applications with complex, interactive UIs. It uses a component-based architecture and a virtual DOM for efficient rendering.

### Key Characteristics

- **Component-based**: Build UIs using reusable components
- **Declarative**: Describe what the UI should look like, not how to manipulate it
- **Virtual DOM**: Efficiently updates only changed parts of the real DOM
- **Unidirectional data flow**: Data flows down through component hierarchy
- **JSX**: JavaScript syntax extension for writing HTML-like code
- **Ecosystem**: Rich ecosystem of libraries and tools

## Core Concepts

### Components

Components are the building blocks of React applications. They can be class-based or function-based.

#### Function Components

```jsx
import React from 'react';

function Welcome(props) {
    return <h1>Hello, {props.name}!</h1>;
}

// Or with arrow function
const Welcome = (props) => {
    return <h1>Hello, {props.name}!</h1>;
};

export default Welcome;
```

#### Class Components

```jsx
import React, { Component } from 'react';

class Welcome extends Component {
    render() {
        return <h1>Hello, {this.props.name}!</h1>;
    }
}

export default Welcome;
```

### JSX

JSX is a syntax extension that allows you to write HTML-like code in JavaScript.

```jsx
const element = <h1>Hello, world!</h1>;

// With JavaScript expressions
const name = 'John';
const element = <h1>Hello, {name}!</h1>;

// Attributes
const element = <img src={user.avatarUrl} alt={user.name} />;

// Children
const element = (
    <div>
        <h1>Hello!</h1>
        <p>Welcome to React</p>
    </div>
);
```

### Props

Props (properties) are how data is passed from parent to child components.

```jsx
// Parent component
function App() {
    return (
        <div>
            <Welcome name="Alice" age={25} />
            <Welcome name="Bob" age={30} />
        </div>
    );
}

// Child component
function Welcome(props) {
    return (
        <div>
            <h1>Hello, {props.name}!</h1>
            <p>You are {props.age} years old.</p>
        </div>
    );
}
```

### State

State represents data that can change over time and affects component rendering.

#### Class Component State

```jsx
class Counter extends Component {
    constructor(props) {
        super(props);
        this.state = {
            count: 0
        };
    }

    increment = () => {
        this.setState({ count: this.state.count + 1 });
    }

    render() {
        return (
            <div>
                <p>Count: {this.state.count}</p>
                <button onClick={this.increment}>Increment</button>
            </div>
        );
    }
}
```

#### Function Component State (useState Hook)

```jsx
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);

    const increment = () => {
        setCount(count + 1);
    };

    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={increment}>Increment</button>
        </div>
    );
}
```

## Hooks

Hooks are functions that let you use state and lifecycle features in function components.

### useState

```jsx
import React, { useState } from 'react';

function TodoList() {
    const [todos, setTodos] = useState([]);
    const [inputValue, setInputValue] = useState('');

    const addTodo = () => {
        if (inputValue.trim()) {
            setTodos([...todos, { id: Date.now(), text: inputValue, completed: false }]);
            setInputValue('');
        }
    };

    const toggleTodo = (id) => {
        setTodos(todos.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        ));
    };

    return (
        <div>
            <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Add a todo"
            />
            <button onClick={addTodo}>Add</button>
            <ul>
                {todos.map(todo => (
                    <li
                        key={todo.id}
                        onClick={() => toggleTodo(todo.id)}
                        style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}
                    >
                        {todo.text}
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

### useEffect

```jsx
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch user data when component mounts or userId changes
    useEffect(() => {
        const fetchUser = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/users/${userId}`);
                const userData = await response.json();
                setUser(userData);
            } catch (error) {
                console.error('Error fetching user:', error);
            } finally {
                setLoading(false);
            }
        };

        if (userId) {
            fetchUser();
        }
    }, [userId]); // Dependency array

    // Cleanup function
    useEffect(() => {
        const timer = setInterval(() => {
            console.log('Component is still mounted');
        }, 1000);

        return () => {
            clearInterval(timer);
        };
    }, []);

    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;

    return (
        <div>
            <h1>{user.name}</h1>
            <p>Email: {user.email}</p>
            <p>Age: {user.age}</p>
        </div>
    );
}
```

### useContext

```jsx
import React, { createContext, useContext, useState } from 'react';

// Create context
const ThemeContext = createContext();

// Provider component
function ThemeProvider({ children }) {
    const [theme, setTheme] = useState('light');

    const toggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light');
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

// Consumer component
function ThemedButton() {
    const { theme, toggleTheme } = useContext(ThemeContext);

    return (
        <button
            onClick={toggleTheme}
            style={{
                background: theme === 'light' ? '#fff' : '#333',
                color: theme === 'light' ? '#333' : '#fff',
                border: '1px solid #ccc',
                padding: '10px 20px'
            }}
        >
            Toggle to {theme === 'light' ? 'dark' : 'light'} theme
        </button>
    );
}

// App component
function App() {
    return (
        <ThemeProvider>
            <div>
                <h1>My App</h1>
                <ThemedButton />
            </div>
        </ThemeProvider>
    );
}
```

### Custom Hooks

```jsx
import { useState, useEffect } from 'react';

// Custom hook for API calls
function useApi(url) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [url]);

    return { data, loading, error };
}

// Usage
function UserList() {
    const { data: users, loading, error } = useApi('/api/users');

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <ul>
            {users.map(user => (
                <li key={user.id}>{user.name}</li>
            ))}
        </ul>
    );
}
```

## Component Lifecycle

### Class Component Lifecycle

```jsx
class UserProfile extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            loading: true
        };
        console.log('Constructor');
    }

    static getDerivedStateFromProps(props, state) {
        console.log('getDerivedStateFromProps');
        return null;
    }

    componentDidMount() {
        console.log('componentDidMount');
        // Fetch data here
        this.fetchUser();
    }

    shouldComponentUpdate(nextProps, nextState) {
        console.log('shouldComponentUpdate');
        return true;
    }

    getSnapshotBeforeUpdate(prevProps, prevState) {
        console.log('getSnapshotBeforeUpdate');
        return null;
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        console.log('componentDidUpdate');
    }

    componentWillUnmount() {
        console.log('componentWillUnmount');
        // Cleanup here
    }

    fetchUser = async () => {
        try {
            const response = await fetch(`/api/users/${this.props.userId}`);
            const user = await response.json();
            this.setState({ user, loading: false });
        } catch (error) {
            console.error('Error fetching user:', error);
            this.setState({ loading: false });
        }
    }

    render() {
        console.log('render');
        const { user, loading } = this.state;

        if (loading) return <div>Loading...</div>;
        if (!user) return <div>User not found</div>;

        return (
            <div>
                <h1>{user.name}</h1>
                <p>{user.email}</p>
            </div>
        );
    }
}
```

## State Management

### useReducer

```jsx
import React, { useReducer } from 'react';

// Reducer function
function todoReducer(state, action) {
    switch (action.type) {
        case 'ADD_TODO':
            return [...state, {
                id: Date.now(),
                text: action.payload,
                completed: false
            }];
        case 'TOGGLE_TODO':
            return state.map(todo =>
                todo.id === action.payload
                    ? { ...todo, completed: !todo.completed }
                    : todo
            );
        case 'DELETE_TODO':
            return state.filter(todo => todo.id !== action.payload);
        default:
            return state;
    }
}

function TodoApp() {
    const [todos, dispatch] = useReducer(todoReducer, []);
    const [inputValue, setInputValue] = useState('');

    const addTodo = () => {
        if (inputValue.trim()) {
            dispatch({ type: 'ADD_TODO', payload: inputValue });
            setInputValue('');
        }
    };

    const toggleTodo = (id) => {
        dispatch({ type: 'TOGGLE_TODO', payload: id });
    };

    const deleteTodo = (id) => {
        dispatch({ type: 'DELETE_TODO', payload: id });
    };

    return (
        <div>
            <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Add a todo"
            />
            <button onClick={addTodo}>Add</button>
            <ul>
                {todos.map(todo => (
                    <li key={todo.id}>
                        <span
                            onClick={() => toggleTodo(todo.id)}
                            style={{
                                textDecoration: todo.completed ? 'line-through' : 'none',
                                cursor: 'pointer'
                            }}
                        >
                            {todo.text}
                        </span>
                        <button onClick={() => deleteTodo(todo.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

### Context API + useReducer

```jsx
import React, { createContext, useContext, useReducer } from 'react';

// Initial state
const initialState = {
    todos: [],
    filter: 'all'
};

// Reducer
function appReducer(state, action) {
    switch (action.type) {
        case 'ADD_TODO':
            return {
                ...state,
                todos: [...state.todos, {
                    id: Date.now(),
                    text: action.payload,
                    completed: false
                }]
            };
        case 'TOGGLE_TODO':
            return {
                ...state,
                todos: state.todos.map(todo =>
                    todo.id === action.payload
                        ? { ...todo, completed: !todo.completed }
                        : todo
                )
            };
        case 'SET_FILTER':
            return {
                ...state,
                filter: action.payload
            };
        default:
            return state;
    }
}

// Context
const AppContext = createContext();

// Provider
function AppProvider({ children }) {
    const [state, dispatch] = useReducer(appReducer, initialState);

    return (
        <AppContext.Provider value={{ state, dispatch }}>
            {children}
        </AppContext.Provider>
    );
}

// Custom hook
function useApp() {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
}

// Components
function TodoList() {
    const { state, dispatch } = useApp();

    const filteredTodos = state.todos.filter(todo => {
        if (state.filter === 'completed') return todo.completed;
        if (state.filter === 'active') return !todo.completed;
        return true;
    });

    return (
        <ul>
            {filteredTodos.map(todo => (
                <li key={todo.id}>
                    <span
                        onClick={() => dispatch({ type: 'TOGGLE_TODO', payload: todo.id })}
                        style={{
                            textDecoration: todo.completed ? 'line-through' : 'none',
                            cursor: 'pointer'
                        }}
                    >
                        {todo.text}
                    </span>
                </li>
            ))}
        </ul>
    );
}

function FilterButtons() {
    const { state, dispatch } = useApp();

    return (
        <div>
            <button
                onClick={() => dispatch({ type: 'SET_FILTER', payload: 'all' })}
                disabled={state.filter === 'all'}
            >
                All
            </button>
            <button
                onClick={() => dispatch({ type: 'SET_FILTER', payload: 'active' })}
                disabled={state.filter === 'active'}
            >
                Active
            </button>
            <button
                onClick={() => dispatch({ type: 'SET_FILTER', payload: 'completed' })}
                disabled={state.filter === 'completed'}
            >
                Completed
            </button>
        </div>
    );
}

function App() {
    return (
        <AppProvider>
            <div>
                <h1>Todo App</h1>
                <FilterButtons />
                <TodoList />
            </div>
        </AppProvider>
    );
}
```

## Forms and Controlled Components

```jsx
import React, { useState } from 'react';

function ContactForm() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: '',
        newsletter: false,
        country: 'us'
    });

    const [errors, setErrors] = useState({});
    const [submitted, setSubmitted] = useState(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Name is required';
        }

        if (!formData.email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }

        if (!formData.message.trim()) {
            newErrors.message = 'Message is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                setSubmitted(true);
                setFormData({
                    name: '',
                    email: '',
                    message: '',
                    newsletter: false,
                    country: 'us'
                });
            } else {
                throw new Error('Failed to submit form');
            }
        } catch (error) {
            setErrors({ submit: 'Failed to submit form. Please try again.' });
        }
    };

    if (submitted) {
        return (
            <div className="success-message">
                <h2>Thank you for your message!</h2>
                <p>We'll get back to you soon.</p>
                <button onClick={() => setSubmitted(false)}>Send another message</button>
            </div>
        );
    }

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label htmlFor="name">Name:</label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={errors.name ? 'error' : ''}
                />
                {errors.name && <span className="error-text">{errors.name}</span>}
            </div>

            <div>
                <label htmlFor="email">Email:</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div>
                <label htmlFor="country">Country:</label>
                <select
                    id="country"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                >
                    <option value="us">United States</option>
                    <option value="ca">Canada</option>
                    <option value="uk">United Kingdom</option>
                    <option value="au">Australia</option>
                </select>
            </div>

            <div>
                <label htmlFor="message">Message:</label>
                <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows="5"
                    className={errors.message ? 'error' : ''}
                />
                {errors.message && <span className="error-text">{errors.message}</span>}
            </div>

            <div>
                <label>
                    <input
                        type="checkbox"
                        name="newsletter"
                        checked={formData.newsletter}
                        onChange={handleChange}
                    />
                    Subscribe to newsletter
                </label>
            </div>

            {errors.submit && <div className="error-text">{errors.submit}</div>}

            <button type="submit">Send Message</button>
        </form>
    );
}
```

## API Integration

### Fetch API

```jsx
import React, { useState, useEffect } from 'react';

function UsersList() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/users');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const createUser = async (userData) => {
        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const newUser = await response.json();
            setUsers(prev => [...prev, newUser]);
        } catch (err) {
            setError(err.message);
        }
    };

    const deleteUser = async (userId) => {
        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            setUsers(prev => prev.filter(user => user.id !== userId));
        } catch (err) {
            setError(err.message);
        }
    };

    if (loading) return <div>Loading users...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div>
            <h2>Users</h2>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.name} ({user.email})
                        <button onClick={() => deleteUser(user.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

### Axios

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:3001/api';
axios.defaults.headers.common['Authorization'] = 'Bearer ' + localStorage.getItem('token');

// Add request interceptor
axios.interceptors.request.use(
    config => {
        // Do something before request is sent
        console.log('Making request to:', config.url);
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// Add response interceptor
axios.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response?.status === 401) {
            // Redirect to login
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

function PostsManager() {
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newPost, setNewPost] = useState({ title: '', content: '' });

    useEffect(() => {
        fetchPosts();
    }, []);

    const fetchPosts = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/posts');
            setPosts(response.data);
        } catch (error) {
            console.error('Error fetching posts:', error);
        } finally {
            setLoading(false);
        }
    };

    const createPost = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/posts', newPost);
            setPosts(prev => [...prev, response.data]);
            setNewPost({ title: '', content: '' });
        } catch (error) {
            console.error('Error creating post:', error);
        }
    };

    const updatePost = async (postId, updates) => {
        try {
            const response = await axios.patch(`/posts/${postId}`, updates);
            setPosts(prev => prev.map(post =>
                post.id === postId ? response.data : post
            ));
        } catch (error) {
            console.error('Error updating post:', error);
        }
    };

    const deletePost = async (postId) => {
        try {
            await axios.delete(`/posts/${postId}`);
            setPosts(prev => prev.filter(post => post.id !== postId));
        } catch (error) {
            console.error('Error deleting post:', error);
        }
    };

    if (loading) return <div>Loading posts...</div>;

    return (
        <div>
            <h2>Posts Manager</h2>

            <form onSubmit={createPost}>
                <input
                    type="text"
                    placeholder="Post title"
                    value={newPost.title}
                    onChange={(e) => setNewPost(prev => ({ ...prev, title: e.target.value }))}
                    required
                />
                <textarea
                    placeholder="Post content"
                    value={newPost.content}
                    onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                    required
                />
                <button type="submit">Create Post</button>
            </form>

            <div className="posts-list">
                {posts.map(post => (
                    <div key={post.id} className="post-item">
                        <h3>{post.title}</h3>
                        <p>{post.content}</p>
                        <button onClick={() => deletePost(post.id)}>Delete</button>
                    </div>
                ))}
            </div>
        </div>
    );
}
```

## Performance Optimization

### React.memo

```jsx
import React from 'react';

// Component that renders expensive content
const ExpensiveComponent = React.memo(({ data, onClick }) => {
    console.log('ExpensiveComponent rendered');

    return (
        <div>
            <h2>Expensive Component</h2>
            <p>Data: {JSON.stringify(data)}</p>
            <button onClick={onClick}>Click me</button>
        </div>
    );
});

// Custom comparison function
const CustomMemoComponent = React.memo(
    ({ data, onClick }) => {
        console.log('CustomMemoComponent rendered');
        return (
            <div>
                <h2>Custom Memo Component</h2>
                <p>Data length: {data.length}</p>
                <button onClick={onClick}>Click me</button>
            </div>
        );
    },
    (prevProps, nextProps) => {
        // Only re-render if data length changed
        return prevProps.data.length === nextProps.data.length;
    }
);

function App() {
    const [count, setCount] = useState(0);
    const [data, setData] = useState([1, 2, 3]);

    const handleClick = useCallback(() => {
        setCount(c => c + 1);
    }, []);

    return (
        <div>
            <button onClick={() => setCount(c => c + 1)}>Update count: {count}</button>
            <button onClick={() => setData(d => [...d, d.length + 1])}>Add data</button>

            <ExpensiveComponent data={data} onClick={handleClick} />
            <CustomMemoComponent data={data} onClick={handleClick} />
        </div>
    );
}
```

### useMemo and useCallback

```jsx
import React, { useState, useMemo, useCallback } from 'react';

function TodoApp() {
    const [todos, setTodos] = useState([]);
    const [filter, setFilter] = useState('all');
    const [inputValue, setInputValue] = useState('');

    // Memoize filtered todos
    const filteredTodos = useMemo(() => {
        console.log('Filtering todos...');
        switch (filter) {
            case 'completed':
                return todos.filter(todo => todo.completed);
            case 'active':
                return todos.filter(todo => !todo.completed);
            default:
                return todos;
        }
    }, [todos, filter]);

    // Memoize completed count
    const completedCount = useMemo(() => {
        return todos.filter(todo => todo.completed).length;
    }, [todos]);

    // Memoize add todo function
    const addTodo = useCallback(() => {
        if (inputValue.trim()) {
            setTodos(prev => [...prev, {
                id: Date.now(),
                text: inputValue,
                completed: false
            }]);
            setInputValue('');
        }
    }, [inputValue]);

    // Memoize toggle function
    const toggleTodo = useCallback((id) => {
        setTodos(prev => prev.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        ));
    }, []);

    return (
        <div>
            <h1>Todo App (Optimized)</h1>

            <div>
                <input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Add a todo"
                />
                <button onClick={addTodo}>Add</button>
            </div>

            <div>
                <button onClick={() => setFilter('all')}>All ({todos.length})</button>
                <button onClick={() => setFilter('active')}>
                    Active ({todos.length - completedCount})
                </button>
                <button onClick={() => setFilter('completed')}>
                    Completed ({completedCount})
                </button>
            </div>

            <ul>
                {filteredTodos.map(todo => (
                    <li key={todo.id}>
                        <span
                            onClick={() => toggleTodo(todo.id)}
                            style={{
                                textDecoration: todo.completed ? 'line-through' : 'none',
                                cursor: 'pointer'
                            }}
                        >
                            {todo.text}
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
```

## Testing

### Jest + React Testing Library

```jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import UserList from './UserList';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Mock data
const mockUsers = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
];

describe('UserList', () => {
    beforeEach(() => {
        mockedAxios.get.mockClear();
        mockedAxios.post.mockClear();
        mockedAxios.delete.mockClear();
    });

    test('renders loading state initially', () => {
        mockedAxios.get.mockImplementation(() => new Promise(() => {}));

        render(<UserList />);
        expect(screen.getByText('Loading users...')).toBeInTheDocument();
    });

    test('renders users after successful fetch', async () => {
        mockedAxios.get.mockResolvedValue({ data: mockUsers });

        render(<UserList />);

        await waitFor(() => {
            expect(screen.getByText('John Doe (john@example.com)')).toBeInTheDocument();
            expect(screen.getByText('Jane Smith (jane@example.com)')).toBeInTheDocument();
        });
    });

    test('handles fetch error', async () => {
        mockedAxios.get.mockRejectedValue(new Error('Network error'));

        render(<UserList />);

        await waitFor(() => {
            expect(screen.getByText('Error: Network error')).toBeInTheDocument();
        });
    });

    test('deletes user successfully', async () => {
        mockedAxios.get.mockResolvedValue({ data: mockUsers });
        mockedAxios.delete.mockResolvedValue({});

        render(<UserList />);

        await waitFor(() => {
            expect(screen.getByText('John Doe (john@example.com)')).toBeInTheDocument();
        });

        const deleteButtons = screen.getAllByText('Delete');
        fireEvent.click(deleteButtons[0]);

        await waitFor(() => {
            expect(mockedAxios.delete).toHaveBeenCalledWith('/api/users/1');
        });

        // User should be removed from the list
        expect(screen.queryByText('John Doe (john@example.com)')).not.toBeInTheDocument();
    });
});

// Custom hook testing
import { renderHook, act } from '@testing-library/react';
import useApi from './useApi';

describe('useApi', () => {
    test('fetches data successfully', async () => {
        const mockData = { id: 1, name: 'Test' };
        mockedAxios.get.mockResolvedValue({ data: mockData });

        const { result } = renderHook(() => useApi('/api/test'));

        expect(result.current.loading).toBe(true);
        expect(result.current.data).toBe(null);
        expect(result.current.error).toBe(null);

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
            expect(result.current.data).toEqual(mockData);
            expect(result.current.error).toBe(null);
        });
    });

    test('handles fetch error', async () => {
        const errorMessage = 'Network error';
        mockedAxios.get.mockRejectedValue(new Error(errorMessage));

        const { result } = renderHook(() => useApi('/api/test'));

        await waitFor(() => {
            expect(result.current.loading).toBe(false);
            expect(result.current.data).toBe(null);
            expect(result.current.error).toEqual(errorMessage);
        });
    });
});
```

This comprehensive guide covers the essential aspects of React development, from basic components to advanced patterns, state management, performance optimization, and testing strategies.
