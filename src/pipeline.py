import cv2
from abc import ABC, abstractmethod
from typing import Optional

class VideoEffect(ABC):
    @abstractmethod
    def process(self, frame):
        pass


class VideoPipeline:
    def __init__(self):
        self.effects = []
    
    def add_effect(self, effect: VideoEffect):
        self.effects.append(effect)
        return self
    
    def process_frame(self, frame):
        result = frame
        for effect in self.effects:
            result = effect.process(result)
        return result
