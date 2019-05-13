import threading
# The thread local storage is a global.
# This may seem weird at first, but it isn't actually shared among threads.
data = threading.local()
data.spam = []  # This list only exists in this thread.
results = []  # Results *are* shared though.

def set_spam():
    thread = threading.current_thread()
    # 'get' or set the 'spam' list. This actually creates a new list.
    # If the list was shared among threads this would cause a race-condition.
    data.spam = getattr(data, 'spam', [])
    with thread:
        data.spam[:] = [thread.name]
    with thread:
        results.append(data.spam == [thread.name])

# Start the threads as in the example above.
set_spam()
print(data.spam)
assert all(results)  # All results should be True.