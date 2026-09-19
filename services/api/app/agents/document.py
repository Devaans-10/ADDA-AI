"""Bounded, process-local document evidence retrieval; no model or embeddings.

Documents expire after one hour and disappear on restart. A separate bearer token
is required for every lookup; possession of a document id alone grants no access.
"""
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
import math
import re
import secrets
import threading
import time

from pypdf import PdfReader

from app.providers import ProviderError

MAX_BYTES = 5 * 1024 * 1024
MAX_PAGES = 30
MAX_CHARACTERS = 200_000
MAX_CHUNKS = 300
STOPWORDS = set('a an and are as at be by can could did do does for from give how i in is it me of on or please tell that the their this to was were what when where which who why with would you your document pdf file uploaded according about'.split())


def _terms(text: str) -> Counter:
    return Counter(word for word in re.findall(r'\w+', text.lower())
                   if len(word) > 1 and word not in STOPWORDS)


@dataclass(frozen=True)
class _Document:
    token: str
    filename: str
    pages: int
    chunks: tuple[tuple[int, str], ...]
    expires: float


class DocumentStore:
    def __init__(self, ttl_seconds: int = 3600, max_documents: int = 10):
        self.ttl_seconds = ttl_seconds
        self.max_documents = max_documents
        self._documents: dict[str, _Document] = {}
        self._lock = threading.Lock()

    def _purge(self) -> None:
        now = time.monotonic()
        for key in list(self._documents):
            if self._documents[key].expires <= now:
                del self._documents[key]

    def ingest(self, data: bytes, filename: str) -> dict:
        if not data or len(data) > MAX_BYTES:
            raise ProviderError('Upload a nonempty file no larger than 5 MB.', 'document_size', 413)
        # The filename is display metadata only, never a filesystem path.
        filename = re.split(r'[/\\]', filename)[-1]
        filename = ''.join(c for c in filename if c.isprintable())[:180]
        extension = filename.rsplit('.', 1)[-1].lower()
        if extension not in ('pdf', 'txt'):
            raise ProviderError('Only PDF and UTF-8 TXT files are supported.', 'document_type', 415)
        if extension == 'txt':
            try:
                pages = [data.decode('utf-8-sig')]
            except UnicodeDecodeError as exc:
                raise ProviderError('Save this text file as UTF-8 and retry.', 'document_encoding', 422) from exc
            if '\x00' in pages[0]:
                raise ProviderError('This is not a supported text file.', 'document_encoding', 422)
        else:
            if not data.startswith(b'%PDF-'):
                raise ProviderError('The file is not a valid PDF.', 'document_invalid', 422)
            try:
                reader = PdfReader(BytesIO(data))
                if reader.is_encrypted:
                    raise ProviderError('Upload an unencrypted PDF.', 'document_encrypted', 422)
                if len(reader.pages) > MAX_PAGES:
                    raise ProviderError('Upload a PDF with at most 30 pages.', 'document_pages', 413)
                pages = []
                total = 0
                for page in reader.pages:
                    text = page.extract_text() or ''
                    total += len(text)
                    if total > MAX_CHARACTERS:
                        raise ProviderError('Document text is too large. Upload a shorter excerpt.', 'document_text_size', 413)
                    pages.append(text)
            except ProviderError:
                raise
            except Exception as exc:
                raise ProviderError('This PDF could not be read. Export a fresh text-based PDF.', 'document_invalid', 422) from exc
        if sum(map(len, pages)) > MAX_CHARACTERS:
            raise ProviderError('Document text is too large. Upload a shorter excerpt.', 'document_text_size', 413)
        chunks: list[tuple[int, str]] = []
        for number, page in enumerate(pages, 1):
            text = re.sub(r'\s+', ' ', page).strip()
            # Keep chunks page-local so every citation has an honest page number.
            while text:
                end = min(len(text), 1000)
                if end < len(text):
                    boundary = text.rfind(' ', 500, end)
                    if boundary > 0:
                        end = boundary
                chunks.append((number, text[:end]))
                text = text[end:].strip()
        if not chunks:
            raise ProviderError('No readable text found. Scanned PDFs need OCR, which is not available in this MVP.', 'document_no_text', 422)
        if len(chunks) > MAX_CHUNKS:
            raise ProviderError('Document has too many passages. Upload a shorter excerpt.', 'document_text_size', 413)
        with self._lock:
            self._purge()
            if len(self._documents) >= self.max_documents:
                raise ProviderError('Document storage is full. Remove a document or try after existing uploads expire.', 'document_capacity', 503)
            document_id, token = secrets.token_urlsafe(18), secrets.token_urlsafe(32)
            self._documents[document_id] = _Document(token, filename, len(pages), tuple(chunks), time.monotonic() + self.ttl_seconds)
        return {'document_id': document_id, 'document_token': token, 'filename': filename,
                'pages': len(pages), 'chunks': len(chunks)}

    def _get(self, document_id: str, token: str) -> _Document:
        self._purge()
        document = self._documents.get(document_id)
        expected = document.token if document else 'missing-document-token'
        valid = secrets.compare_digest(expected.encode(), (token or '').encode())
        if not document or not valid:
            raise ProviderError('Document unavailable or expired. Upload it again.', 'document_not_found', 404)
        return document

    def delete(self, document_id: str, document_token: str) -> None:
        with self._lock:
            self._get(document_id, document_token)
            del self._documents[document_id]

    def answer(self, document_id: str, document_token: str, query: str) -> dict:
        with self._lock:
            document = self._get(document_id, document_token)
        query_terms = _terms(query)
        summary = bool(re.search(r'\b(summar(?:y|ize|ise)|overview|main findings|key points)\b', query.lower()))
        counters = [_terms(text) for _, text in document.chunks]
        frequencies = Counter(word for counts in counters for word in counts)
        ranked = []
        for index, counts in enumerate(counters):
            score = sum((1 + math.log(counts[word])) *
                        (1 + math.log((len(counters) + 1) / (1 + frequencies[word])))
                        for word in query_terms if counts[word])
            if score:
                ranked.append((score, index))
        indices = [i for _, i in sorted(ranked, key=lambda item: (-item[0], item[1]))[:3]]
        if summary:
            # Representative excerpts, not a generated abstract or completeness claim.
            indices = []
            seen = set()
            for i, (page, _) in enumerate(document.chunks):
                if page not in seen:
                    indices.append(i)
                    seen.add(page)
                if len(indices) == 3:
                    break
        if not indices:
            return {'answer': 'Insufficient evidence: no matching passages were found in this document. Try the exact terms used in the text. This local retrieval uses keyword matching; it does not infer an answer.',
                    'citations': [], 'source_count': 0}
        citations = []
        blocks = ['**Document evidence — local keyword retrieval, no language model.**',
                  'Representative page excerpts (not a generated summary):' if summary else 'These matching excerpts may help answer your question; they are not a synthesized answer:']
        for number, index in enumerate(indices, 1):
            page, excerpt = document.chunks[index]
            cite_id = f'D{number}'
            citations.append({'id': cite_id, 'title': document.filename, 'page': page,
                              'document_id': document_id, 'excerpt': excerpt})
            # Escape markdown punctuation in untrusted source text before rendering.
            safe_excerpt = re.sub(r'([\\`*_{}\[\]()<>#+.!|~-])', r'\\\1', excerpt)
            blocks.append(f'> {safe_excerpt}\n\n[{cite_id}] — Page {page}')
        return {'answer': '\n\n'.join(blocks), 'citations': citations, 'source_count': len(citations)}
