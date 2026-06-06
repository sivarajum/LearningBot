# Cloud Firestore Interview Questions & Answers

## Beginner Level Questions

### 1. What is Cloud Firestore and how does it differ from traditional databases?

**Answer:** Cloud Firestore is Google's flexible, scalable NoSQL cloud database designed for mobile, web, and server development. It provides real-time data synchronization and offline support, making it ideal for modern applications.

**Key Differences from Traditional Databases:**

**Data Model:**
- **Firestore**: Document-based NoSQL with JSON-like documents
- **Traditional RDBMS**: Table-based with fixed schemas and relations

**Scalability:**
- **Firestore**: Automatic horizontal scaling to millions of users
- **Traditional RDBMS**: Vertical scaling with manual sharding

**Real-time Capabilities:**
- **Firestore**: Built-in real-time synchronization
- **Traditional RDBMS**: Requires additional technologies (WebSockets, polling)

**Offline Support:**
- **Firestore**: Native offline support with local caching
- **Traditional RDBMS**: Limited offline capabilities

### 2. Explain the basic structure of Firestore data.

**Answer:** Firestore uses a hierarchical, document-based data model:

**Collections and Documents:**
- **Collections**: Containers for documents (like tables)
- **Documents**: JSON-like objects containing data (like rows)
- **Subcollections**: Collections nested within documents

**Example Structure:**
```
Firestore Database
├── Collection: "users"
│   ├── Document: "user123"
│   │   ├── name: "John Doe"
│   │   ├── email: "john@example.com"
│   │   └── created_at: timestamp
│   └── Subcollection: "posts"
│       ├── Document: "post456"
│       │   ├── title: "My Post"
│       │   └── content: "Hello World"
│       └── Document: "post789"
│           └── ...
└── Collection: "posts"
    └── ...
```

**Key Characteristics:**
- Documents can contain subcollections
- No fixed schema requirements
- Hierarchical data organization
- References between documents

### 3. What are the main features of Firestore?

**Answer:** Firestore offers several key features:

**Real-time Synchronization:**
- Live data updates across clients
- Automatic UI synchronization
- Offline data access and sync

**Strong Consistency:**
- Global consistency across regions
- No eventual consistency delays
- ACID transactions

**Security:**
- Firebase Security Rules for access control
- IAM integration for server access
- Data validation at database level

**Scalability:**
- Automatic scaling from zero to millions of users
- No manual provisioning
- Global distribution

**Offline Support:**
- Local caching and persistence
- Conflict resolution strategies
- Sync when connection restored

### 4. How do you perform basic CRUD operations in Firestore?

**Answer:** Firestore supports standard CRUD operations:

**Create (Add Document):**
```javascript
// Web SDK
await addDoc(collection(db, 'users'), {
  name: 'John Doe',
  email: 'john@example.com',
  created_at: serverTimestamp()
});
```

**Read (Get Document):**
```javascript
const docRef = doc(db, 'users', 'user123');
const docSnap = await getDoc(docRef);
if (docSnap.exists()) {
  console.log(docSnap.data());
}
```

**Update (Modify Document):**
```javascript
const docRef = doc(db, 'users', 'user123');
await updateDoc(docRef, {
  name: 'Jane Doe',
  updated_at: serverTimestamp()
});
```

**Delete (Remove Document):**
```javascript
const docRef = doc(db, 'users', 'user123');
await deleteDoc(docRef);
```

### 5. What are Firestore Security Rules?

**Answer:** Firestore Security Rules are a flexible way to control access to documents and collections:

**Basic Structure:**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Rules go here
  }
}
```

**Common Patterns:**
```javascript
// Allow read/write for authenticated users
match /users/{userId} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}

// Public read, authenticated write
match /posts/{postId} {
  allow read: if true;
  allow write: if request.auth != null;
}
```

**Functions Available:**
- `request.auth`: Authentication information
- `request.resource`: New document data
- `resource`: Existing document data
- `get()`: Read other documents
- `exists()`: Check document existence

## Intermediate Level Questions

### 6. How does Firestore handle real-time updates?

**Answer:** Firestore provides real-time synchronization through snapshot listeners:

**Snapshot Listeners:**
```javascript
// Listen to document changes
const docRef = doc(db, 'users', 'user123');
const unsubscribe = onSnapshot(docRef, (doc) => {
  console.log('Current data:', doc.data());
});

// Listen to query changes
const q = query(collection(db, 'posts'), orderBy('created_at', 'desc'));
const unsubscribeQuery = onSnapshot(q, (querySnapshot) => {
  querySnapshot.docChanges().forEach((change) => {
    if (change.type === 'added') {
      console.log('New post:', change.doc.data());
    }
  });
});
```

**How it Works:**
1. Client establishes listener connection
2. Server sends initial data snapshot
3. Server monitors for changes
4. Changes sent to client in real-time
5. Client updates local cache and UI

**Performance Considerations:**
- Listeners consume resources
- Unsubscribe when not needed
- Use appropriate query scopes

### 7. Explain Firestore's offline capabilities.

**Answer:** Firestore provides robust offline support:

**Offline Persistence:**
- Automatic local caching of data
- Disk persistence for large datasets
- Configurable cache size limits

**Offline Operations:**
- Read cached data without network
- Queue write operations for later sync
- Automatic conflict resolution

**Sync Process:**
1. **Queue Operations**: Writes stored locally when offline
2. **Reconnection**: Sync begins when connection restored
3. **Upload Changes**: Local changes sent to server
4. **Download Changes**: Server changes downloaded
5. **Conflict Resolution**: Merge local and server changes

**Conflict Resolution Strategies:**
- **Last-write-wins**: Simple automatic resolution
- **Custom logic**: Application-defined merge rules
- **Manual resolution**: User-guided conflict handling

### 8. How do you query data in Firestore?

**Answer:** Firestore supports various query types:

**Simple Queries:**
```javascript
// Equality query
const q1 = query(collection(db, 'users'), where('city', '==', 'New York'));

// Range query
const q2 = query(collection(db, 'products'), where('price', '>', 100));

// Array query
const q3 = query(collection(db, 'posts'), where('tags', 'array-contains', 'tech'));
```

**Compound Queries:**
```javascript
// Multiple conditions
const q = query(
  collection(db, 'products'),
  where('category', '==', 'electronics'),
  where('price', '<', 1000),
  orderBy('price', 'desc'),
  limit(10)
);
```

**Limitations:**
- Inequality filters limited to one field
- Must have composite indexes for compound queries
- No JOIN operations (use denormalization or references)

### 9. What are Firestore indexes and how do they work?

**Answer:** Firestore uses indexes for efficient query execution:

**Automatic Indexes:**
- Single-field indexes created automatically
- Enable simple equality and range queries
- No manual management required

**Composite Indexes:**
- Multi-field indexes for complex queries
- Required for compound queries
- Can include sort orders

**Index Creation:**
```javascript
// Automatic for simple queries
// Manual for complex queries
const index = {
  collectionGroup: 'posts',
  queryScope: 'COLLECTION',
  fields: [
    { fieldPath: 'category', order: 'ASCENDING' },
    { fieldPath: 'price', order: 'DESCENDING' }
  ]
};
```

**Index Management:**
- Automatic creation for most queries
- Manual creation for complex cases
- Index exemptions to reduce storage costs
- Monitoring index usage and performance

### 10. How do you handle relationships in Firestore?

**Answer:** Firestore handles relationships through several patterns:

**Document References:**
```javascript
// Store reference to another document
const userRef = doc(db, 'users', 'user123');
await updateDoc(postRef, {
  author: userRef,
  title: 'My Post'
});

// Fetch referenced document
const postDoc = await getDoc(postRef);
const authorRef = postDoc.data().author;
const authorDoc = await getDoc(authorRef);
```

**Denormalization:**
```javascript
// Duplicate data for read optimization
await setDoc(postRef, {
  title: 'My Post',
  authorName: 'John Doe',  // Denormalized
  authorId: 'user123'      // Reference
});
```

**Subcollections:**
```javascript
// Hierarchical relationships
const commentsRef = collection(db, 'posts', postId, 'comments');
await addDoc(commentsRef, {
  text: 'Great post!',
  authorId: 'user456'
});
```

**Collection Group Queries:**
```javascript
// Query across subcollections
const q = query(
  collectionGroup(db, 'comments'),
  where('authorId', '==', 'user456')
);
```

### 11. Explain Firestore's consistency model.

**Answer:** Firestore provides strong consistency with some optimizations:

**Strong Consistency:**
- All reads return the most recent writes
- No stale data in normal operations
- Global consistency across regions

**Optimizations:**
- **Latency-based routing**: Route to closest region
- **Read-your-writes**: Users see their own changes immediately
- **Monotonic reads**: No going back in time for a user

**Consistency Guarantees:**
- **Per-document**: Strong consistency for individual documents
- **Queries**: Consistent within a single query
- **Transactions**: ACID properties across multiple documents

**Trade-offs:**
- Strong consistency may have higher latency than eventual consistency
- Optimizations balance consistency with performance

### 12. How do you implement authentication and authorization in Firestore?

**Answer:** Firestore integrates with Firebase Authentication:

**Authentication Setup:**
```javascript
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const auth = getAuth();
await signInWithEmailAndPassword(auth, email, password);
```

**Security Rules with Auth:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    match /posts/{postId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null &&
        resource.data.authorId == request.auth.uid;
    }
  }
}
```

**Custom Claims:**
```javascript
// Set custom claims in Cloud Functions
await getAuth().setCustomUserClaims(uid, { admin: true });
```

**Authorization Patterns:**
- User-based access control
- Role-based permissions
- Resource ownership validation
- Time-based access restrictions

### 13. What are the performance considerations for Firestore?

**Answer:** Several factors affect Firestore performance:

**Query Optimization:**
- Use appropriate indexes
- Avoid full collection scans
- Limit result sets with pagination
- Use composite indexes for compound queries

**Data Structure:**
- Keep documents under 1MB
- Use subcollections for hierarchical data
- Denormalize for read-heavy workloads
- Avoid deep nesting in documents

**Client-Side Optimization:**
- Unsubscribe unused listeners
- Use offline persistence wisely
- Batch multiple operations
- Implement caching strategies

**Monitoring:**
- Track read/write operation counts
- Monitor latency percentiles
- Analyze query performance
- Set up alerts for performance issues

### 14. How does Firestore handle transactions?

**Answer:** Firestore supports ACID transactions:

**Transaction Syntax:**
```javascript
await runTransaction(db, async (transaction) => {
  const userRef = doc(db, 'users', 'user123');
  const accountRef = doc(db, 'accounts', 'acc456');

  const userDoc = await transaction.get(userRef);
  const accountDoc = await transaction.get(accountRef);

  if (userDoc.exists() && accountDoc.exists()) {
    const newBalance = accountDoc.data().balance - 100;
    transaction.update(accountRef, { balance: newBalance });
    transaction.update(userRef, { lastTransaction: serverTimestamp() });
  }
});
```

**Transaction Properties:**
- **Atomic**: All operations succeed or all fail
- **Consistent**: Database remains in valid state
- **Isolated**: Concurrent transactions don't interfere
- **Durable**: Changes persist after commit

**Limitations:**
- Maximum 500 operations per transaction
- Cannot contain get() operations after write operations
- Must read documents before writing them

### 15. How do you export and import data in Firestore?

**Answer:** Firestore provides several data export/import options:

**BigQuery Export:**
```javascript
// Scheduled daily export
gcloud firestore export gs://my-bucket/export --collection-ids=users,posts
```

**Manual Export:**
```javascript
// Export specific collections
gcloud firestore export gs://my-bucket/export \
  --collection-ids=users \
  --collection-ids=posts
```

**Import Operations:**
```javascript
// Import from export
gcloud firestore import gs://my-bucket/export/2023-01-01T12:00:00_12345/
```

**BigQuery Integration:**
- Scheduled exports to BigQuery
- Real-time analytics on Firestore data
- Advanced querying and reporting

**Migration Tools:**
- Database Migration Service for other databases
- Third-party tools for complex migrations
- Custom scripts for data transformation

## Advanced Level Questions

### 16. Design a real-time chat application using Firestore.

**Answer:** Architecture for a real-time chat application:

**Data Model:**
```javascript
// Users collection
{
  userId: "user123",
  name: "John Doe",
  email: "john@example.com",
  online: true,
  lastSeen: timestamp
}

// Chats collection (subcollection of users)
{
  chatId: "chat456",
  participants: ["user123", "user789"],
  lastMessage: "Hello!",
  lastMessageTime: timestamp,
  unreadCount: { user123: 0, user789: 2 }
}

// Messages subcollection (under chats)
{
  messageId: "msg789",
  senderId: "user123",
  text: "Hello World!",
  timestamp: timestamp,
  readBy: ["user123"]
}
```

**Real-time Features:**
```javascript
// Listen to chat list
const chatsQuery = query(
  collection(db, 'users', currentUserId, 'chats'),
  orderBy('lastMessageTime', 'desc')
);

onSnapshot(chatsQuery, (snapshot) => {
  // Update chat list UI
});

// Listen to messages in active chat
const messagesQuery = query(
  collection(db, 'chats', chatId, 'messages'),
  orderBy('timestamp', 'asc')
);

onSnapshot(messagesQuery, (snapshot) => {
  // Update messages UI
});
```

**Performance Optimizations:**
- Pagination for message history
- Unread count denormalization
- Presence indicators
- Message caching

### 17. How would you implement data validation in Firestore?

**Answer:** Multiple approaches to data validation:

**Security Rules Validation:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow create: if validateUserData(request.resource.data);
      allow update: if validateUserUpdate(request.resource.data, resource.data);
    }

    function validateUserData(userData) {
      return userData.keys().hasAll(['name', 'email']) &&
             userData.name is string &&
             userData.name.size() > 0 &&
             userData.email.matches('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}');
    }
  }
}
```

**Client-Side Validation:**
```javascript
function validateUserData(data) {
  if (!data.name || typeof data.name !== 'string') {
    throw new Error('Name is required and must be a string');
  }
  if (!data.email || !isValidEmail(data.email)) {
    throw new Error('Valid email is required');
  }
  return true;
}
```

**Cloud Functions Validation:**
```javascript
exports.validateUserData = functions.firestore
  .document('users/{userId}')
  .onWrite((change, context) => {
    const data = change.after.data();
    if (!validateUserData(data)) {
      throw new functions.https.HttpsError('invalid-argument', 'Invalid user data');
    }
  });
```

**Best Practices:**
- Validate at multiple layers
- Use consistent validation rules
- Provide clear error messages
- Test validation thoroughly

### 18. Explain the cost structure of Firestore and optimization strategies.

**Answer:** Firestore pricing includes several components:

**Operation Costs:**
- **Reads**: $0.06 per 100,000 document reads
- **Writes**: $0.18 per 100,000 document writes
- **Deletes**: $0.02 per 100,000 document deletes

**Storage Costs:**
- **Document storage**: $0.18/GB/month
- **Index storage**: Additional cost for indexes

**Network Costs:**
- **Egress**: $0.12/GB for data transfer

**Optimization Strategies:**

**Minimize Operations:**
```javascript
// Use listeners instead of polling
const unsubscribe = onSnapshot(query, (snapshot) => {
  // Handle real-time updates
});

// Batch operations
const batch = writeBatch(db);
batch.set(doc1, data1);
batch.set(doc2, data2);
await batch.commit();
```

**Optimize Data Structure:**
- Denormalize for read-heavy workloads
- Use subcollections appropriately
- Keep documents under 1MB

**Query Optimization:**
- Use appropriate indexes
- Limit result sets
- Avoid expensive queries

### 19. How do you handle large-scale data migrations to Firestore?

**Answer:** Strategies for large-scale migrations:

**Planning Phase:**
- Analyze source data structure
- Design Firestore data model
- Estimate migration time and costs
- Plan rollback strategy

**Migration Tools:**
```javascript
// Using Dataflow for large migrations
const pipeline = Pipeline.create()
  .apply('Read from Source',
    DatastoreIO.read().withQuery(query))
  .apply('Transform Data',
    ParDo.of(new TransformFn()))
  .apply('Write to Firestore',
    FirestoreIO.write()
      .withCollectionId('collection')
      .withEntityProvider(entityProvider));
```

**Chunking Strategy:**
- Process data in batches
- Use parallel workers
- Implement checkpointing
- Handle failures gracefully

**Validation:**
- Compare record counts
- Validate data integrity
- Test application functionality
- Performance benchmarking

**Post-Migration:**
- Update application code
- Monitor performance
- Optimize as needed
- Clean up source data

### 20. Design a multi-tenant application using Firestore.

**Answer:** Multi-tenant architecture patterns:

**Tenant Isolation Strategies:**

**Database-per-Tenant:**
- Complete isolation
- Higher management overhead
- Maximum security
- Cost scales with tenants

**Collection-per-Tenant:**
```javascript
// Separate collections for each tenant
const tenantUsersRef = collection(db, `tenant_${tenantId}_users`);
const tenantPostsRef = collection(db, `tenant_${tenantId}_posts`);
```

**Document-per-Tenant:**
```javascript
// Tenant ID in document path
const userRef = doc(db, 'tenants', tenantId, 'users', userId);
const postRef = doc(db, 'tenants', tenantId, 'posts', postId);
```

**Security Implementation:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /tenants/{tenantId}/{document=**} {
      allow read, write: if request.auth != null &&
        getTenantUser(request.auth.uid, tenantId).exists;
    }

    function getTenantUser(userId, tenantId) {
      return get(/databases/$(database)/documents/tenants/$(tenantId)/users/$(userId));
    }
  }
}
```

**Performance Considerations:**
- Index tenant-specific queries
- Monitor per-tenant usage
- Implement tenant quotas
- Optimize for tenant access patterns

### 21. How do you implement full-text search in Firestore?

**Answer:** Full-text search implementation approaches:

**Basic Text Search:**
```javascript
// Store searchable text as array
await setDoc(postRef, {
  title: 'My Blog Post',
  content: 'This is the content...',
  searchTerms: ['my', 'blog', 'post', 'content']  // Tokenized
});

// Query using array-contains
const q = query(
  collection(db, 'posts'),
  where('searchTerms', 'array-contains', 'blog')
);
```

**Third-Party Integration:**
```javascript
// Use Algolia or Elasticsearch
const algoliaIndex = client.initIndex('posts');

exports.onPostWrite = functions.firestore
  .document('posts/{postId}')
  .onWrite((change, context) => {
    const post = change.after.data();
    return algoliaIndex.saveObject({
      objectID: context.params.postId,
      title: post.title,
      content: post.content
    });
  });
```

**BigQuery Integration:**
- Export data to BigQuery
- Use BigQuery's search functions
- Scheduled exports for search indexing

**Client-Side Search:**
- Download data to client
- Implement client-side search
- Suitable for small datasets

### 22. Explain Firestore's regional vs multi-regional deployment.

**Answer:** Deployment options for different use cases:

**Regional Deployment:**
- Single region (e.g., us-central1)
- Lower latency for regional users
- 99.99% availability SLA
- Cost-effective for non-global apps

**Multi-Regional Deployment:**
- Multiple regions (e.g., nam3: 3 US regions)
- Global distribution
- 99.999% availability SLA
- Higher cost but maximum resilience

**Choosing Deployment:**
- **Regional**: Apps with regional user base, cost-sensitive
- **Multi-regional**: Global apps, financial services, high availability requirements

**Trade-offs:**
- **Latency**: Regional lower for local users
- **Cost**: Multi-regional more expensive
- **Availability**: Multi-regional higher SLA
- **Data residency**: Regional for compliance

### 23. How do you implement optimistic concurrency control in Firestore?

**Answer:** Optimistic concurrency for conflict resolution:

**Version-Based Updates:**
```javascript
// Include version field
await setDoc(userRef, {
  name: 'John Doe',
  version: 1,
  updated_at: serverTimestamp()
});

// Update with version check
await runTransaction(db, async (transaction) => {
  const doc = await transaction.get(userRef);
  if (doc.data().version !== expectedVersion) {
    throw new Error('Document was modified by another user');
  }

  transaction.update(userRef, {
    name: 'Jane Doe',
    version: expectedVersion + 1,
    updated_at: serverTimestamp()
  });
});
```

**ETag-Based Updates:**
```javascript
// Use document ETag
const doc = await getDoc(userRef);
await updateDoc(userRef, {
  name: 'Jane Doe',
  updated_at: serverTimestamp()
}, {
  merge: true,
  // Firestore handles ETag internally
});
```

**Conflict Resolution Strategies:**
- **Fail on conflict**: Reject conflicting updates
- **Merge changes**: Combine conflicting updates
- **Last-write-wins**: Accept latest update
- **Custom resolution**: Application-specific logic

### 24. Design a monitoring and alerting strategy for Firestore.

**Answer:** Comprehensive monitoring strategy:

**Key Metrics to Monitor:**
- Read/write/delete operation counts
- Latency percentiles (P50, P95, P99)
- Error rates and types
- Storage utilization

**Cloud Monitoring Setup:**
```javascript
// Custom metrics
const metric = {
  type: 'custom.googleapis.com/firestore/operations',
  labels: {
    operation: 'read',
    collection: 'users'
  },
  value: operationCount
};
```

**Alerting Policies:**
- High latency alerts (> 1s P95)
- Error rate alerts (> 5%)
- Storage utilization (> 80%)
- Operation rate anomalies

**Dashboard Creation:**
- Real-time performance dashboard
- Historical trend analysis
- Per-collection metrics
- Cost monitoring

**Incident Response:**
- Automated alerts to on-call
- Runbooks for common issues
- Escalation procedures
- Post-mortem analysis

### 25. How does Firestore compare to MongoDB?

**Answer:** Key comparisons between Firestore and MongoDB:

**Data Model:**
- **Firestore**: Document-based with real-time sync
- **MongoDB**: Document-based with flexible schemas

**Scalability:**
- **Firestore**: Automatic scaling, serverless
- **MongoDB**: Manual cluster management, replica sets

**Consistency:**
- **Firestore**: Strong consistency globally
- **MongoDB**: Configurable consistency (strong/eventual)

**Real-time Features:**
- **Firestore**: Built-in real-time synchronization
- **MongoDB**: Requires additional technologies (Change Streams + WebSockets)

**Operations:**
- **Firestore**: Pay-per-operation pricing
- **MongoDB**: Pay-per-cluster pricing

**Ecosystem:**
- **Firestore**: Deep Firebase/GCP integration
- **MongoDB**: Broad third-party tool support

**Use Cases:**
- **Firestore**: Mobile/web apps, real-time features, serverless
- **MongoDB**: General-purpose, complex analytics, custom deployments

## Scenario-Based Questions

### 26. Your Firestore queries are slow. How do you troubleshoot?

**Answer:** Systematic approach to query performance issues:

1. **Check Query Structure:**
   - Review query for missing indexes
   - Verify compound query requirements
   - Check for single vs composite indexes

2. **Analyze Index Usage:**
   - Use Firebase Console to check index status
   - Verify automatic index creation
   - Create manual composite indexes if needed

3. **Examine Data Structure:**
   - Check document sizes (keep under 1MB)
   - Review collection structure
   - Consider denormalization for read optimization

4. **Monitor Performance Metrics:**
   - Check latency percentiles in Cloud Monitoring
   - Analyze read operation counts
   - Identify expensive queries

5. **Optimize Query Patterns:**
   - Use pagination for large result sets
   - Implement appropriate sorting and filtering
   - Consider collection group queries for subcollections

### 27. Design a social media application using Firestore.

**Answer:** Social media application architecture:

**Data Model:**
```javascript
// Users collection
{
  userId: "user123",
  username: "johndoe",
  profile: {
    name: "John Doe",
    bio: "Software engineer",
    avatar: "gs://bucket/avatar.jpg"
  },
  followers: ["user456", "user789"],  // Denormalized
  following: ["user456"]
}

// Posts collection
{
  postId: "post456",
  authorId: "user123",
  content: "My first post!",
  media: ["gs://bucket/image.jpg"],
  likes: ["user456", "user789"],  // Denormalized
  created_at: timestamp
}

// Comments subcollection (under posts)
{
  commentId: "comment789",
  authorId: "user456",
  text: "Great post!",
  likes: ["user123"],
  created_at: timestamp
}
```

**Real-time Features:**
- Live feed updates
- Notification system
- Online presence indicators

**Performance Optimizations:**
- Denormalize counts and references
- Use pagination for feeds
- Implement caching strategies
- Optimize image loading

### 28. How would you implement user authentication and data security?

**Answer:** Comprehensive security implementation:

**Authentication Setup:**
```javascript
// Firebase Auth integration
import { getAuth, onAuthStateChanged } from 'firebase/auth';

onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in
    console.log('User:', user.uid);
  } else {
    // User is signed out
  }
});
```

**Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Posts are public for reading, authenticated for writing
    match /posts/{postId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null &&
        resource.data.authorId == request.auth.uid;
    }

    // Comments under posts
    match /posts/{postId}/comments/{commentId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

**Additional Security:**
- Input validation
- Rate limiting
- Audit logging
- Data encryption

### 29. Your Firestore costs are too high. How do you optimize?

**Answer:** Cost optimization strategies:

**Operation Optimization:**
- **Listeners**: Unsubscribe unused listeners
- **Batching**: Combine multiple operations
- **Caching**: Implement client-side caching
- **Pagination**: Limit query result sizes

**Query Optimization:**
- **Indexes**: Remove unused indexes
- **Queries**: Use efficient query patterns
- **Denormalization**: Reduce cross-document reads
- **Offline**: Leverage offline persistence

**Data Structure Optimization:**
- **Document size**: Keep under 1MB limit
- **Subcollections**: Use appropriate hierarchy
- **References**: Minimize document references
- **Arrays**: Use arrays for small lists

**Monitoring and Alerts:**
- Set up cost alerts
- Monitor usage patterns
- Identify cost spikes
- Implement usage quotas

### 30. Explain how to implement offline-first functionality.

**Answer:** Offline-first implementation strategy:

**Enable Offline Persistence:**
```javascript
// Web SDK
import { getFirestore, enableIndexedDbPersistence } from 'firebase/firestore';

const db = getFirestore();
enableIndexedDbPersistence(db)
  .catch((err) => {
    if (err.code == 'failed-precondition') {
      console.log('Multiple tabs open, persistence can only be enabled in one tab at a time.');
    } else if (err.code == 'unimplemented') {
      console.log('The current browser does not support all of the features required to enable persistence');
    }
  });
```

**Offline Write Handling:**
```javascript
// Queue writes for offline
function addPost(content) {
  const postRef = doc(collection(db, 'posts'));
  setDoc(postRef, {
    content: content,
    authorId: currentUser.uid,
    created_at: serverTimestamp(),
    offline: true  // Mark as offline write
  });
}
```

**Sync Strategy:**
```javascript
// Handle reconnection
window.addEventListener('online', () => {
  // Sync pending changes
  syncOfflineChanges();
});

function syncOfflineChanges() {
  // Query offline documents
  const q = query(
    collection(db, 'posts'),
    where('offline', '==', true)
  );

  getDocs(q).then((snapshot) => {
    snapshot.forEach((doc) => {
      // Update timestamp and remove offline flag
      updateDoc(doc.ref, {
        created_at: serverTimestamp(),
        offline: deleteField()
      });
    });
  });
}
```

**Conflict Resolution:**
- Implement custom merge logic
- Use version fields for conflict detection
- Provide user interface for conflict resolution
- Test offline scenarios thoroughly

This comprehensive set of Cloud Firestore interview questions covers everything from basic document operations to advanced real-time architectures, ensuring candidates understand both the Firebase-integrated NoSQL database and its role in modern application development.
