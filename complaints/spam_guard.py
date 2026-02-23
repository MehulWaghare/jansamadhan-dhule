from django.utils import timezone
from datetime import timedelta
from .models import Complaint, Comment

# ================= SETTINGS =================

COMPLAINT_LIMIT_PER_HOUR = 3
COMMENT_LIMIT_PER_HOUR = 10
DUPLICATE_COOLDOWN_MINUTES = 10

BAD_WORDS = [
    "stupid",
    "idiot",
    "nonsense",
    "abuse",
    "badword"
]


# ================= BAD WORD CHECK =================
def contains_bad_words(text: str) -> bool:
    if not text:
        return False

    text_lower = text.lower()
    return any(word in text_lower for word in BAD_WORDS)


# ================= COMPLAINT RATE LIMIT =================
def is_complaint_rate_limited(user) -> bool:
    one_hour_ago = timezone.now() - timedelta(hours=1)

    count = Complaint.objects.filter(
        user=user,
        created_at__gte=one_hour_ago
    ).count()

    return count >= COMPLAINT_LIMIT_PER_HOUR


# ================= COMMENT RATE LIMIT =================
def is_comment_rate_limited(user) -> bool:
    one_hour_ago = timezone.now() - timedelta(hours=1)

    count = Comment.objects.filter(
        user=user,
        created_at__gte=one_hour_ago
    ).count()

    return count >= COMMENT_LIMIT_PER_HOUR


# ================= DUPLICATE COOLDOWN =================
def is_duplicate_cooldown(user, text) -> bool:
    """
    Prevent same user posting very similar complaint quickly
    """
    if not text:
        return False

    cooldown_time = timezone.now() - timedelta(minutes=DUPLICATE_COOLDOWN_MINUTES)

    recent = Complaint.objects.filter(
        user=user,
        created_at__gte=cooldown_time
    )

    text_lower = text.lower()

    for comp in recent:
        if comp.description and text_lower in comp.description.lower():
            return True

    return False