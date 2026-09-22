import time
from datetime import datetime
from functools import wraps


def my_generator():
    
    for i in range(1, 111, 1):
        yield i


def log_node(message: str = None, extract=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(state, config=None):
            print(f"\n{'─'*40}")
            print(f"Nodo → {fn.__name__}")
            print(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

            start = time.time()
            result = fn(state, config) if config is not None else fn(state)
            elapsed = time.time() - start

            if message and extract:
                try:
                    values = extract(result)
                    print(message.format(*values))
                except Exception as e:
                    print(f"[log] impossibile formattare: {e}")
            
            print(f"✔  Fine ({elapsed:.2f}s)")
            print(f"{'─'*40}")
            return result
        return wrapper
    return decorator


def log_worker_node(fn):
    def wrapper(state, config):
        global generator
        numero_nodo = next(generator)
        print(f"In esecuzione nodo num {numero_nodo}")
        result = fn(state, config)
        print(f'Fine esecuzione nodo num {numero_nodo}')
        return result
    return wrapper



generator = my_generator()