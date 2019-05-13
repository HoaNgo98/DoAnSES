import threading
import itertools


class TriggeredThread(threading.Thread):
    def __init__(self, sequence=None, *args, **kwargs):
        self.sequence = sequence
        self.lock = threading.Condition()
        self.event = threading.Event()
        threading.Thread.__init__(self, *args, **kwargs)

    def __enter__(self):
        self.lock.acquire()
        while not self.event.is_set():
            self.lock.wait()
        self.event.clear()

    def __exit__(self, *args):
        self.lock.release()
        if self.sequence:
            next(self.sequence).trigger()

    def trigger(self):
        with self.lock:
            self.event.set()
            self.lock.notify()

spam = []  # Use a list to share values across threads.
results = []  # Register the results.

def set_spam():
    thread = threading.current_thread()
    with thread:  # Acquires the lock.
        # Set 'spam' to thread name
        spam[:] = [thread.name]
    # Thread 'releases' the lock upon exiting the context.
    # The next thread is triggered and this thread waits for a trigger.
    with thread:
        # Since each thread overwrites the content of the 'spam'
        # list, this should only result in True for the last thread.
        results.append(spam == [thread.name])

threads = [
    TriggeredThread(name='a', target=set_spam),
    TriggeredThread(name='b', target=set_spam),
    TriggeredThread(name='c', target=set_spam)]

# Create a shifted sequence of threads and share it among the threads.
thread_sequence = itertools.cycle(threads[1:] + threads[:1])
for thread in threads:
    thread.sequence = thread_sequence

# Start each thread
[thread.start() for thread in threads]
# Trigger first thread.
# That thread will trigger the next thread, and so on.
threads[0].trigger()
# Wait for each thread to finish.
[thread.join() for thread in threads]
# The last thread 'has won the race' overwriting the value
# for 'spam', thus [False, False, True].
# If set_spam were thread-safe, all results would be true.
if results == [False, False, True]:
    print("race condition triggered")
elif results == [True, True, True]:
    print("code is thread-safe")
# assert results == [False, False, True], "race condition triggered"
# assert results == [True, True, True], "code is thread-safe"