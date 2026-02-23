import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Complaint

SIMILARITY_THRESHOLD = 0.6
DISTANCE_THRESHOLD_METERS = 500  # nearby radius


# ================= DISTANCE CALCULATOR =================
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns distance in meters between two lat/lon points
    """
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ================= SMART DUPLICATE DETECTOR =================
def find_similar_complaint(new_text, new_lat, new_lon):
    complaints = Complaint.objects.exclude(latitude=None).exclude(longitude=None)

    if complaints.count() == 0:
        return None, 0

    texts = [c.description for c in complaints]
    texts.append(new_text)

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    best_match = None
    best_score = 0

    for idx, complaint in enumerate(complaints):
        sim_score = similarity_scores[idx]

        if sim_score < SIMILARITY_THRESHOLD:
            continue

        # check distance
        distance = haversine_distance(
            new_lat, new_lon,
            complaint.latitude, complaint.longitude
        )

        if distance <= DISTANCE_THRESHOLD_METERS:
            if sim_score > best_score:
                best_match = complaint
                best_score = sim_score

    return best_match, float(best_score)