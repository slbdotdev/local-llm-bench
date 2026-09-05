def add_waiting(queue, item):
    queue.append(item)


def take_oldest(queue):
    if queue:
        return queue.pop(0)
    return None
