from difflib import SequenceMatcher
from .models import Complaint


def text_similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_similar_complaint(description, lat, lon, radius_km=1.0, threshold=0.7):
    """
    Lightweight duplicate detection (Render-friendly)
    """

    complaints = Complaint.objects.exclude(
        latitude=None
    ).exclude(
        longitude=None
    )

    best_match = None
    best_score = 0

    for comp in complaints:
        score = text_similarity(description, comp.description)

        if score > threshold and score > best_score:
            best_match = comp
            best_score = score

    return best_match, best_score