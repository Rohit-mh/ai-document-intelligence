---
name: google-gemini-python
description: Use this skill whenever the user wants to write Python code for calling Google Gemini models on Vertex AI. It covers text generation, JSON extraction, image inputs, and document workflows, including direct file uploads using the File API. It helps you use the correct `google-genai` SDK and guides you on the right way to pass images and documents. Make sure to use this skill whenever the user mentions Google Gemini, Vertex AI, genai client, Gemini Python, Gemini image analysis, Gemini PDF processing, Gemini audio, or any Python code that needs to call a Gemini model hosted on Vertex AI, even if they don't explicitly say "Gemini" or "Vertex AI".
---

# Google Gemini Python API Skill

This skill provides complete documentation and best practices for using the Google Gemini models on Vertex AI with Python.
All reference material is included inline below — no external reference files are needed.

## Key Differences from Other SDKs

1. **Client Initialization**: You MUST use `genai.Client(vertexai=True, ...)` from the `google-genai` package, not the older `vertexai` SDK.
2. **Environment Setup**: Requires `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, and `GOOGLE_APPLICATION_CREDENTIALS`.
3. **Structured Output**: Uses `GenerateContentConfig(response_mime_type="application/json")` to force JSON.

## Common Workflows Covered

- Basic Text Generation
- System Instruction & Structured JSON Output
- Generic Function for JSON Extraction
- Sending Images to Gemini (Direct Bytes and File API)
- Comparing Two Images
- Sending Documents (Pattern A: OCR/Text Extraction first, Pattern B: Direct file upload via File API)
- Token Usage Reading
- Production-Ready Wrapper Class
- Error Handling
- Utility Functions for File Handling

## When to use which Document/Media Pattern

- **Pattern A (OCR/Text first)**: Best for TXT, DOCX, machine-readable PDFs, OCR-derived text, structured extraction pipelines (invoices, forms).
- **Pattern B (Direct File Upload)**: Best for media files (audio, images), simpler integrations without manual byte loading, workflows reusing uploaded file objects.

---

# Complete Google Gemini on Vertex AI Python Reference

This documentation is based on the current Google Gen AI SDK pattern for using Gemini models on Vertex AI.

It assumes the following are already present:

* A valid Vertex AI service account JSON key file exists locally.
* The following variables are present in `.env`:

  * `GOOGLE_CLOUD_PROJECT`
  * `GOOGLE_CLOUD_LOCATION`
  * `GOOGLE_APPLICATION_CREDENTIALS`
  * `GOOGLE_GENAI_USE_VERTEXAI=True`

This guide is specifically aligned to the calling pattern that initializes `genai.Client(vertexai=True, project=..., location=..., credentials=...)` and calls Gemini through `client.models.generate_content(...)`.

---

## 1. Objective

This guide explains how to call Google Gemini models on Vertex AI with Python for:

1. normal text generation
2. structured JSON output
3. image input
4. PDF, TXT, DOCX, and document workflows
5. comparing two files or images
6. production-ready reusable helper functions

A very important point for document and media handling is that there are **two valid ways** to work with files in Gemini workflows:

1. **Extract text / OCR first, then send the raw text** to Gemini
2. **Directly upload files** using the **File API** and pass those uploaded files to the model

Both approaches are documented below.

---

## 2. Correct SDK to Use

Use the Google Gen AI SDK (`google-genai`) for Gemini on Vertex AI.

Install the required packages:

```bash
pip install --upgrade google-genai python-dotenv google-auth
```

For document handling and local preprocessing, you may also need:

```bash
pip install pypdf python-docx pillow pymupdf
```

---

## 3. Environment Variables

Example `.env` file:

```env
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
GOOGLE_GENAI_USE_VERTEXAI=True
```

### Meaning of each variable

* `GOOGLE_CLOUD_PROJECT`: your Google Cloud project ID
* `GOOGLE_CLOUD_LOCATION`: Vertex AI region, such as `us-central1`
* `GOOGLE_APPLICATION_CREDENTIALS`: local path to the service-account JSON key file
* `GOOGLE_GENAI_USE_VERTEXAI=True`: indicates the SDK should be used against Vertex AI instead of the Gemini Developer API

---

## 4. Correct Client Initialization

The correct client initialization style for Gemini on Vertex AI in Python uses:

* `from google import genai`
* `from google.genai import types`
* `genai.Client(vertexai=True, project=..., location=..., credentials=...)`

### Recommended initialization with `.env`

```python
import os
from dotenv import load_dotenv
from google import genai
from google.oauth2 import service_account

load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_APPLICATION_CREDENTIALS,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = genai.Client(
    vertexai=True,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    credentials=credentials,
)
```

---

## 5. Reusable Initialization Helper

```python
import os
from dotenv import load_dotenv
from google import genai
from google.oauth2 import service_account

load_dotenv()


def get_gemini_vertex_client():
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    missing = []
    if not project:
        missing.append("GOOGLE_CLOUD_PROJECT")
    if not location:
        missing.append("GOOGLE_CLOUD_LOCATION")
    if not creds_path:
        missing.append("GOOGLE_APPLICATION_CREDENTIALS")

    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credential file not found: {creds_path}")

    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials,
    )
    return client
```

---

## 6. Choosing a Model

Example:

```python
MODEL_NAME = "gemini-2.5-pro"
```

Keep the model name separate from the client so you can swap models easily.

---

## 7. Basic Text Generation

This is the core pattern for normal text chat or prompt-response usage.

```python
import os
from dotenv import load_dotenv
from google import genai
from google.oauth2 import service_account

load_dotenv()

credentials = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    credentials=credentials,
)

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Explain Vertex AI and Gemini in simple words.",
)

print(response.text)
```

---

## 8. Reusable Function for Text Calls

```python
from google.genai import types


def ask_gemini(prompt: str, model: str = "gemini-2.5-pro") -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=500,
        ),
    )
    return response.text


answer = ask_gemini("What are the benefits of using Gemini on Vertex AI?")
print(answer)
```

---

## 9. System Instruction + User Prompt

Use `system_instruction` inside `GenerateContentConfig` to supply system-level behavior.

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Extract the key details from this receipt.",
    config=types.GenerateContentConfig(
        system_instruction="You are an expert financial document extraction assistant.",
        temperature=0,
        max_output_tokens=800,
    )
)

print(response.text)
```

---

## 10. Structured JSON Output

Use the following pattern for structured extraction with Gemini on Vertex AI:

* `response_mime_type="application/json"`
* `temperature=0`
* `json.loads(response.text)`

```python
import json
from google.genai import types

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Invoice No: INV-1001, Vendor: ABC Pvt Ltd, Amount: 5400, Date: 2026-03-12",
    config=types.GenerateContentConfig(
        system_instruction="Extract invoice details and return only valid JSON.",
        response_mime_type="application/json",
        temperature=0,
    )
)

parsed = json.loads(response.text)
print(parsed)
```

---

## 11. Generic JSON Extraction Function

```python
import json
from google.genai import types


def extract_json(document_text: str, system_prompt: str, model: str = "gemini-2.5-pro") -> dict:
    response = client.models.generate_content(
        model=model,
        contents=document_text,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0,
        )
    )
    return json.loads(response.text)
```

---

## 12. Reading Token Usage

Read usage from `response.usage_metadata` for token counts when available.

```python
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Summarize this document.",
)

try:
    prompt_tokens = response.usage_metadata.prompt_token_count
    completion_tokens = response.usage_metadata.candidates_token_count
    total_tokens = response.usage_metadata.total_token_count
    print(prompt_tokens, completion_tokens, total_tokens)
except Exception:
    print("Usage metadata not available")
```

---

## 13. Sending Images to Gemini on Vertex AI

There are two practical approaches for image workflows with Gemini.

### Approach A: Send image bytes directly in the request

```python
from google.genai import types

with open("sample.png", "rb") as f:
    image_bytes = f.read()

image_part = types.Part.from_bytes(
    data=image_bytes,
    mime_type="image/png",
)

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=[
        types.Content(
            role="user",
            parts=[
                image_part,
                types.Part.from_text(text="Describe this image in detail."),
            ],
        )
    ],
    config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=500,
    )
)

print(response.text)
```

### Approach B: Upload images using the File API

```python
from google import genai

client = genai.Client()

my_file = client.files.upload(file="path/to/sample.jpg")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[my_file, "Caption this image."],
)

print(response.text)
```

This approach is useful when you want to upload the media first and then pass the uploaded file object directly to the model.

### Supported use cases

* receipt image understanding
* visual inspection
* screenshot analysis
* form reading
* comparing two document images
* ID or cheque image validation
* image captioning from uploaded image files

---

## 14. Comparing Two Images in One Request

Use two `Part.from_bytes(...)` inputs plus a text instruction, all sent in the same multimodal request.

```python
import json
from google.genai import types

with open("reference.png", "rb") as f:
    ref_bytes = f.read()

with open("query.png", "rb") as f:
    query_bytes = f.read()

ref_part = types.Part.from_bytes(data=ref_bytes, mime_type="image/png")
query_part = types.Part.from_bytes(data=query_bytes, mime_type="image/png")

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=[
        types.Content(
            role="user",
            parts=[
                ref_part,
                query_part,
                types.Part.from_text(
                    text=(
                        "Image 1 is the reference document. "
                        "Image 2 is the query document. "
                        "Compare both and return only JSON."
                    )
                ),
            ],
        )
    ],
    config=types.GenerateContentConfig(
        system_instruction="You are a document comparison expert.",
        response_mime_type="application/json",
        temperature=0,
    )
)

result = json.loads(response.text)
print(result)
```

---

## 15. Sending PDFs, TXT, DOCX, and Other Documents

For document workflows, there are **two practical approaches**.

### Pattern A: Extract the document text first, then send the extracted text

This architecture:

1. extract text from the file first
2. build a prompt using that content
3. send the extracted content to Gemini
4. optionally force JSON output

This is the safest pattern for:

* TXT
* DOCX
* machine-readable PDFs
* OCR-derived text
* structured extraction pipelines

### Pattern B: Directly upload files using the File API

In this method, you upload the file first and then pass the uploaded file object directly to the model.

This is especially useful for:

* media files such as audio and images
* direct file-to-model workflows
* simpler integrations where you do not want to manually load bytes or extract text first
* workflows where the uploaded file object is directly reused in generation calls

### Example: Uploading audio using the File API

```python
from google import genai

client = genai.Client()

myfile = client.files.upload(file="path/to/sample.mp3")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=["Describe this audio clip", myfile]
)

print(response.text)
```

### Example: Uploading images using the File API

```python
from google import genai

client = genai.Client()

my_file = client.files.upload(file="path/to/sample.jpg")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[my_file, "Caption this image."],
)

print(response.text)
```

### When to choose Pattern A vs Pattern B

Choose **Pattern A (OCR/text first)** when:

* you want exact control over extracted content
* you already use OCR pipelines
* you need normalization, cleanup, field mapping, or schema enforcement
* you are processing business documents such as invoices, receipts, tax proofs, forms, DOCX, TXT, or scanned PDFs

Choose **Pattern B (direct file upload)** when:

* you want a simpler file-to-model integration
* you are working with media such as image or audio files
* you want to upload once and pass the uploaded file object into generation calls
* you do not want to manually extract text or load bytes in the request

---

## 16. TXT Example

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    txt_content = f.read()

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=txt_content,
)

print(response.text)
```

---

## 17. DOCX Example

```python
from docx import Document


def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


doc_text = read_docx("sample.docx")

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=doc_text,
)

print(response.text)
```

---

## 18. PDF Example with `pypdf`

```python
from pypdf import PdfReader


def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


pdf_text = read_pdf_text("document.pdf")

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=pdf_text,
)

print(response.text)
```

---

## 19. Best Practice for Scanned PDFs, Receipts, and Forms

For scanned documents, forms, or bills, plain text extraction from PDF may be weak. The better production pattern is:

1. extract layout-aware markdown using OCR/document intelligence
2. pass the extracted content to Gemini
3. force JSON output for structured fields

That is a strong enterprise architecture for invoice extraction, tax proof validation, cheque processing, and form understanding.

### Recommended flow

* input PDF/image
* OCR or layout extraction
* cleaned text/markdown
* Gemini extraction with system prompt
* JSON response

### When direct file upload is better

Direct file upload is a strong option when:

* you want a simpler integration path
* you are working with media such as audio and image files
* you want to upload the file once and pass it directly into `generate_content(...)`
* you do not need a separate OCR normalization step

So the updated recommendation is:

* for **controlled enterprise extraction**, prefer **OCR/text first**
* for **direct media-to-model workflows**, use **file upload**

---

## 20. Example: OCR/Text Extraction + Gemini JSON Extraction

```python
import json
from google.genai import types


def extract_structured_data_from_document(document_content: str, system_prompt: str) -> dict:
    user_prompt = f"""Extract all key information from the following document content and return it as structured JSON.

Document Content:
{document_content}

Return ONLY valid JSON with the extracted information."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0,
        )
    )

    return json.loads(response.text)
```

This is the core pattern for invoice extraction, cheque validation, receipt parsing, and business-document field extraction.

---

## 21. Utility Functions for Local File Handling

```python
import io
from pypdf import PdfReader
from docx import Document
from PIL import Image
import fitz  # PyMuPDF


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_docx_file(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def read_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    content = []
    for page in reader.pages:
        content.append(page.extract_text() or "")
    return "\n".join(content)


def convert_pdf_first_page_to_png_bytes(path: str) -> bytes:
    pdf_doc = fitz.open(path)
    page = pdf_doc[0]
    pix = page.get_pixmap(dpi=200)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    pdf_doc.close()
    return buffer.getvalue()
```

---

## 22. Production-Ready Wrapper Class

```python
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.oauth2 import service_account

load_dotenv()


class GeminiVertexService:
    def __init__(self, model: str = "gemini-2.5-pro"):
        self.project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.model = model

        credentials = service_account.Credentials.from_service_account_file(
            self.creds_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        self.client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            credentials=credentials,
        )

    def generate_text(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2, max_output_tokens: int = 500) -> str:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_prompt,
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    def generate_json(self, prompt: str, system_prompt: str) -> dict:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0,
            ),
        )
        return json.loads(response.text)

    def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: str) -> str:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        image_part,
                        types.Part.from_text(text=prompt),
                    ],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=500,
            ),
        )
        return response.text

    def upload_and_analyze_file(self, file_path: str, prompt: str, model: str | None = None) -> str:
        uploaded_file = self.client.files.upload(file=file_path)
        response = self.client.models.generate_content(
            model=model or self.model,
            contents=[prompt, uploaded_file],
        )
        return response.text
```

---

## 23. Error Handling

```python
try:
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents="Hello",
    )
    print(response.text)
except Exception as e:
    print(f"Gemini Vertex AI call failed: {e}")
```

### Common causes of failure

* invalid or missing service-account JSON file
* wrong `GOOGLE_CLOUD_PROJECT`
* wrong `GOOGLE_CLOUD_LOCATION`
* insufficient Vertex AI permissions
* unsupported model or region
* malformed JSON response parsing
* sending too much document content in one call
* wrong MIME type for file/image parts

---

## 24. Recommended Design by Use Case

### A. Normal chatbot

Use:

* `client.models.generate_content(...)`
* plain `contents="..."`

### B. Structured document extraction

Use:

* OCR or text extraction first
* `response_mime_type="application/json"`
* `temperature=0`

### C. Image analysis

Use either:

* `types.Part.from_bytes(...)` for direct local bytes
* `client.files.upload(...)` for uploaded image workflows

### D. Document comparison

Use:

* multiple `Part` objects in one request
* a clear comparison prompt
* JSON output

### E. Large document workflows

Use:

* OCR/layout extraction first
* chunk long documents
* summarize or extract section by section

### F. Direct media/file workflows

Use:

* `client.files.upload(...)`
* pass uploaded file objects into `client.models.generate_content(...)`

---

## 25. Important Notes

1. For Vertex AI, use `genai.Client(vertexai=True, ...)`, not the Gemini Developer API key pattern.
2. `GOOGLE_APPLICATION_CREDENTIALS` should point to the JSON key file path.
3. For strict extraction, keep `temperature=0`.
4. For JSON output, use `response_mime_type="application/json"`.
5. For local images, use `types.Part.from_bytes(...)`.
6. There are now **two documented file approaches**:

   * extract text / OCR first, then send raw text
   * upload files directly using `client.files.upload(...)`
7. For scanned PDFs and receipts, OCR/layout extraction before Gemini is usually more reliable for controlled enterprise extraction.
8. For direct audio and image workflows, file upload is now an important documented pattern.

---

## 26. Final Recommended Base Template

```python
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.oauth2 import service_account

load_dotenv()

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
MODEL_NAME = "gemini-2.5-pro"

credentials = service_account.Credentials.from_service_account_file(
    GOOGLE_APPLICATION_CREDENTIALS,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = genai.Client(
    vertexai=True,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
    credentials=credentials,
)


def call_gemini_text(user_prompt: str, system_prompt: str | None = None) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            max_output_tokens=500,
        ),
    )
    return response.text


if __name__ == "__main__":
    answer = call_gemini_text("Explain how Gemini on Vertex AI works.")
    print(answer)
```

---

## 27. Reference Alignment

This documentation uses:

* `from google import genai`
* `from google.genai import types`
* `genai.Client(vertexai=True, project=..., location=..., credentials=...)`
* `client.models.generate_content(...)`
* `GenerateContentConfig(system_instruction=..., response_mime_type="application/json", temperature=0)`
* `types.Part.from_bytes(...)` for image/document comparison
* OCR/document-extraction-first architecture before Gemini-based structured extraction

It also includes the direct file approach using:

* `client.files.upload(...)`
* passing uploaded files directly into `client.models.generate_content(...)`
* uploaded image workflows
* uploaded audio workflows

This covers both:

1. **OCR / raw-text-first workflows**
2. **Direct file-upload-to-model workflows**
