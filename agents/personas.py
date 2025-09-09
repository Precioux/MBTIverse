from __future__ import annotations
from agents.base_agent import BaseAgent

# Each class loads its MBTI prompt from prompts/{code}.txt

class ISTJAgent(BaseAgent):
    def __init__(self): super().__init__("ISTJ", "prompts/istj.txt")

class ISFJAgent(BaseAgent):
    def __init__(self): super().__init__("ISFJ", "prompts/isfj.txt")

class INFJAgent(BaseAgent):
    def __init__(self): super().__init__("INFJ", "prompts/infj.txt")

class INTJAgent(BaseAgent):
    def __init__(self): super().__init__("INTJ", "prompts/intj.txt")

class ISTPAgent(BaseAgent):
    def __init__(self): super().__init__("ISTP", "prompts/istp.txt")

class ISFPAgent(BaseAgent):
    def __init__(self): super().__init__("ISFP", "prompts/isfp.txt")

class INFPAgent(BaseAgent):
    def __init__(self): super().__init__("INFP", "prompts/infp.txt")

class INTPAgent(BaseAgent):
    def __init__(self): super().__init__("INTP", "prompts/intp.txt")

class ESTPAgent(BaseAgent):
    def __init__(self): super().__init__("ESTP", "prompts/estp.txt")

class ESFPAgent(BaseAgent):
    def __init__(self): super().__init__("ESFP", "prompts/esfp.txt")

class ENFPAgent(BaseAgent):
    def __init__(self): super().__init__("ENFP", "prompts/enfp.txt")

class ENTPAgent(BaseAgent):
    def __init__(self): super().__init__("ENTP", "prompts/entp.txt")

class ESTJAgent(BaseAgent):
    def __init__(self): super().__init__("ESTJ", "prompts/estj.txt")

class ESFJAgent(BaseAgent):
    def __init__(self): super().__init__("ESFJ", "prompts/esfj.txt")

class ENFJAgent(BaseAgent):
    def __init__(self): super().__init__("ENFJ", "prompts/enfj.txt")

class ENTJAgent(BaseAgent):
    def __init__(self): super().__init__("ENTJ", "prompts/entj.txt")
