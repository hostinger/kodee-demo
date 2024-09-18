def meta(**metadata):
    def decorator(func):
        if not hasattr(func, "meta"):
            func.meta = []
        func.meta.append(metadata)
        return func

    return decorator
