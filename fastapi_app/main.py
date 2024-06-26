from fastapi import FastAPI, Request, Response
import json
import uvicorn
import nest_asyncio
import google.generativeai as genai
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.docstore.document import Document
from unstructured.cleaners.core import remove_punctuation, clean, clean_extra_whitespace
import logging
import re
import textwrap
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

nest_asyncio.apply()

logging.basicConfig(level=logging.DEBUG)

app = FastAPI(debug=True)

genai.configure(api_key="GOOGLE API KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

templates = Jinja2Templates(directory="templates")
jinja_env = Environment(loader=FileSystemLoader('templates'))

@app.get("/")
def read_root():
    return templates.TemplateResponse("input_form.html", {"request": {}})

@app.get("/generate_sales_pitch_and_email")
def generate_sales_pitch_and_email_form():
     return templates.TemplateResponse("input_form.html", {"request": {}})

@app.post("/generate_sales_pitch_and_email")
async def generate_sales_pitch_and_email_endpoint(request: Request):
     logging.debug("Received request for generate sales pitch and email endpoint")
     try:
        data = await request.form()
        url = data.get("url")
     except Exception as e:
       logging.error(f"Error parsing request body: {e}")
       url = ""

     if not url:
         return JSONResponse(content={"error": "Invalid request body"}, status_code=400)

     sales_pitch,email_content = generate_sales_pitch_and_email(url)

     logging.debug(f"Generated sales pitch : {sales_pitch}")
     logging.debug(f"Generated email content: {email_content}")

     return templates.TemplateResponse("output.html", {"request": request, "sales_pitch": sales_pitch, "email_content": email_content})

def generate_sales_pitch_and_email(url):
     logging.debug(f"Generating sales pitch and email for URL: {url}")
     try:
         loader = UnstructuredURLLoader(urls=[url], mode="elements", post_processors=[clean, remove_punctuation, clean_extra_whitespace])
         elements = loader.load()
         selected_elements = [e for e in elements if e.metadata['category'] == "NarrativeText"]
         full_clean = " ".join([e.page_content for e in selected_elements])
         document = Document(page_content=full_clean, metadata={"source": url})

         wrapped_text = textwrap.fill(document.page_content, width=80)
         prompt = (
            f"Generate an appealing, effective, clear, concise, and professional sales pitch and also generate an email content for lead generation according to provided URL: {url}. "
            f"Begin with the sales pitch before transitioning to the email content. Use a horizontal line to divide the sales pitch from the email message. Avoid using asterisks and pound signs."
        )

         response = model.generate_content(prompt)
         text_only_response = re.sub(r'<[^>]*>|[*]', '', response.text)
         text_only_response = text_only_response.replace('\n', '<br>')
         # Separate the sales pitch and email content
         parts = text_only_response.split('---')
         sales_pitch = parts[0].replace("Sales Pitch:", "").strip()
         email_content = parts[1].replace("Email Content:", "").strip() if len(parts) > 1 else ""

         logging.debug(f"Generated sales pitch: {sales_pitch}")
         logging.debug(f"Generated email content: {email_content}")
         return sales_pitch, email_content
         
     except Exception as e:
         logging.error(f"Error generating sales pitch and email: {e}")
         return "Error generating sales pitch and email"

if __name__ == "__main__":
     uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")
