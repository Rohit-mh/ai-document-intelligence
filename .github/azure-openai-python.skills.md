---
name: azure-openai-python
description: Use this skill whenever the user wants to write Python code for calling Azure OpenAI API. It covers chat completions, JSON extraction, image inputs, and direct document uploads (Responses API). It helps you avoid mixing up the standard OpenAI client with the Azure OpenAI client and guides you on the right way to pass images and PDFs. Make sure to use this skill whenever the user mentions Azure OpenAI, AzureOpenAI client, Azure GPT, Azure chat completions, Azure image analysis, Azure PDF processing, or any Python code that needs to call an OpenAI model hosted on Azure, even if they don't explicitly say "Azure OpenAI".
---

# Azure OpenAI Python API Skill

This skill provides complete documentation and best practices for using the Azure OpenAI API with Python.
All reference material is included inline below — no external reference files are needed.

## Key Differences from Standard OpenAI

1. **Client Initialization**: You MUST use `AzureOpenAI` from the `openai` package, not the standard `OpenAI` client.
2. **Required Parameters**: You must pass `azure_endpoint`, `api_key`, and `api_version` to the client.
3. **Model Configuration**: Azure uses deployment names (`model=deployment_name`), rather than foundation model names.

## Common Workflows Covered

- Basic Text Chat
- Structured JSON Output
- Generic Function for JSON Extraction
- Sending Images to Azure OpenAI (URL and Base64)
- Comparing Two Images
- Sending Documents (Pattern A: OCR/Text Extraction first, Pattern B: Direct file input via Responses API)
- Production-Ready Wrapper Class
- Error Handling
- Utility Functions for File Handling

## When to use which Document Pattern

- **Pattern A (OCR/Text first)**: Best for TXT, DOCX, scanned PDFs after OCR, structured business extraction (invoices, forms).
- **Pattern B (Direct File Input)**: Best for native PDF understanding, multimodal reasoning, direct summarization without manual text extraction.

---

# Complete Azure OpenAI Python Reference

This documentation is based on the Azure-specific SDK usage pattern: `from openai import AzureOpenAI` with `azure_endpoint`, `api_key`, and `api_version`. It assumes the following variables are already present in your `.env` file:

* `AZURE_OPENAI_API_KEY`
* `AZURE_OPENAI_ENDPOINT`
* `AZURE_DEPLOYEMENT_NAME`
* `AZURE_MODEL_VERSION`

> Note: the variable is written as `AZURE_DEPLOYEMENT_NAME` here because that is what was requested. If your actual `.env` uses `AZURE_DEPLOYMENT_NAME`, keep the code and env variable names consistent.

---

## 1. Objective

This guide explains how to call Azure OpenAI from Python for:

1. normal text chat/completion
2. structured JSON output
3. image input
4. PDF and document handling
5. multi-document workflows
6. best practices for production use

A very important point for document handling is that there are **two valid ways** to send files to Azure OpenAI:

1. **OCR / text-extraction first, then send the raw text** to the model
2. **Directly send the file** to the model using the **Responses API**

Both approaches are documented below, and both are useful depending on the use case.

---

## 2. Installation

Install the required package:

```bash
pip install openai python-dotenv
```

If you also want to process Word, PDF, or images before sending content to the model, you may additionally need:

```bash
pip install pypdf python-docx pillow pymupdf
```

---

## 3. Environment Variables

Example `.env` file:

```env
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYEMENT_NAME=gpt-4o-mini
AZURE_MODEL_VERSION=2025-04-01-preview
```

### Meaning of each variable

* `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
* `AZURE_OPENAI_ENDPOINT`: Azure OpenAI resource endpoint
* `AZURE_DEPLOYEMENT_NAME`: model deployment name created in Azure
* `AZURE_MODEL_VERSION`: API version used while calling Azure OpenAI

In Azure OpenAI, the `model` parameter in SDK calls should usually be the **deployment name**, not the raw foundation model name.

---

## 4. Correct Azure OpenAI Client Initialization

This is the correct client initialization pattern:

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYEMENT_NAME = os.getenv("AZURE_DEPLOYEMENT_NAME")
AZURE_MODEL_VERSION = os.getenv("AZURE_MODEL_VERSION")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_MODEL_VERSION,
)
```

### Why this is the correct pattern

The correct Azure-specific SDK pattern uses:

* `AzureOpenAI(...)`
* `azure_endpoint=...`
* `api_key=...`
* `api_version=...`

---

## 5. Reusable Initialization Helper

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


def get_azure_openai_client() -> tuple[AzureOpenAI, str]:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_DEPLOYEMENT_NAME")
    api_version = os.getenv("AZURE_MODEL_VERSION")

    missing = []
    if not api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not deployment:
        missing.append("AZURE_DEPLOYEMENT_NAME")
    if not api_version:
        missing.append("AZURE_MODEL_VERSION")

    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )
    return client, deployment
```

---

## 6. Basic Text Chat Call

This is the most common Azure OpenAI function for normal chatbot-style usage.

```python
from dotenv import load_dotenv
from openai import AzureOpenAI
import os

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_MODEL_VERSION"),
)

deployment_name = os.getenv("AZURE_DEPLOYEMENT_NAME")

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Azure OpenAI in simple words."}
    ],
    temperature=0.2,
    max_tokens=300,
)

print(response.choices[0].message.content)
```

### Explanation

* `client.chat.completions.create(...)` calls the Azure chat completions endpoint.
* `model=deployment_name` should point to your Azure deployment.
* `messages` contains the conversation.
* `temperature` controls randomness.
* `max_tokens` controls the output length.

---

## 7. Reusable Function for Normal Chat

```python
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_MODEL_VERSION"),
)

deployment_name = os.getenv("AZURE_DEPLOYEMENT_NAME")


def ask_llm(user_prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content


answer = ask_llm("What are the advantages of Azure OpenAI?")
print(answer)
```

---

## 8. Structured JSON Output

Use `response_format={"type": "json_object"}` when structured output is needed.

```python
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_MODEL_VERSION"),
)

deployment_name = os.getenv("AZURE_DEPLOYEMENT_NAME")

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "system",
            "content": "Extract invoice details and return only valid JSON."
        },
        {
            "role": "user",
            "content": "Invoice No: INV-1001, Vendor: ABC Pvt Ltd, Amount: 5400, Date: 2026-03-12"
        }
    ],
    temperature=0,
    response_format={"type": "json_object"}
)

content = response.choices[0].message.content
parsed = json.loads(content)
print(parsed)
```

### When to use this

Use this when you need:

* OCR result extraction
* metadata extraction
* document parsing
* schema-like responses
* reliable machine-readable output

---

## 9. Generic Function for JSON Extraction

```python
import json


def extract_json_from_text(document_text: str, system_prompt: str) -> dict:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return json.loads(content)
```

---

## 10. Sending Images to Azure OpenAI

For image understanding, Azure OpenAI supports the **Responses API**. This is the preferred approach when you want to pass image content directly to the model.

### Approach A: Image URL input

Use this when your image is already hosted and you have a valid URL.

```python
response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what is in this image?" },
                {
                    "type": "input_image",
                    "image_url": "<image_URL>"
                }
            ]
        }
    ]
)

print(response)
```

### Approach B: Base64 encoded image input

Use this when the image is stored locally and you want to send it directly from Python.

```python
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
image_path = "path_to_your_image.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what is in this image?" },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]
)

print(response)
```

### When to use image input

* visual inspection
* screenshot analysis
* product or object understanding
* cheque comparison
* receipt and form image understanding
* multimodal extraction workflows

### Note on older chat-completions image style

Earlier code examples also show image handling through `client.chat.completions.create(...)` using `image_url` blocks inside `messages`. That style is still useful to understand when maintaining older code. However, for direct multimodal file/image inputs, the **Responses API** is the better way going forward.

## 11. Comparing Two Images in One Request

If you want to compare two images in one request, you can pass multiple image items in the same input content list.

### Example pattern

```python
import base64


def to_data_url(path: str, mime_type: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


ref_uri = to_data_url("reference.png", "image/png")
query_uri = to_data_url("query.png", "image/png")

response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Compare image 1 and image 2 and explain the differences."},
                {"type": "input_image", "image_url": ref_uri},
                {"type": "input_image", "image_url": query_uri}
            ]
        }
    ]
)

print(response)
```

This is useful for comparison, validation, and verification workflows.

## 12. Sending PDF, TXT, DOCX, and Other Documents

There are **two practical patterns** for sending documents to Azure OpenAI.

## Pattern A: Extract text first, then send text to Azure OpenAI

This pattern is for OCR-driven workflows:

1. extract content from the file using another library or service
2. build a prompt using extracted content
3. send the extracted content as text to Azure OpenAI

This is the most reliable approach for:

* TXT
* DOCX
* scanned PDF after OCR
* structured extraction workflows
* forms, invoices, and business documents where you want tighter control

### Example: TXT file

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    txt_content = f.read()

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "Summarize the document."},
        {"role": "user", "content": txt_content}
    ],
    temperature=0.2,
    max_tokens=500,
)

print(response.choices[0].message.content)
```

### Example: DOCX file

```python
from docx import Document


def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


doc_text = read_docx("sample.docx")

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "Summarize the Word document."},
        {"role": "user", "content": doc_text}
    ],
)

print(response.choices[0].message.content)
```

### Example: PDF text extraction with `pypdf`

```python
from pypdf import PdfReader


def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


pdf_text = read_pdf_text("document.pdf")

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "Summarize this PDF."},
        {"role": "user", "content": pdf_text}
    ],
    max_tokens=700,
)

print(response.choices[0].message.content)
```

## Pattern B: Directly send the file to Azure OpenAI

In this method, you pass the actual file directly to the model using the **Responses API**.

This is especially useful for:

* native PDF understanding
* direct multimodal workflows
* cases where you want the model to reason over the file itself
* workflows where you do not want to manually extract text first

### Example: Direct file input using Base64 PDF data

```python
import base64

with open("PDF-FILE-NAME.pdf", "rb") as f: # assumes PDF is in the same directory as the executing script
    data = f.read()

base64_string = base64.b64encode(data).decode("utf-8")

response = client.responses.create(
    model="gpt-4o-mini", # model deployment name
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "filename": "PDF-FILE-NAME.pdf",
                    "file_data": f"data:application/pdf;base64,{base64_string}",
                },
                {
                    "type": "input_text",
                    "text": "Summarize this PDF",
                },
            ],
        },
    ]
)

print(response.output_text)
```

### Example: Upload PDF first, then analyze it

You can also upload the PDF first and then use the returned file ID in later workflows.

```python
# Upload a file with a purpose of "assistants"
file = client.files.create(
  file=open("nucleus_sampling.pdf", "rb"), # This assumes a .pdf file in the same directory as the executing script
  purpose="assistants"
)

print(file.model_dump_json(indent=2))
file_id = file.id
```

After uploading, the `file_id` can be used in your downstream logic wherever file-based workflows are supported.

### When to choose Pattern A vs Pattern B

Choose **Pattern A (OCR/text first)** when:

* you want exact control over extracted content
* you already use OCR pipelines such as Azure Document Intelligence
* you need normalization, cleanup, field mapping, or schema enforcement
* you are processing DOCX, TXT, scanned forms, or mixed business documents

Choose **Pattern B (direct file input)** when:

* the API/model supports the file type directly
* you want simpler direct PDF analysis
* you want multimodal reasoning over the original file
* you do not want to manually extract text before sending

## 13. Best Practice for Scanned PDFs and Forms

For scanned documents, image-heavy PDFs, bills, receipts, and forms, the best approach still depends on your use case.

### Recommended approach for business extraction workflows

1. use OCR or document parsing first
2. send the extracted text/markdown to Azure OpenAI
3. ask for JSON or structured output

### Recommended flow

* PDF/image input
* OCR / layout extraction
* cleaned text or markdown
* Azure OpenAI extraction using system prompt
* JSON output

### When direct file input is better

Direct file input is a strong option when:

* you want quick summarization of a PDF
* you want a simpler integration path
* the model supports reasoning directly over the uploaded file
* you do not need a separate OCR normalization step

So the updated recommendation is:

* for **controlled enterprise extraction**, prefer **OCR/text first**
* for **simple direct summarization or native file reasoning**, use **direct file input**

## 14. Example: OCR + Azure OpenAI Extraction Pattern

```python
import json
from openai import AzureOpenAI


def extract_structured_data_from_document(document_content: str, system_prompt: str) -> dict:
    user_prompt = f"""Extract all key information from the following document content and return it as structured JSON.

Document Content:
{document_content}

Return ONLY valid JSON with the extracted information."""

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
```

This is the core pattern for invoice extraction, cheque validation, receipt parsing, and business-document field extraction.

---

## 15. Utility Functions for File Handling

```python
import os
import base64
from pypdf import PdfReader
from docx import Document


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


def file_to_base64_data_url(path: str, mime_type: str) -> str:
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
```

---

## 16. Production-Ready Wrapper Class

```python
import os
import json
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


class AzureOpenAIService:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_DEPLOYEMENT_NAME")
        self.api_version = os.getenv("AZURE_MODEL_VERSION")

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def chat(self, user_prompt: str, system_prompt: str = "You are a helpful assistant.", temperature: float = 0.2, max_tokens: int = 500) -> str:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def chat_json(self, user_prompt: str, system_prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def analyze_image(self, image_path: str, prompt: str, mime_type: str = "image/png"):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        data_url = f"data:{mime_type};base64,{b64}"

        response = self.client.responses.create(
            model=self.deployment,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": data_url
                        }
                    ]
                }
            ]
        )
        return response

    def analyze_pdf_direct(self, pdf_path: str, prompt: str) -> str:
        with open(pdf_path, "rb") as f:
            data = f.read()

        base64_string = base64.b64encode(data).decode("utf-8")

        response = self.client.responses.create(
            model=self.deployment,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": os.path.basename(pdf_path),
                            "file_data": f"data:application/pdf;base64,{base64_string}",
                        },
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                    ],
                },
            ]
        )
        return response.output_text
```

## 17. Error Handling

Recommended error-safe wrapper:

```python
try:
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Azure OpenAI call failed: {e}")
```

### Common causes of failure

* wrong API key
* wrong endpoint
* wrong deployment name
* wrong API version
* unsupported model capability for image input
* too much document text in one request
* malformed JSON output request

---

## 18. Recommended Design by Use Case

## A. Normal chatbot

Use:

* `client.chat.completions.create(...)`
* text-only `messages`

## B. OCR extraction from bills, forms, and receipts

Use:

* OCR first
* pass extracted content into Azure OpenAI
* enforce `response_format={"type": "json_object"}`

## C. Image comparison or visual analysis

Use:

* `client.responses.create(...)`
* content list with `input_text` + one or more `input_image` blocks

## D. PDF / Word / TXT summarization

Use either:

* **Approach 1:** extract text first for controlled workflows
* **Approach 2:** direct file input through `client.responses.create(...)` when supported

## E. Enterprise document Q&A over many files

Use:

* retrieval pipeline / vector database / Azure AI Search / On Your Data style architecture
* do not dump very large files directly into one prompt

## F. Direct multimodal file workflows

Use:

* `client.responses.create(...)`
* `input_file`, `input_image`, and `input_text` blocks together when needed

## 19. Important Notes

1. In Azure OpenAI, the `model` field should usually be the **deployment name**.
2. The client class should be `AzureOpenAI`, not the generic `OpenAI` client, for the code style you are using.
3. For structured extraction, keep `temperature=0`.
4. For image input in the newer direct multimodal style, use `client.responses.create(...)` with `input_image`.
5. There are now **two documented document approaches**:

   * extract text / OCR first, then send raw text
   * directly send supported files through the Responses API
6. For PDF, direct file input is now a valid and important documented pattern.
7. For DOCX, TXT, scanned documents, and structured extraction pipelines, OCR/text-first is still often the safest and most controllable approach.
8. For very long files, split content into chunks before sending to the model.

## 20. Final Recommended Base Template

```python
import os
import json
import base64
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYEMENT_NAME = os.getenv("AZURE_DEPLOYEMENT_NAME")
AZURE_MODEL_VERSION = os.getenv("AZURE_MODEL_VERSION")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_MODEL_VERSION,
)


def call_azure_openai_chat(user_prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    response = client.chat.completions.create(
        model=AZURE_DEPLOYEMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content


def call_azure_openai_pdf_direct(pdf_path: str, prompt: str) -> str:
    with open(pdf_path, "rb") as f:
        data = f.read()

    base64_string = base64.b64encode(data).decode("utf-8")

    response = client.responses.create(
        model=AZURE_DEPLOYEMENT_NAME,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": os.path.basename(pdf_path),
                        "file_data": f"data:application/pdf;base64,{base64_string}",
                    },
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                ],
            },
        ]
    )
    return response.output_text


if __name__ == "__main__":
    answer = call_azure_openai_chat("Explain how Azure OpenAI works.")
    print(answer)
```

## 21. Reference Alignment

This documentation uses:

* `from openai import AzureOpenAI`
* `client = AzureOpenAI(azure_endpoint=..., api_key=..., api_version=...)`
* `client.chat.completions.create(...)`
* `response_format={"type": "json_object"}` for structured extraction
* OCR/document-extraction-first architecture before LLM extraction

It also includes the newer direct multimodal/file approach using:

* `client.responses.create(...)`
* `input_image` for images
* `input_file` for direct PDF/file submission
* `client.files.create(...)` for uploading files before downstream analysis

This covers both:

1. **OCR / raw-text-first workflows**
2. **Direct file-to-model workflows**
