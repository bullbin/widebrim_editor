def fsLog(*args, **kwargs):
    print("[FS - Normal]", *args, **kwargs)

def fsLogSpam(*args, **kwargs):
    print("[FS - Vrbose]", *args, **kwargs)

def fsLogWarn(*args, **kwargs):
    print("[FS -  Warn ]", *args, **kwargs)

def fsLogSevere(*args, **kwargs):
    print("[FS - Severe]", *args, **kwargs)