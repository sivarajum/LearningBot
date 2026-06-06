# Node.js Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
# Install Node.js
# Download from nodejs.org or use nvm
nvm install 18
nvm use 18

# Create project
mkdir my-app && cd my-app
npm init -y
```

### 2. **First Application**
```javascript
// app.js
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World\n');
});

server.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

### 3. **Express Basics**
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello World' });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

## Level 2 – Production Patterns

### Database Integration
```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/mydb');

const User = mongoose.model('User', {
    name: String,
    email: String
});

app.post('/users', async (req, res) => {
    const user = new User(req.body);
    await user.save();
    res.json(user);
});
```

### Authentication
```javascript
const jwt = require('jsonwebtoken');

app.post('/login', (req, res) => {
    const token = jwt.sign(
        { userId: user.id },
        process.env.JWT_SECRET,
        { expiresIn: '1h' }
    );
    res.json({ token });
});
```

## Level 3 – Architect Playbook

### Microservices
```javascript
// Service 1
const express = require('express');
const app = express();

app.get('/api/users', async (req, res) => {
    // Fetch from database
    res.json(users);
});

// Service 2 - Call Service 1
const axios = require('axios');
const users = await axios.get('http://service1:3000/api/users');
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Install package | `npm install package` | Install dependency |
| Run script | `npm start` | Run application |
| Test | `npm test` | Run tests |
| Build | `npm run build` | Build for production |

## Checklist Before Production

- [ ] Set up proper error handling
- [ ] Implement authentication/authorization
- [ ] Configure environment variables
- [ ] Set up logging and monitoring
- [ ] Implement rate limiting
- [ ] Set up database connection pooling
- [ ] Configure HTTPS/TLS
- [ ] Set up CI/CD pipeline
