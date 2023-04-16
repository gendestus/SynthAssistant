import datetime
import uuid

class Memory:
    id: uuid.UUID
    type: str
    value: str
    timestamp: int
    importance: float
    recall_trigger: str
    distance: float = 1000
    recent_threshold: int = 3600
    recency_weight: float = 1.0
    importance_weight: float = 1.0
    relevancy_weight: float = 1.0

    def calc_score(self):
        # get recency score 0.0 to 1.0 where 1.0 is now and 0.0 is {recent_threshold} seconds ago
        recency_score = 1.0 - (self.timestamp - int(datetime.datetime.now().timestamp())) / self.recent_threshold
        
        # get importance score 0.0 to 1.0 where 1.0 is most important and 0.0 is least important
        # keep in mind that importance is from 1.0 to 10.0
        importance_score = self.importance / 10.0

        # get relevancy score based on the distance between the recall trigger and the memory
        # distance will usually fall between 0.0 and 10.0
        # values greater than 10.0 should be treated as 10.0
        relevancy_score = 1.0 - (self.distance / 10.0)

        return (recency_score * self.recency_weight) + (importance_score * self.importance_weight) + (relevancy_score * self.relevancy_weight)