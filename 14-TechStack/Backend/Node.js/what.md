# Node.js Backend Development Guide

## What is Node.js?

Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine that allows you to run JavaScript on the server side. It uses an event-driven, non-blocking I/O model that makes it lightweight and efficient for building scalable network applications.

### Key Characteristics

- **Single-threaded**: Uses a single thread with event loop
- **Non-blocking I/O**: Asynchronous operations don't block execution
- **Event-driven**: Responds to events through callbacks, promises, or async/await
- **NPM ecosystem**: Largest package ecosystem in the world
- **Cross-platform**: Runs on Windows, macOS, Linux

## Core Concepts

### Event Loop

The event loop is the heart of Node.js, enabling non-blocking I/O operations.

```javascript
console.log('Start');

setTimeout(() => {
    console.log('Timeout callback');
}, 0);

Promise.resolve().then(() => {
    console.log('Promise callback');
});

console.log('End');

// Output: Start, End, Promise callback, Timeout callback
```

### Modules System

Node.js uses CommonJS modules by default (ES6 modules also supported).

```javascript
// math.js
function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

module.exports = { add, multiply };

// app.js
const { add, multiply } = require('./math');

console.log(add(5, 3));        // 8
console.log(multiply(5, 3));   // 15
```

### Asynchronous Programming

#### Callbacks
```javascript
const fs = require('fs');

fs.readFile('file.txt', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading file:', err);
        return;
    }
    console.log('File content:', data);
});
```

#### Promises
```javascript
const fs = require('fs').promises;

fs.readFile('file.txt', 'utf8')
    .then(data => {
        console.log('File content:', data);
    })
    .catch(err => {
        console.error('Error reading file:', err);
    });
```

#### Async/Await
```javascript
const fs = require('fs').promises;

async function readFile() {
    try {
        const data = await fs.readFile('file.txt', 'utf8');
        console.log('File content:', data);
    } catch (err) {
        console.error('Error reading file:', err);
    }
}

readFile();
```

## Express.js Framework

Express.js is the most popular web framework for Node.js, providing robust features for web and mobile applications.

### Basic Server Setup

```javascript
const express = require('express');
const app = express();
const port = 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.get('/api/users', (req, res) => {
    res.json([
        { id: 1, name: 'John Doe' },
        { id: 2, name: 'Jane Smith' }
    ]);
});

app.post('/api/users', (req, res) => {
    const newUser = {
        id: Date.now(),
        name: req.body.name,
        email: req.body.email
    };
    // In a real app, you'd save to database
    res.status(201).json(newUser);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
```

### Middleware

Middleware functions have access to the request object (req), response object (res), and the next middleware function.

```javascript
// Logger middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
    next();
});

// Authentication middleware
const authenticate = (req, res, next) => {
    const token = req.header('Authorization');
    if (!token) {
        return res.status(401).json({ error: 'Access denied' });
    }
    // Verify token logic here
    next();
};

// Protected route
app.get('/api/protected', authenticate, (req, res) => {
    res.json({ message: 'This is protected data' });
});
```

### Route Parameters and Query Strings

```javascript
// Route parameters
app.get('/api/users/:id', (req, res) => {
    const userId = req.params.id;
    // Find user by ID
    res.json({ id: userId, name: 'User ' + userId });
});

// Query parameters
app.get('/api/search', (req, res) => {
    const { q, limit = 10, offset = 0 } = req.query;
    // Search logic here
    res.json({
        query: q,
        limit: parseInt(limit),
        offset: parseInt(offset),
        results: []
    });
});
```

## RESTful API Design

### HTTP Methods and Status Codes

```javascript
// GET - Retrieve resources
app.get('/api/resources', (req, res) => {
    // Return collection of resources
    res.json(resources);
});

app.get('/api/resources/:id', (req, res) => {
    // Return single resource
    const resource = resources.find(r => r.id === req.params.id);
    if (!resource) {
        return res.status(404).json({ error: 'Resource not found' });
    }
    res.json(resource);
});

// POST - Create new resource
app.post('/api/resources', (req, res) => {
    const newResource = {
        id: Date.now().toString(),
        ...req.body
    };
    resources.push(newResource);
    res.status(201).json(newResource);
});

// PUT - Update entire resource
app.put('/api/resources/:id', (req, res) => {
    const index = resources.findIndex(r => r.id === req.params.id);
    if (index === -1) {
        return res.status(404).json({ error: 'Resource not found' });
    }
    resources[index] = { id: req.params.id, ...req.body };
    res.json(resources[index]);
});

// PATCH - Partial update
app.patch('/api/resources/:id', (req, res) => {
    const resource = resources.find(r => r.id === req.params.id);
    if (!resource) {
        return res.status(404).json({ error: 'Resource not found' });
    }
    Object.assign(resource, req.body);
    res.json(resource);
});

// DELETE - Remove resource
app.delete('/api/resources/:id', (req, res) => {
    const index = resources.findIndex(r => r.id === req.params.id);
    if (index === -1) {
        return res.status(404).json({ error: 'Resource not found' });
    }
    resources.splice(index, 1);
    res.status(204).send();
});
```

### Error Handling

```javascript
// Error handling middleware (must be last)
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something went wrong!',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Route not found' });
});
```

## Database Integration

### MongoDB with Mongoose

```javascript
const mongoose = require('mongoose');

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/myapp', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// Define schema
const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true
    },
    age: {
        type: Number,
        min: 0,
        max: 120
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Add instance methods
userSchema.methods.getFullInfo = function() {
    return `${this.name} (${this.email}) - Age: ${this.age}`;
};

// Add static methods
userSchema.statics.findByName = function(name) {
    return this.find({ name: new RegExp(name, 'i') });
};

// Create model
const User = mongoose.model('User', userSchema);

// Usage
app.post('/api/users', async (req, res) => {
    try {
        const user = new User(req.body);
        await user.save();
        res.status(201).json(user);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

app.get('/api/users', async (req, res) => {
    try {
        const users = await User.find();
        res.json(users);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

### PostgreSQL with Sequelize

```javascript
const { Sequelize, DataTypes } = require('sequelize');

// Create Sequelize instance
const sequelize = new Sequelize('database', 'username', 'password', {
    host: 'localhost',
    dialect: 'postgres'
});

// Define model
const User = sequelize.define('User', {
    name: {
        type: DataTypes.STRING,
        allowNull: false
    },
    email: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    age: {
        type: DataTypes.INTEGER,
        validate: {
            min: 0,
            max: 120
        }
    }
}, {
    timestamps: true
});

// Sync database
sequelize.sync();

// Routes
app.post('/api/users', async (req, res) => {
    try {
        const user = await User.create(req.body);
        res.status(201).json(user);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

app.get('/api/users', async (req, res) => {
    try {
        const users = await User.findAll();
        res.json(users);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

## Authentication and Security

### JWT Authentication

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// User model with password hashing
userSchema.pre('save', async function(next) {
    if (!this.isModified('password')) return next();

    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
});

// Login route
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const user = await User.findOne({ email });

        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }

        const token = jwt.sign(
            { userId: user._id, email: user.email },
            process.env.JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.json({ token, user: { id: user._id, name: user.name, email: user.email } });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Protected route middleware
const auth = (req, res, next) => {
    try {
        const token = req.header('Authorization').replace('Bearer ', '');
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'Please authenticate' });
    }
};

app.get('/api/profile', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.userId);
        res.json(user);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});
```

### Input Validation

```javascript
const Joi = require('joi');

// Validation schemas
const userSchema = Joi.object({
    name: Joi.string().min(2).max(50).required(),
    email: Joi.string().email().required(),
    age: Joi.number().integer().min(0).max(120),
    password: Joi.string().min(6).required()
});

const loginSchema = Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required()
});

// Validation middleware
const validate = (schema) => {
    return (req, res, next) => {
        const { error } = schema.validate(req.body);
        if (error) {
            return res.status(400).json({
                error: 'Validation error',
                details: error.details[0].message
            });
        }
        next();
    };
};

// Routes with validation
app.post('/api/users', validate(userSchema), async (req, res) => {
    // User creation logic
});

app.post('/api/auth/login', validate(loginSchema), async (req, res) => {
    // Login logic
});
```

## File Upload Handling

```javascript
const multer = require('multer');
const path = require('path');

// Configure storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

// File filter
const fileFilter = (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|pdf|doc|docx/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
        return cb(null, true);
    } else {
        cb(new Error('Invalid file type'));
    }
};

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB limit
    fileFilter: fileFilter
});

// Routes
app.post('/api/upload/single', upload.single('file'), (req, res) => {
    res.json({
        message: 'File uploaded successfully',
        filename: req.file.filename,
        size: req.file.size
    });
});

app.post('/api/upload/multiple', upload.array('files', 5), (req, res) => {
    const files = req.files.map(file => ({
        filename: file.filename,
        size: file.size,
        mimetype: file.mimetype
    }));
    res.json({
        message: `${req.files.length} files uploaded successfully`,
        files: files
    });
});
```

## Real-time Communication with Socket.io

```javascript
const http = require('http');
const socketIo = require('socket.io');

const server = http.createServer(app);
const io = socketIo(server);

// Socket connection handling
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    // Join room
    socket.on('join-room', (roomId) => {
        socket.join(roomId);
        socket.to(roomId).emit('user-joined', socket.id);
    });

    // Handle chat messages
    socket.on('send-message', (data) => {
        io.to(data.roomId).emit('receive-message', {
            message: data.message,
            sender: socket.id,
            timestamp: new Date()
        });
    });

    // Handle typing indicators
    socket.on('typing', (data) => {
        socket.to(data.roomId).emit('user-typing', socket.id);
    });

    socket.on('stop-typing', (data) => {
        socket.to(data.roomId).emit('user-stop-typing', socket.id);
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
    });
});

// API endpoint to send notifications
app.post('/api/notify', (req, res) => {
    const { roomId, message } = req.body;
    io.to(roomId).emit('notification', { message, timestamp: new Date() });
    res.json({ success: true });
});
```

## Testing

### Unit Testing with Jest

```javascript
// math.js
function add(a, b) {
    return a + b;
}

function divide(a, b) {
    if (b === 0) {
        throw new Error('Division by zero');
    }
    return a / b;
}

module.exports = { add, divide };

// math.test.js
const { add, divide } = require('./math');

describe('Math functions', () => {
    test('add function', () => {
        expect(add(2, 3)).toBe(5);
        expect(add(-1, 1)).toBe(0);
        expect(add(0, 0)).toBe(0);
    });

    test('divide function', () => {
        expect(divide(6, 2)).toBe(3);
        expect(divide(5, 2)).toBe(2.5);
    });

    test('divide by zero throws error', () => {
        expect(() => divide(5, 0)).toThrow('Division by zero');
    });
});
```

### API Testing with Supertest

```javascript
const request = require('supertest');
const app = require('../app'); // Your Express app

describe('API Tests', () => {
    describe('GET /api/users', () => {
        it('should return all users', async () => {
            const response = await request(app)
                .get('/api/users')
                .expect(200)
                .expect('Content-Type', /json/);

            expect(Array.isArray(response.body)).toBe(true);
        });
    });

    describe('POST /api/users', () => {
        it('should create a new user', async () => {
            const userData = {
                name: 'John Doe',
                email: 'john@example.com',
                age: 30
            };

            const response = await request(app)
                .post('/api/users')
                .send(userData)
                .expect(201)
                .expect('Content-Type', /json/);

            expect(response.body).toHaveProperty('id');
            expect(response.body.name).toBe(userData.name);
        });

        it('should validate input', async () => {
            const invalidData = {
                name: '',
                email: 'invalid-email'
            };

            await request(app)
                .post('/api/users')
                .send(invalidData)
                .expect(400);
        });
    });
});
```

## Deployment and Production

### Environment Configuration

```javascript
// config.js
const config = {
    development: {
        port: process.env.PORT || 3000,
        database: 'mongodb://localhost:27017/dev_db',
        jwtSecret: 'dev_secret_key'
    },
    production: {
        port: process.env.PORT || 8080,
        database: process.env.MONGODB_URI,
        jwtSecret: process.env.JWT_SECRET
    },
    test: {
        port: 3001,
        database: 'mongodb://localhost:27017/test_db',
        jwtSecret: 'test_secret_key'
    }
};

const env = process.env.NODE_ENV || 'development';
module.exports = config[env];
```

### Process Management with PM2

```json
// ecosystem.config.js
module.exports = {
    apps: [{
        name: 'my-app',
        script: 'app.js',
        instances: 'max',
        exec_mode: 'cluster',
        env: {
            NODE_ENV: 'development',
            PORT: 3000
        },
        env_production: {
            NODE_ENV: 'production',
            PORT: 8080
        }
    }]
};
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGODB_URI=mongodb://db:27017/myapp
    depends_on:
      - db

  db:
    image: mongo:5.0
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongodb_data:
```

## Performance Optimization

### Caching

```javascript
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 minutes

// Cache middleware
const cacheMiddleware = (duration) => {
    return (req, res, next) => {
        const key = req.originalUrl;
        const cachedResponse = cache.get(key);

        if (cachedResponse) {
            res.json(cachedResponse);
            return;
        }

        const originalJson = res.json;
        res.json = (body) => {
            cache.set(key, body, duration);
            originalJson.call(res, body);
        };

        next();
    };
};

// Usage
app.get('/api/users', cacheMiddleware(300), async (req, res) => {
    const users = await User.find();
    res.json(users);
});
```

### Clustering

```javascript
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
    console.log(`Master ${process.pid} is running`);

    // Fork workers
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }

    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        // Restart worker
        cluster.fork();
    });
} else {
    // Worker process
    const app = require('./app');
    const port = process.env.PORT || 3000;

    app.listen(port, () => {
        console.log(`Worker ${process.pid} started on port ${port}`);
    });
}
```

## Modern Node.js Features

### ES6+ Features

```javascript
// Destructuring
const { name, email, ...rest } = user;

// Arrow functions
const getUser = async (id) => {
    const user = await User.findById(id);
    return user;
};

// Template literals
const greeting = `Hello, ${user.name}! Welcome to ${appName}.`;

// Spread operator
const updatedUser = { ...user, lastLogin: new Date() };

// Optional chaining
const email = user?.contact?.email;

// Nullish coalescing
const limit = req.query.limit ?? 10;
```

### Built-in Modules

```javascript
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');
const { EventEmitter } = require('events');

// File operations
async function readFile(filePath) {
    try {
        const data = await fs.readFile(filePath, 'utf8');
        return data;
    } catch (err) {
        console.error('Error reading file:', err);
        throw err;
    }
}

// Path operations
const filePath = path.join(__dirname, 'uploads', filename);
const ext = path.extname(filename);

// Crypto operations
const hash = crypto.createHash('sha256');
hash.update(password);
const hashedPassword = hash.digest('hex');

// Event emitter
class MyEmitter extends EventEmitter {}

const myEmitter = new MyEmitter();
myEmitter.on('event', () => {
    console.log('Event fired!');
});
myEmitter.emit('event');
```

This comprehensive guide covers the essential aspects of Node.js backend development, from basic concepts to advanced patterns and production deployment strategies.
