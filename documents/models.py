from django.db import models
from .utils import extract_text_from_file, detect_and_translate, add_to_faiss


class UploadedDocument(models.Model):
    file = models.FileField(upload_to="documents/")
    text_original = models.TextField(blank=True, null=True)   # extracted text (original language)
    text_translated = models.TextField(blank=True, null=True) # translated to English (for embeddings)
    language = models.CharField(max_length=10, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)  # save file first so self.file.path is available

        if not self.text_original:
            file_path = self.file.path
            extracted = extract_text_from_file(file_path) or ""
            translated, lang = detect_and_translate(extracted or "")
            self.text_original = extracted
            self.text_translated = translated
            self.language = lang
            super().save(update_fields=["text_original", "text_translated", "language"])

        # Always (re)generate chunks so DB + FAISS are in sync
        self.generate_chunks()

    def generate_chunks(self, chunk_size=200, overlap=20):
        """
        Split text into chunks, save them in DB, and also add them to FAISS index.
        """
        # delete old chunks
        DocumentChunk.objects.filter(document=self).delete()

        text = (self.text_translated or self.text_original or "").strip()
        if not text:
            return 0

        words = text.split()
        i = 0
        idx = 0
        chunk_texts = []  # store all chunk texts for FAISS

        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:
                DocumentChunk.objects.create(
                    document=self,
                    text=chunk_text,
                    chunk_index=idx
                )
                chunk_texts.append(chunk_text)
                idx += 1
            i += chunk_size - overlap

        # Add all chunks to FAISS
        if chunk_texts:
            add_to_faiss(chunk_texts, self.id)

        return idx

    def __str__(self):
        return self.file.name or f"UploadedDocument {self.pk}"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        UploadedDocument, on_delete=models.CASCADE, related_name="chunks"
    )
    text = models.TextField()
    chunk_index = models.PositiveIntegerField()
    embedding = models.JSONField(blank=True, null=True)  # placeholder for later (optional)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("document", "chunk_index")
        ordering = ["document", "chunk_index"]

    def __str__(self):
        name = self.document.file.name if self.document and self.document.file else f"Doc {self.document_id}"
        return f"{name} - chunk {self.chunk_index}"
