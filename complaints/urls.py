from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('post-complaint/', views.post_complaint, name='post_complaint'),
    path('complaints/', views.complaint_list, name='complaint_list'),

    path('like/<int:complaint_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:complaint_id>/', views.add_comment, name='add_comment'),
    path('delete/<int:complaint_id>/', views.delete_complaint, name='delete_complaint'),
    path('heatmap/', views.heatmap_view, name='heatmap'),
    path('set-language/<str:lang_code>/', views.set_language_view, name='set_language'),
]