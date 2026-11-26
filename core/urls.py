from django.contrib import admin
from django.urls import path
from api.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    DocumentListCreateView,
    DocumentDetailView,
    ProtectedDocumentFileView,
    CategoryListCreateView, 
    CategoryDetailView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/documents/', DocumentListCreateView.as_view(), name='documents'),
    path('api/documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('api/documents/<int:pk>/file/', ProtectedDocumentFileView.as_view(), name='document-file'),
    path('api/categories/', CategoryListCreateView.as_view(), name='categories'),
    path('api/categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]