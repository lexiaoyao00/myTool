def fileType(file_path:str) -> str:
    file_suffix = file_path.split('.')[-1].lower()
    if file_suffix in ['jpg','jpeg','png','gif']:
        return 'image'
    elif file_suffix in ['mp4','webm','mkv']:
        return 'video'
    else:
        return file_suffix