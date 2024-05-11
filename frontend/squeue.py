import heapq

class QueueInterface:
    def enqueue(self, job):
        pass
    
    def dequeue(self, job):
        pass

    def is_empty(self):
        pass

class FIFOQueue(QueueInterface):
    def __init__(self):
        self.queue = []
    
    def enqueue(self, job):
        self.queue.append(job)
    
    def dequeue(self):
        if not self.is_empty():
            return self.queue.pop(0)
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    

class SRTFPriorityQueue(QueueInterface):
    def __init__(self):
        self.queue = []

    def enqueue(self, job):
        heapq.heappush(self.queue, (job._remainingTime, job))
    
    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)[1]
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    
    def get_hp_remainingTime(self):
        if not self.is_empty():
            return self.queue[0][1]._remainingTime
        else:
            return None
        
class SEALPriorityQueue(QueueInterface):
    def __init__(self):
        self.queue = []

    def enqueue(self, job):
        heapq.heappush(self.queue, (job.Priority, job))
    
    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)[1]
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    
    def get_hp_priority(self):
        if not self.is_empty():
            return self.queue[0][1].Priority
        else:
            return None

class SFSPriorityQueue(QueueInterface):
    def __init__(self):
        self.queue = []

    def firstEnqueue(self, job):
        heapq.heappush(self.queue, (0, job))

    def enqueue(self, job):
        heapq.heappush(self.queue, (job.Priority, job))

    def dequeue(self):
        if not self.is_empty():
            return heapq.heappop(self.queue)[1]
        else:
            return None
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def __len__(self):
        return len(self.queue)
    
    def get_hp_priority(self):
        if not self.is_empty():
            return self.queue[0][1].Priority
        else:
            return None