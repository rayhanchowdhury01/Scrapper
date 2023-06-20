import fitz
from docx import Document

from urllib.request import urlopen

import requests
from io import BytesIO
from bs4 import BeautifulSoup


def read_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        pdf_content = response.content
        doc = fitz.open("pdf", pdf_content)
        text = ""
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            text += page.get_text()
        return text
    else:
        return ("Error: Unable to download the PDF.")


def read_docx_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            docx_content = response.content
            doc = Document(BytesIO(docx_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return "null"
    except:
        return "error"


def read_txt_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        txt_content = response.text
        print(txt_content)
    else:
        print("Error: Unable to download the TXT file.")


def read_html(url):
    try:
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except:
        return "error"


def is_pdf_url(url):
    try:
        response = requests.head(url)
        content_type = response.headers.get('content-type')
        if content_type is not None and 'application/pdf' in content_type.lower():
            return True
        return url.endswith('.pdf')
    except:
        return False


docx_url = "https://www.mtsac.edu/webdesign/accessible-docs/word/example03.docx"
pdf_url = "http://www.northsouth.edu/newassets/images/5-9451.PABX_Directory _3March2023.pdf"
txt_url = "https://filesamples.com/samples/document/txt/sample3.txt"
html_url = "http://www.northsouth.edu/"
from elasticsearch import Elasticsearch

# Create an Elasticsearch client
es = Elasticsearch(
    cloud_id="e61df9493b6d478ea6bb207b9ef9b91a:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ0ZjViMGM4N2MyMTE0NmE2OGEwNjlkZDIxYmZkYmY1MiRhOWM5MTcxNDU3MDE0YjRkODQzMjFkNGJkMjM5YWY1Zg==",
    basic_auth=("elastic", "0MHKMlWLJrHmYpptvYR7yk9e")
)

index_name = "my_index"

mapping = {
    "properties": {
        "url": {"type": "keyword"},
        "content": {"type": "text"},
    }
}


def index_documents(documents):
    for doc in documents:
        es.index(index=index_name, body=doc)


def create_index(es, documents_to_index):
    # Delete the index if it already exists
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

    # Create the index with mapping
    es.indices.create(index=index_name, body={"mappings": mapping})
    index_documents(documents_to_index)


# Example usage
documents_to_index = [
    {"url": "https://example.com/page1", "content": "This is the content of page 1."},
    {"url": "https://example.com/page2", "content": "Here is the content of page 2."},
    {"url": "www.stackovf.com",
     "content": "hello hge world rayhan bj is a very good man .. xd hello world this is chatgopt"},
    {"url": "https://example.com/page3", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."},
    {"url": "https://example.com/page4",
     "content": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."},
    {"url": "https://example.com/page5",
     "content": "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."},
    {"url": "https://example.com/page6",
     "content": "Duis nabeel irure dolor in reprehenderit in voluptate velit esse."},
    # Add more documents as needed
]

file_path = "urls.txt"
with open(file_path, "r") as file:
    lines = file.readlines()
urls_array = [line.strip() for line in lines]

# Print the URLs in the array
count = 0
s = 0
f = 0
for url in urls_array:
    count += 1
    try:
        text = ""
        if (is_pdf_url(url)):
            try:
                text = read_pdf_from_url(url)
                print('success =' + url)
                s += 1

            except:
                print('fail =' + url)
                f += 1
        else:
            try:
                text = read_html(url)
                print('success =' + url)
                s += 1
            except:

                try:
                    text = read_pdf_from_url(url)
                    print('success =' + url)
                    s += 1
                except:
                    print('fail =' + url)
                    f += 1
        documents_to_index.append({"url": url, "content": text})
    except:
        print('fail: ' + url)


def search_documents(query):
    body = {
        "query": {
            "match": {
                "content": query
            }
        },
        "highlight": {
            "fields": {
                "content": {}
            }
        }
    }
    result = es.search(index=index_name, body=body)
    return result


create_index(es, documents_to_index)


def ask():
    query = input('Enter word: ')
    search_results = search_documents(query)
    for hit in search_results["hits"]["hits"]:
        print("content", hit["_source"])
        print("---")
