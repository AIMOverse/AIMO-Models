class MockRedis:
    """Mock Redis client for testing"""
    
    def __init__(self):
        self.data = {}
        self.expire_times = {}
        
    def get(self, key):
        """Get stored value, return None if not exists"""
        return self.data.get(key)
        
    def set(self, key, value, ex=None):
        """Set key-value, optional expiration time"""
        self.data[key] = value
        if ex:
            self.expire_times[key] = ex
        return True
        
    def incr(self, key):
        """Increment key value"""
        if key not in self.data:
            self.data[key] = "0"
        value = int(self.data[key]) + 1
        self.data[key] = str(value)
        return value
        
    def expire(self, key, seconds):
        """Set key expiration time"""
        self.expire_times[key] = seconds
        return True
        
    def ttl(self, key):
        """Get remaining time to live of a key"""
        return self.expire_times.get(key, -2)
        
    def pipeline(self):
        """Return a pipeline instance (self)"""
        return self
        
    def execute(self):
        """Execute pipeline commands (mock)"""
        return [True, True]