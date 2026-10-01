"""
Greedy TSP stroke sequencing and direction optimizer to minimize pen-up travel time.
"""

from typing import List
import math

try:
    from src.core.models import ContourPoints
except (ImportError, ModuleNotFoundError):
    from core.models import ContourPoints  # type: ignore


def sort_contours_greedy(contours: List[ContourPoints]) -> List[ContourPoints]:
    """
    Reorders contours by proximity using a greedy nearest-neighbor approach.
    Reverses individual stroke direction if drawing end-to-start minimizes distance.
    """
    if not contours:
        return []

    unvisited = contours.copy()
    sorted_contours: List[ContourPoints] = []
    current = unvisited.pop(0)
    sorted_contours.append(current)

    while unvisited:
        last_point = current[-1]
        best_idx = 0
        best_dist = float('inf')
        should_reverse = False

        for idx, cnt in enumerate(unvisited):
            start_pt = cnt[0]
            end_pt = cnt[-1]
            d_start = math.hypot(last_point[0] - start_pt[0], last_point[1] - start_pt[1])
            d_end = math.hypot(last_point[0] - end_pt[0], last_point[1] - end_pt[1])

            if d_start < best_dist:
                best_dist = d_start
                best_idx = idx
                should_reverse = False

            if d_end < best_dist:
                best_dist = d_end
                best_idx = idx
                should_reverse = True

        next_cnt = unvisited.pop(best_idx)
        if should_reverse:
            next_cnt = next_cnt[::-1]

        sorted_contours.append(next_cnt)
        current = next_cnt

    return sorted_contours
