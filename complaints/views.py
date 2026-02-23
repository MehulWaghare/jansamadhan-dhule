from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import F, ExpressionWrapper, IntegerField

from .forms import RegisterForm, LoginForm, ComplaintForm, CommentForm
from .models import Complaint, Like
from .utils import find_similar_complaint

from .spam_guard import (
    is_complaint_rate_limited,
    is_comment_rate_limited,
    contains_bad_words,
    is_duplicate_cooldown,
)


# ================= HOME =================
def home(request):
    return render(request, 'home.html')


# ================= REGISTER =================
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('home')


# ================= POST COMPLAINT (AI + SPAM GUARD) =================
@login_required
def post_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)

        if form.is_valid():
            new_description = form.cleaned_data.get('description')
            new_lat = form.cleaned_data.get('latitude')
            new_lon = form.cleaned_data.get('longitude')

            # 🚨 ================= SPAM PROTECTION =================

            # rate limit
            if is_complaint_rate_limited(request.user):
                messages.error(
                    request,
                    "🚫 You are posting complaints too frequently. Please try later."
                )
                return redirect('post_complaint')

            # bad language
            if contains_bad_words(new_description):
                messages.error(
                    request,
                    "🚫 Complaint contains inappropriate language."
                )
                return redirect('post_complaint')

            # duplicate cooldown (same user rapid repeat)
            if is_duplicate_cooldown(request.user, new_description):
                messages.warning(
                    request,
                    "⚠️ You recently posted a similar complaint. Please wait."
                )
                return redirect('post_complaint')

            # 🤖 ================= SMART DUPLICATE AI =================
            similar_complaint = None
            score = 0

            if new_description and new_lat is not None and new_lon is not None:
                similar_complaint, score = find_similar_complaint(
                    new_description,
                    new_lat,
                    new_lon
                )

            if similar_complaint:
                messages.warning(
                    request,
                    f"⚠️ Similar complaint already exists nearby (Similarity: {score:.2f})"
                )

            # ✅ save complaint
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()

            messages.success(request, "Complaint posted successfully!")
            return redirect('complaint_list')
    else:
        form = ComplaintForm()

    return render(request, 'post_complaint.html', {'form': form})


# ================= LIST WITH PRIORITY =================
def complaint_list(request):
    complaints = Complaint.objects.annotate(
        priority_score=ExpressionWrapper(
            (F('likes_count') * 3) +
            (F('comments_count') * 2),
            output_field=IntegerField()
        )
    ).order_by('-priority_score', '-created_at')

    return render(request, 'complaint_list.html', {'complaints': complaints})


# ================= LIKE =================
@login_required
def toggle_like(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        complaint=complaint
    )

    if not created:
        like.delete()
        complaint.likes_count = max(0, complaint.likes_count - 1)
    else:
        complaint.likes_count += 1

    complaint.save()

    return JsonResponse({'likes_count': complaint.likes_count})


# ================= COMMENT (WITH SPAM GUARD) =================
@login_required
def add_comment(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data.get('text')

            # 🚨 rate limit
            if is_comment_rate_limited(request.user):
                messages.error(
                    request,
                    "🚫 You are commenting too frequently."
                )
                return redirect('complaint_list')

            # 🚨 bad words
            if contains_bad_words(text):
                messages.error(
                    request,
                    "🚫 Comment contains inappropriate language."
                )
                return redirect('complaint_list')

            # ✅ save comment
            comment = form.save(commit=False)
            comment.user = request.user
            comment.complaint = complaint
            comment.save()

            complaint.comments_count += 1
            complaint.save()

    return redirect('complaint_list')


# ================= DELETE =================
@login_required
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.user != complaint.user and not request.user.is_superuser:
        return HttpResponseForbidden(
            "You are not allowed to delete this complaint."
        )

    complaint.delete()
    messages.success(request, "Complaint deleted successfully.")
    return redirect('complaint_list')


# ================= HEATMAP =================
def heatmap_view(request):
    complaints = Complaint.objects.exclude(
        latitude=None
    ).exclude(
        longitude=None
    )

    heat_data = [
        [c.latitude, c.longitude]
        for c in complaints
    ]

    return render(request, 'heatmap.html', {
        'heat_data': heat_data
    })

from django.utils import translation
from django.conf import settings


def set_language_view(request, lang_code):
    if lang_code in dict(settings.LANGUAGES):
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return redirect(request.META.get('HTTP_REFERER', 'home'))