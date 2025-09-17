from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_document, name="upload_document"),
    path("success/", views.upload_success, name="upload_success"),
    path("search/", views.search_documents, name="search_documents"),
]
