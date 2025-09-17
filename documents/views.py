from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import UploadedDocument
from .utils import search_faiss


def upload_document(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("upload_success")
    else:
        form = DocumentForm()
    return render(request, "upload.html", {"form": form})


def upload_success(request):
    return render(request, "success.html")


def search_documents(request):
    query = None
    results = []
    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            results = search_faiss(query, top_k=3)  # get top 3 results
    return render(request, "search.html", {"query": query, "results": results})
