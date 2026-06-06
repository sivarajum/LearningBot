# MongoDB Database Guide

## MongoDB Fundamentals

### What is MongoDB?

MongoDB is a document-oriented NoSQL database designed for ease of development and scaling. It stores data in flexible, JSON-like documents, meaning fields can vary from document to document and data structure can be changed over time.

### Key Characteristics

- **Document-oriented**: Stores data in BSON (Binary JSON) documents
- **Schema-less**: No predefined schema required
- **Horizontal scaling**: Built-in sharding for horizontal scaling
- **High performance**: Memory-mapped storage engine
- **Rich query language**: Powerful querying capabilities
- **Indexing**: Multiple indexing strategies
- **Replication**: Built-in replication for high availability

### BSON Data Types

```javascript
// MongoDB supports various data types
{
  _id: ObjectId("507f1f77bcf86cd799439011"), // ObjectId
  name: "John Doe",                                // String
  age: 30,                                         // Integer (32-bit)
  height: 5.9,                                      // Double
  isActive: true,                                   // Boolean
  tags: ["developer", "mongodb"],                   // Array
  address: {                                        // Embedded Document
    street: "123 Main St",
    city: "New York",
    zip: "10001"
  },
  createdAt: ISODate("2023-01-01T00:00:00Z"),       // Date
  binaryData: BinData(0, "SGVsbG8gV29ybGQ="),       // Binary Data
  score: NumberDecimal("99.99"),                    // Decimal128
  location: {                                       // Geospatial
    type: "Point",
    coordinates: [-73.97, 40.77]
  }
}
```

## Database Operations

### Connecting to MongoDB

```javascript
const { MongoClient } = require('mongodb');

// Connection URL
const url = 'mongodb://localhost:27017';
const client = new MongoClient(url);

// Database Name
const dbName = 'myapp';

async function connectToMongoDB() {
  try {
    // Connect to MongoDB
    await client.connect();
    console.log('Connected successfully to MongoDB');

    const db = client.db(dbName);
    return db;
  } catch (error) {
    console.error('Connection failed:', error);
    throw error;
  }
}

// Usage
connectToMongoDB().then(db => {
  // Use the database
}).catch(console.error);
```

### CRUD Operations

#### Create Operations

```javascript
// Insert a single document
async function insertUser(db) {
  const users = db.collection('users');

  const user = {
    name: 'John Doe',
    email: 'john@example.com',
    age: 30,
    createdAt: new Date()
  };

  try {
    const result = await users.insertOne(user);
    console.log('User inserted:', result.insertedId);
    return result;
  } catch (error) {
    console.error('Insert failed:', error);
  }
}

// Insert multiple documents
async function insertMultipleUsers(db) {
  const users = db.collection('users');

  const userList = [
    { name: 'Jane Smith', email: 'jane@example.com', age: 25 },
    { name: 'Bob Johnson', email: 'bob@example.com', age: 35 },
    { name: 'Alice Brown', email: 'alice@example.com', age: 28 }
  ];

  try {
    const result = await users.insertMany(userList);
    console.log('Users inserted:', result.insertedCount);
    return result;
  } catch (error) {
    console.error('Insert failed:', error);
  }
}
```

#### Read Operations

```javascript
// Find all documents
async function findAllUsers(db) {
  const users = db.collection('users');

  try {
    const allUsers = await users.find({}).toArray();
    console.log('All users:', allUsers);
    return allUsers;
  } catch (error) {
    console.error('Find failed:', error);
  }
}

// Find with query
async function findUsersByAge(db, minAge) {
  const users = db.collection('users');

  try {
    const query = { age: { $gte: minAge } };
    const users = await users.find(query).toArray();
    console.log(`Users aged ${minAge}+:`, users);
    return users;
  } catch (error) {
    console.error('Find failed:', error);
  }
}

// Find one document
async function findUserByEmail(db, email) {
  const users = db.collection('users');

  try {
    const user = await users.findOne({ email });
    console.log('User found:', user);
    return user;
  } catch (error) {
    console.error('Find failed:', error);
  }
}

// Advanced queries
async function advancedQueries(db) {
  const users = db.collection('users');

  // Query with multiple conditions
  const query1 = {
    age: { $gte: 25, $lte: 35 },
    name: { $regex: /^J/ } // Names starting with 'J'
  };

  // Query with array operations
  const query2 = {
    tags: { $in: ['developer', 'admin'] }
  };

  // Query with embedded document
  const query3 = {
    'address.city': 'New York'
  };

  // Query with logical operators
  const query4 = {
    $or: [
      { age: { $lt: 25 } },
      { age: { $gt: 35 } }
    ]
  };

  try {
    const results1 = await users.find(query1).toArray();
    const results2 = await users.find(query2).toArray();
    const results3 = await users.find(query3).toArray();
    const results4 = await users.find(query4).toArray();

    return { results1, results2, results3, results4 };
  } catch (error) {
    console.error('Advanced queries failed:', error);
  }
}
```

#### Update Operations

```javascript
// Update a single document
async function updateUser(db, userId, updates) {
  const users = db.collection('users');

  try {
    const filter = { _id: new ObjectId(userId) };
    const updateDoc = {
      $set: updates,
      $currentDate: { lastModified: true }
    };

    const result = await users.updateOne(filter, updateDoc);
    console.log('User updated:', result.modifiedCount);
    return result;
  } catch (error) {
    console.error('Update failed:', error);
  }
}

// Update multiple documents
async function updateMultipleUsers(db, ageThreshold, newStatus) {
  const users = db.collection('users');

  try {
    const filter = { age: { $gte: ageThreshold } };
    const updateDoc = {
      $set: { status: newStatus },
      $inc: { updateCount: 1 }
    };

    const result = await users.updateMany(filter, updateDoc);
    console.log('Users updated:', result.modifiedCount);
    return result;
  } catch (error) {
    console.error('Update failed:', error);
  }
}

// Replace entire document
async function replaceUser(db, userId, newUserData) {
  const users = db.collection('users');

  try {
    const filter = { _id: new ObjectId(userId) };
    const result = await users.replaceOne(filter, newUserData);
    console.log('User replaced:', result.modifiedCount);
    return result;
  } catch (error) {
    console.error('Replace failed:', error);
  }
}

// Upsert operation
async function upsertUser(db, userData) {
  const users = db.collection('users');

  try {
    const filter = { email: userData.email };
    const updateDoc = {
      $set: userData,
      $setOnInsert: { createdAt: new Date() }
    };
    const options = { upsert: true };

    const result = await users.updateOne(filter, updateDoc, options);
    console.log('Upsert result:', result);
    return result;
  } catch (error) {
    console.error('Upsert failed:', error);
  }
}
```

#### Delete Operations

```javascript
// Delete a single document
async function deleteUser(db, userId) {
  const users = db.collection('users');

  try {
    const filter = { _id: new ObjectId(userId) };
    const result = await users.deleteOne(filter);
    console.log('User deleted:', result.deletedCount);
    return result;
  } catch (error) {
    console.error('Delete failed:', error);
  }
}

// Delete multiple documents
async function deleteUsersByAge(db, maxAge) {
  const users = db.collection('users');

  try {
    const filter = { age: { $lt: maxAge } };
    const result = await users.deleteMany(filter);
    console.log('Users deleted:', result.deletedCount);
    return result;
  } catch (error) {
    console.error('Delete failed:', error);
  }
}

// Delete all documents
async function deleteAllUsers(db) {
  const users = db.collection('users');

  try {
    const result = await users.deleteMany({});
    console.log('All users deleted:', result.deletedCount);
    return result;
  } catch (error) {
    console.error('Delete failed:', error);
  }
}
```

## Indexing

### Creating Indexes

```javascript
// Single field index
async function createSingleFieldIndex(db) {
  const users = db.collection('users');

  try {
    const indexName = await users.createIndex({ email: 1 });
    console.log('Single field index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}

// Compound index
async function createCompoundIndex(db) {
  const users = db.collection('users');

  try {
    const indexName = await users.createIndex({ age: 1, name: 1 });
    console.log('Compound index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}

// Unique index
async function createUniqueIndex(db) {
  const users = db.collection('users');

  try {
    const indexName = await users.createIndex(
      { email: 1 },
      { unique: true }
    );
    console.log('Unique index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}

// Text index for full-text search
async function createTextIndex(db) {
  const posts = db.collection('posts');

  try {
    const indexName = await posts.createIndex(
      { title: 'text', content: 'text' }
    );
    console.log('Text index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}

// Geospatial index
async function createGeospatialIndex(db) {
  const places = db.collection('places');

  try {
    const indexName = await places.createIndex(
      { location: '2dsphere' }
    );
    console.log('Geospatial index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}

// TTL index for automatic document expiration
async function createTTLIndex(db) {
  const sessions = db.collection('sessions');

  try {
    const indexName = await sessions.createIndex(
      { createdAt: 1 },
      { expireAfterSeconds: 3600 } // Expire after 1 hour
    );
    console.log('TTL index created:', indexName);
  } catch (error) {
    console.error('Index creation failed:', error);
  }
}
```

### Index Management

```javascript
// List all indexes
async function listIndexes(db, collectionName) {
  const collection = db.collection(collectionName);

  try {
    const indexes = await collection.indexes();
    console.log('Indexes:', indexes);
    return indexes;
  } catch (error) {
    console.error('List indexes failed:', error);
  }
}

// Drop an index
async function dropIndex(db, collectionName, indexName) {
  const collection = db.collection(collectionName);

  try {
    const result = await collection.dropIndex(indexName);
    console.log('Index dropped:', result);
  } catch (error) {
    console.error('Drop index failed:', error);
  }
}

// Get index information
async function getIndexStats(db, collectionName) {
  const collection = db.collection(collectionName);

  try {
    const stats = await collection.aggregate([
      { $indexStats: {} }
    ]).toArray();

    console.log('Index stats:', stats);
    return stats;
  } catch (error) {
    console.error('Get index stats failed:', error);
  }
}
```

## Aggregation Framework

### Basic Aggregation

```javascript
// Group and count
async function groupAndCount(db) {
  const users = db.collection('users');

  try {
    const result = await users.aggregate([
      {
        $group: {
          _id: '$department',
          count: { $sum: 1 },
          avgAge: { $avg: '$age' }
        }
      },
      {
        $sort: { count: -1 }
      }
    ]).toArray();

    console.log('Group and count result:', result);
    return result;
  } catch (error) {
    console.error('Aggregation failed:', error);
  }
}

// Filter and project
async function filterAndProject(db) {
  const users = db.collection('users');

  try {
    const result = await users.aggregate([
      {
        $match: {
          age: { $gte: 25 },
          department: 'Engineering'
        }
      },
      {
        $project: {
          name: 1,
          email: 1,
          age: 1,
          fullName: {
            $concat: ['$firstName', ' ', '$lastName']
          }
        }
      }
    ]).toArray();

    console.log('Filter and project result:', result);
    return result;
  } catch (error) {
    console.error('Aggregation failed:', error);
  }
}
```

### Advanced Aggregation

```javascript
// Lookup (join)
async function joinCollections(db) {
  const orders = db.collection('orders');

  try {
    const result = await orders.aggregate([
      {
        $lookup: {
          from: 'users',
          localField: 'userId',
          foreignField: '_id',
          as: 'user'
        }
      },
      {
        $unwind: '$user'
      },
      {
        $project: {
          orderId: '$_id',
          userName: '$user.name',
          total: 1,
          orderDate: 1
        }
      }
    ]).toArray();

    console.log('Join result:', result);
    return result;
  } catch (error) {
    console.error('Aggregation failed:', error);
  }
}

// Faceted search
async function facetedSearch(db) {
  const products = db.collection('products');

  try {
    const result = await products.aggregate([
      {
        $facet: {
          categories: [
            { $group: { _id: '$category', count: { $sum: 1 } } }
          ],
          priceRanges: [
            {
              $bucket: {
                groupBy: '$price',
                boundaries: [0, 50, 100, 200, 500],
                default: 'Other',
                output: { count: { $sum: 1 } }
              }
            }
          ],
          topRated: [
            { $match: { rating: { $gte: 4.5 } } },
            { $sort: { rating: -1 } },
            { $limit: 5 }
          ]
        }
      }
    ]).toArray();

    console.log('Faceted search result:', result);
    return result;
  } catch (error) {
    console.error('Aggregation failed:', error);
  }
}

// Time series aggregation
async function timeSeriesAggregation(db) {
  const events = db.collection('events');

  try {
    const result = await events.aggregate([
      {
        $match: {
          timestamp: {
            $gte: new Date('2023-01-01'),
            $lt: new Date('2024-01-01')
          }
        }
      },
      {
        $group: {
          _id: {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' }
          },
          count: { $sum: 1 },
          uniqueUsers: { $addToSet: '$userId' }
        }
      },
      {
        $project: {
          date: '$_id',
          count: 1,
          uniqueUserCount: { $size: '$uniqueUsers' },
          _id: 0
        }
      },
      {
        $sort: { 'date.year': 1, 'date.month': 1, 'date.day': 1 }
      }
    ]).toArray();

    console.log('Time series result:', result);
    return result;
  } catch (error) {
    console.error('Aggregation failed:', error);
  }
}
```

## Data Modeling

### Embedded Documents

```javascript
// User with embedded address
const userWithAddress = {
  _id: new ObjectId(),
  name: 'John Doe',
  email: 'john@example.com',
  address: {
    street: '123 Main St',
    city: 'New York',
    state: 'NY',
    zip: '10001',
    coordinates: {
      type: 'Point',
      coordinates: [-73.97, 40.77]
    }
  },
  createdAt: new Date()
};

// Blog post with embedded comments
const blogPost = {
  _id: new ObjectId(),
  title: 'MongoDB Best Practices',
  content: 'Content here...',
  author: {
    id: new ObjectId(),
    name: 'Jane Smith',
    email: 'jane@example.com'
  },
  comments: [
    {
      id: new ObjectId(),
      author: 'Bob Johnson',
      content: 'Great article!',
      createdAt: new Date('2023-01-15')
    },
    {
      id: new ObjectId(),
      author: 'Alice Brown',
      content: 'Very helpful, thanks!',
      createdAt: new Date('2023-01-16')
    }
  ],
  tags: ['mongodb', 'database', 'nosql'],
  published: true,
  createdAt: new Date('2023-01-10'),
  updatedAt: new Date('2023-01-10')
};
```

### References

```javascript
// User document
const user = {
  _id: new ObjectId(),
  name: 'John Doe',
  email: 'john@example.com'
};

// Order document with reference
const order = {
  _id: new ObjectId(),
  userId: user._id, // Reference to user
  items: [
    {
      productId: new ObjectId(),
      quantity: 2,
      price: 29.99
    }
  ],
  total: 59.98,
  status: 'pending',
  createdAt: new Date()
};

// Product document
const product = {
  _id: new ObjectId(),
  name: 'Wireless Headphones',
  price: 29.99,
  category: 'Electronics',
  inStock: true
};
```

### Schema Design Patterns

```javascript
// Attribute Pattern - for sparse data
const product = {
  _id: new ObjectId(),
  name: 'Laptop',
  price: 999.99,
  attributes: {
    screen_size: '15.6"',
    ram: '16GB',
    storage: '512GB SSD',
    color: 'Silver'
  }
};

// Bucket Pattern - for time series data
const sensorData = {
  _id: new ObjectId(),
  sensorId: 'sensor001',
  startDate: new Date('2023-01-01T00:00:00Z'),
  endDate: new Date('2023-01-01T01:00:00Z'),
  measurements: [
    { timestamp: new Date('2023-01-01T00:00:00Z'), value: 23.5 },
    { timestamp: new Date('2023-01-01T00:15:00Z'), value: 24.1 },
    { timestamp: new Date('2023-01-01T00:30:00Z'), value: 23.8 },
    // ... more measurements
  ]
};

// Polymorphic Pattern - for different document types
const events = [
  {
    _id: new ObjectId(),
    type: 'user_login',
    userId: new ObjectId(),
    timestamp: new Date(),
    ipAddress: '192.168.1.1',
    userAgent: 'Mozilla/5.0...'
  },
  {
    _id: new ObjectId(),
    type: 'order_placed',
    userId: new ObjectId(),
    orderId: new ObjectId(),
    timestamp: new Date(),
    total: 149.99
  }
];
```

## Transactions

### Multi-Document Transactions

```javascript
// Transfer money between accounts
async function transferMoney(db, fromAccountId, toAccountId, amount) {
  const session = db.client.startSession();

  try {
    await session.withTransaction(async () => {
      const accounts = db.collection('accounts');

      // Check sender balance
      const sender = await accounts.findOne(
        { _id: fromAccountId },
        { session }
      );

      if (!sender || sender.balance < amount) {
        throw new Error('Insufficient funds');
      }

      // Debit sender
      await accounts.updateOne(
        { _id: fromAccountId },
        { $inc: { balance: -amount } },
        { session }
      );

      // Credit receiver
      await accounts.updateOne(
        { _id: toAccountId },
        { $inc: { balance: amount } },
        { session }
      );

      // Log transaction
      await db.collection('transactions').insertOne({
        fromAccountId,
        toAccountId,
        amount,
        timestamp: new Date()
      }, { session });
    });

    console.log('Transfer completed successfully');
  } catch (error) {
    console.error('Transfer failed:', error);
  } finally {
    await session.endSession();
  }
}

// Order processing with inventory check
async function processOrder(db, orderData) {
  const session = db.client.startSession();

  try {
    await session.withTransaction(async () => {
      const orders = db.collection('orders');
      const products = db.collection('products');

      // Check inventory for all items
      for (const item of orderData.items) {
        const product = await products.findOne(
          { _id: item.productId },
          { session }
        );

        if (!product || product.stock < item.quantity) {
          throw new Error(`Insufficient stock for product ${item.productId}`);
        }
      }

      // Create order
      const order = await orders.insertOne({
        ...orderData,
        status: 'confirmed',
        createdAt: new Date()
      }, { session });

      // Update inventory
      for (const item of orderData.items) {
        await products.updateOne(
          { _id: item.productId },
          { $inc: { stock: -item.quantity } },
          { session }
        );
      }

      console.log('Order processed successfully:', order.insertedId);
    });
  } catch (error) {
    console.error('Order processing failed:', error);
  } finally {
    await session.endSession();
  }
}
```

## Replication

### Replica Set Configuration

```javascript
// Connect to replica set
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017,localhost:27018,localhost:27019/myapp?replicaSet=rs0';
const client = new MongoClient(uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

// Read preferences
async function readFromSecondary(db) {
  const users = db.collection('users');

  try {
    // Read from secondary
    const user = await users.findOne(
      { email: 'john@example.com' },
      { readPreference: 'secondary' }
    );

    console.log('User from secondary:', user);
    return user;
  } catch (error) {
    console.error('Read from secondary failed:', error);
  }
}

// Write concern
async function insertWithWriteConcern(db) {
  const users = db.collection('users');

  try {
    const result = await users.insertOne(
      { name: 'John Doe', email: 'john@example.com' },
      { writeConcern: { w: 'majority', wtimeout: 5000 } }
    );

    console.log('Insert with write concern:', result);
  } catch (error) {
    console.error('Insert failed:', error);
  }
}
```

## Sharding

### Sharded Cluster Setup

```javascript
// Connect to sharded cluster
const { MongoClient } = require('mongodb');

const uri = 'mongodb://mongos1:27017,mongos2:27017/myapp';
const client = new MongoClient(uri);

// Enable sharding for database
async function enableSharding(db) {
  try {
    await db.admin().command({ enableSharding: db.databaseName });
    console.log('Sharding enabled for database');
  } catch (error) {
    console.error('Enable sharding failed:', error);
  }
}

// Create hashed shard key
async function createHashedShardKey(db) {
  const users = db.collection('users');

  try {
    // Create index on shard key
    await users.createIndex({ _id: 'hashed' });

    // Shard collection
    await db.admin().command({
      shardCollection: `${db.databaseName}.users`,
      key: { _id: 'hashed' }
    });

    console.log('Collection sharded with hashed key');
  } catch (error) {
    console.error('Sharding failed:', error);
  }
}

// Create ranged shard key
async function createRangedShardKey(db) {
  const orders = db.collection('orders');

  try {
    // Create index on shard key
    await orders.createIndex({ customerId: 1, orderDate: 1 });

    // Shard collection
    await db.admin().command({
      shardCollection: `${db.databaseName}.orders`,
      key: { customerId: 1, orderDate: 1 }
    });

    console.log('Collection sharded with ranged key');
  } catch (error) {
    console.error('Sharding failed:', error);
  }
}
```

## Performance Optimization

### Query Optimization

```javascript
// Explain query execution
async function explainQuery(db) {
  const users = db.collection('users');

  try {
    const explanation = await users.find({ age: { $gte: 25 } })
      .explain('executionStats');

    console.log('Query explanation:', JSON.stringify(explanation, null, 2));
  } catch (error) {
    console.error('Explain failed:', error);
  }
}

// Profile slow queries
async function enableProfiling(db) {
  try {
    // Enable profiling for queries > 100ms
    await db.setProfilingLevel(1, { slowms: 100 });
    console.log('Profiling enabled');
  } catch (error) {
    console.error('Enable profiling failed:', error);
  }
}

// View profile data
async function viewProfileData(db) {
  const systemProfile = db.collection('system.profile');

  try {
    const slowQueries = await systemProfile.find({})
      .sort({ ts: -1 })
      .limit(10)
      .toArray();

    console.log('Slow queries:', slowQueries);
  } catch (error) {
    console.error('View profile failed:', error);
  }
}
```

### Connection Pooling

```javascript
// Configure connection pool
const { MongoClient } = require('mongodb');

const client = new MongoClient('mongodb://localhost:27017', {
  maxPoolSize: 10,        // Maximum number of connections
  minPoolSize: 5,         // Minimum number of connections
  maxIdleTimeMS: 30000,   // Close connections after 30 seconds of inactivity
  serverSelectionTimeoutMS: 5000, // Timeout for server selection
  socketTimeoutMS: 45000, // Close sockets after 45 seconds of inactivity
  bufferMaxEntries: 0,    // Disable mongoose buffering
  bufferCommands: false   // Disable mongoose buffering
});

// Monitor connection pool
client.on('connectionPoolCreated', (event) => {
  console.log('Connection pool created');
});

client.on('connectionPoolReady', (event) => {
  console.log('Connection pool ready');
});

client.on('connectionCreated', (event) => {
  console.log('Connection created');
});

client.on('connectionClosed', (event) => {
  console.log('Connection closed');
});
```

## Security

### Authentication and Authorization

```javascript
// Create user with roles
async function createDatabaseUser(db) {
  try {
    await db.admin().command({
      createUser: 'appuser',
      pwd: 'securepassword',
      roles: [
        {
          role: 'readWrite',
          db: db.databaseName
        }
      ]
    });

    console.log('Database user created');
  } catch (error) {
    console.error('Create user failed:', error);
  }
}

// Connect with authentication
const { MongoClient } = require('mongodb');

const uri = 'mongodb://appuser:securepassword@localhost:27017/myapp?authSource=admin';
const client = new MongoClient(uri);
```

### Data Encryption

```javascript
// Field-level encryption
const { ClientEncryption } = require('mongodb-client-encryption');

async function encryptField(db) {
  const encryption = new ClientEncryption(db.client, {
    keyVaultNamespace: 'encryption.__keyVault',
    kmsProviders: {
      local: {
        key: 'your-32-byte-key-here' // In production, use proper KMS
      }
    }
  });

  try {
    // Create data key
    const dataKey = await encryption.createDataKey('local');

    // Encrypt field
    const encryptedField = await encryption.encrypt(
      'sensitive data',
      {
        keyId: dataKey,
        algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic'
      }
    );

    console.log('Field encrypted');
    return encryptedField;
  } catch (error) {
    console.error('Encryption failed:', error);
  }
}
```

## Backup and Recovery

### Database Backup

```javascript
// mongodump - create backup
const { spawn } = require('child_process');

function createBackup(databaseName, outputPath) {
  return new Promise((resolve, reject) => {
    const mongodump = spawn('mongodump', [
      `--db=${databaseName}`,
      `--out=${outputPath}`,
      '--host=localhost',
      '--port=27017'
    ]);

    mongodump.stdout.on('data', (data) => {
      console.log(`Backup stdout: ${data}`);
    });

    mongodump.stderr.on('data', (data) => {
      console.error(`Backup stderr: ${data}`);
    });

    mongodump.on('close', (code) => {
      if (code === 0) {
        console.log('Backup completed successfully');
        resolve();
      } else {
        reject(new Error(`Backup failed with code ${code}`));
      }
    });
  });
}

// mongorestore - restore from backup
function restoreBackup(databaseName, backupPath) {
  return new Promise((resolve, reject) => {
    const mongorestore = spawn('mongorestore', [
      `--db=${databaseName}`,
      backupPath,
      '--host=localhost',
      '--port=27017',
      '--drop' // Drop existing collections
    ]);

    mongorestore.stdout.on('data', (data) => {
      console.log(`Restore stdout: ${data}`);
    });

    mongorestore.stderr.on('data', (data) => {
      console.error(`Restore stderr: ${data}`);
    });

    mongorestore.on('close', (code) => {
      if (code === 0) {
        console.log('Restore completed successfully');
        resolve();
      } else {
        reject(new Error(`Restore failed with code ${code}`));
      }
    });
  });
}
```

This comprehensive guide covers MongoDB from basic operations to advanced features including aggregation, indexing, transactions, replication, sharding, and performance optimization.
