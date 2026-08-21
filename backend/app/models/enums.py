import enum


class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Topic(str, enum.Enum):
    ARRAY = "ARRAY"
    STRING = "STRING"
    LINKED_LIST = "LINKED_LIST"
    STACK = "STACK"
    QUEUE = "QUEUE"
    TREE = "TREE"
    GRAPH = "GRAPH"
    DP = "DP"


class SubmissionStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TLE = "TLE"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"


class Language(str, enum.Enum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
