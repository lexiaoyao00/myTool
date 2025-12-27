import enum


class FileType(enum.Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    OTHER = 'other'

def judge_file_type(file_path:str) -> str:
    file_suffix = file_path.split('.')[-1].lower()
    if file_suffix in ['jpg','jpeg','png','gif']:
        return FileType.IMAGE
    elif file_suffix in ['mp4','webm','mkv']:
        return FileType.VIDEO
    else:
        return file_suffix

class CommandType(enum.Enum):
    START = 'start'
    STOP = 'stop'

class TopicName(enum.Enum):
    SPIDER = 'spider'
    LOGIN = 'login'
