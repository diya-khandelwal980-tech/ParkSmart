
import heapq
import time


# 1. GREEDY ALGORITHM
def find_best_slot(parking_slots):
    start = time.perf_counter()

    available = [
        slot for slot in parking_slots
        if slot["status"].lower() == "available"
    ]

    if not available:
        return None, (time.perf_counter() - start) * 1000

    # Select the nearest available slot.
    best_slot = min(
        available,
        key=lambda slot: (slot["distance"], slot["slot_number"])
    )

    elapsed = (time.perf_counter() - start) * 1000
    return best_slot, elapsed


# 2. DIJKSTRA'S SHORTEST PATH ALGORITHM
def dijkstra(graph, start, end):
    start_time = time.perf_counter()

    if start not in graph or end not in graph:
        elapsed = (time.perf_counter() - start_time) * 1000
        return [], None, elapsed

    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}

    distances[start] = 0
    queue = [(0, start)]

    while queue:
        current_distance, current = heapq.heappop(queue)

        if current_distance > distances[current]:
            continue

        if current == end:
            break

        for neighbor, weight in graph[current].items():

            if neighbor not in distances:
                continue

            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

                heapq.heappush(
                    queue,
                    (new_distance, neighbor)
                )

    elapsed = (time.perf_counter() - start_time) * 1000

    if distances[end] == float("inf"):
        return [], None, elapsed

    # Reconstruct the shortest path.
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    return path, distances[end], elapsed


# 3. LINEAR SEARCH ALGORITHM
def linear_search(parking_slots, slot_number):
    start = time.perf_counter()

    search_value = slot_number.strip().lower()

    for slot in parking_slots:
        if slot["slot_number"].strip().lower() == search_value:
            elapsed = (time.perf_counter() - start) * 1000
            return slot, elapsed

    elapsed = (time.perf_counter() - start) * 1000
    return None, elapsed


# 4. SELECTION SORT ALGORITHM
def sort_slots_by_distance(parking_slots):
    slots = parking_slots.copy()
    n = len(slots)

    for i in range(n):
        min_index = i

        for j in range(i + 1, n):
            if slots[j]["distance"] < slots[min_index]["distance"]:
                min_index = j

        slots[i], slots[min_index] = slots[min_index], slots[i]

    return slots
