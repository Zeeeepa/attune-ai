# Redis Setup Guide

## Overview

Redis provides enhanced features for Empathy Framework:
- **Session Management**: Fast, TTL-based working memory for agent coordination
- **Real-time Coordination**: Pub/Sub messaging between agents
- **Caching**: Two-tier caching (memory + Redis) for performance
- **Task Queues**: Distributed task management
- **Audit Trails**: Redis Streams for event logging

**Redis is OPTIONAL** - The framework works perfectly without it using in-memory mock mode.

---

## Quick Start (macOS)

### 1. Install Redis

```bash
# Using Homebrew (recommended)
brew install redis

# Start Redis service
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return: PONG
```

### 2. Enable Redis in Empathy Framework

Add to your `.env` file:

```bash
# Redis Configuration (Local Development)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=  # Leave empty if no password
```

### 3. Test Your Setup

```python
from attune.memory.short_term import RedisShortTermMemory
from attune.memory.types import AgentCredentials, AccessTier

# Initialize Redis
memory = RedisShortTermMemory()
print(f"Redis connected: {memory.client is not None}")

# Test basic operation
creds = AgentCredentials("agent_1", AccessTier.CONTRIBUTOR)
memory.stash("test_key", {"data": "Hello Redis!"}, creds)
data = memory.retrieve("test_key", creds)
print(f"Retrieved: {data}")
```

---

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_ENABLED` | `false` | Enable/disable Redis (true/false) |
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number (0-15) |
| `REDIS_PASSWORD` | None | Redis password (if required) |

### Programmatic Configuration

```python
from attune.memory.short_term import RedisShortTermMemory
from attune.memory.types import RedisConfig

# Option 1: Using environment variables (recommended)
memory = RedisShortTermMemory()

# Option 2: Direct configuration
config = RedisConfig(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    ssl=False,  # Enable for managed Redis services
)
memory = RedisShortTermMemory(config=config)

# Option 3: Force mock mode for testing
memory = RedisShortTermMemory(use_mock=True)
```

---

## Features

### 1. Role-Based Access Control

```python
from attune.memory.types import AccessTier

# Different access tiers
reader = AgentCredentials("agent_reader", AccessTier.READER)
contributor = AgentCredentials("agent_contributor", AccessTier.CONTRIBUTOR)
coordinator = AgentCredentials("agent_coordinator", AccessTier.COORDINATOR)
```

### 2. TTL-Based Expiration

```python
from attune.memory.types import TTLStrategy

# Data expires after 1 hour
memory.stash("temp_data", {"value": 42}, creds, ttl_seconds=3600)

# Use TTL strategies
strategy = TTLStrategy.MEDIUM  # 1 hour
memory.stash("working_data", data, creds, ttl_strategy=strategy)
```

### 3. Pub/Sub for Real-Time Coordination

```python
# Subscribe to agent signals
def on_message(msg):
    print(f"Received: {msg}")

memory.subscribe("agent_signals", on_message)

# Publish from another agent
memory.publish("agent_signals", {"event": "task_complete"}, creds)
```

### 4. Batch Operations

```python
# Stash multiple items efficiently
items = [
    ("key1", {"data": 1}),
    ("key2", {"data": 2}),
    ("key3", {"data": 3}),
]
memory.stash_batch(items, creds)

# Retrieve multiple items
keys = ["key1", "key2", "key3"]
results = memory.retrieve_batch(keys, creds)
```

---

## For New Users (Redis Disabled by Default)

If you download Empathy Framework for the first time:

1. **Redis is NOT required** - The framework works out of the box
2. **Mock mode is automatic** - In-memory storage is used by default
3. **No setup needed** - Just start using the framework

### When to Enable Redis

Enable Redis when you need:
- ✅ Multi-agent coordination across processes
- ✅ Persistent session management
- ✅ Real-time pub/sub messaging
- ✅ Production-grade caching
- ✅ Distributed task queues

---

## Troubleshooting

### Redis Not Connecting

```bash
# Check if Redis is running
redis-cli ping

# If not running, start it
brew services start redis

# Check Redis logs
tail -f /opt/homebrew/var/log/redis.log
```

### Permission Errors

```bash
# Check Redis configuration
redis-cli CONFIG GET requirepass

# If password is set, add to .env
REDIS_PASSWORD=your_password_here
```

### Port Already in Use

```bash
# Check what's using port 6379
lsof -i :6379

# Use a different port
REDIS_PORT=6380
```

---

## Production Deployment

### Managed Redis Services

For production, use managed Redis services:

- **AWS ElastiCache**: Enterprise-grade, managed Redis
- **Redis Cloud**: Official Redis hosting
- **Google Cloud Memorystore**: GCP-integrated Redis

### Security Configuration

```bash
# Enable SSL/TLS
REDIS_ENABLED=true
REDIS_HOST=your-redis.cloud.redislabs.com
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password
REDIS_SSL=true
```

### High Availability

```python
config = RedisConfig(
    host="redis-primary.example.com",
    port=6379,
    password="secure_password",
    ssl=True,
    retry_max_attempts=5,  # Retry on failure
    retry_base_delay=0.1,  # Start with 100ms
    retry_max_delay=5.0,   # Max 5 seconds between retries
)
```

---

## Monitoring

### Check Metrics

```python
memory = RedisShortTermMemory()

print(f"Total requests: {memory.metrics.total_requests}")
print(f"Success rate: {memory.metrics.success_rate}%")
print(f"Average latency: {memory.metrics.latency_avg_ms}ms")
print(f"Retries: {memory.metrics.retries_total}")
```

### Redis CLI Commands

```bash
# Monitor all commands
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# List all keys
redis-cli KEYS "empathy:*"

# Get key value
redis-cli GET empathy:working:my_key
```

---

## Summary

- **Optional**: Redis is NOT required for Empathy Framework
- **Easy Setup**: 3 steps to enable on macOS
- **Automatic Fallback**: Mock mode when Redis is disabled
- **Production Ready**: SSL, retries, high availability support
- **Well Tested**: 4 of 5 Redis initialization tests passing

For questions or issues, see: [GitHub Issues](https://github.com/Smart-AI-Memory/attune-ai/issues)
