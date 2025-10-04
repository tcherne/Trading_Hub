import requests
from bs4 import BeautifulSoup
import PyPDF2
import os
from urllib.parse import urljoin

# Base URL for bills with chamber action
BASE_URL = "https://www.congress.gov/bills-with-chamber-action/119th-congress/browse-by-date"

# Directory to save downloaded PDFs
OUTPUT_DIR = "bills_pdfs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_bill_links():
    """Scrape the Congress.gov page for links to bill pages."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links to bill pages (adjust selector based on page structure)
        bill_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/bill/119th-congress/' in href:
                full_url = urljoin(BASE_URL, href)
                bill_links.append(full_url)
        
        return list(set(bill_links))  # Remove duplicates
    except Exception as e:
        print(f"Error fetching bill links: {e}")
        return []

def get_pdf_link(bill_url):
    """Fetch the PDF link for a specific bill page."""
    try:
        response = requests.get(bill_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for PDF links (often under 'Text' tab or similar)
        pdf_link = None
        for link in soup.find_all('a', href=True):
            if link['href'].endswith('.pdf'):
                pdf_link = urljoin(bill_url, link['href'])
                break
        return pdf_link
    except Exception as e:
        print(f"Error fetching PDF link from {bill_url}: {e}")
        return None

def download_and_parse_pdf(pdf_url, bill_id):
    """Download a PDF and extract its text content."""
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # Save PDF
        pdf_path = os.path.join(OUTPUT_DIR, f"{bill_id}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        # Parse PDF
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        
        return text
    except Exception as e:
        print(f"Error processing PDF {pdf_url}: {e}")
        return None

def prepare_grok_queries(bill_text, bill_id):
    """Prepare queries for Grok based on bill text."""
    questions = [
        "Which public companies may benefit from this legislation?",
        "How much financial impact might this have for the identified companies?",
        "What is a 3-month forecast for these companies based on the legislation?"
    ]
    
    # Structure the query for Grok (placeholder for actual API call)
    queries = []
    for question in questions:
        query = {
            "bill_id": bill_id,
            "bill_text": bill_text[:1000],  # Limit text length for demo purposes
            "question": question
        }
        queries.append(query)
    
    return queries

def submit_to_grok(queries):
    """Placeholder function to submit queries to Grok API."""
    # Replace this with actual xAI API call (see https://x.ai/api for details)
    for query in queries:
        print(f"\nSubmitting to Grok:")
        print(f"Bill ID: {query['bill_id']}")
        print(f"Question: {query['question']}")
        print(f"Bill Text Preview: {query['bill_text'][:200]}...")
        print("--- Response from Grok (placeholder) ---")
        print("Grok response would be here. Implement API call to get actual response.")
        # Example API call structure (pseudo-code):
        # response = requests.post("https://api.x.ai/grok", json={
        #     "query": query['question'],
        #     "context": query['bill_text']
        # })
        # print(response.json())

def main():
    # Step 1: Get bill page links
    print("Fetching bill links...")
    bill_links = get_bill_links()
    print(f"Found {len(bill_links)} bill links.")
    
    # Step 2: Process each bill
    for i, bill_url in enumerate(bill_links[:5]):  # Limit to 5 bills for demo
        print(f"\nProcessing bill {i+1}/{len(bill_links)}: {bill_url}")
        
        # Step 3: Get PDF link
        pdf_url = get_pdf_link(bill_url)
        if not pdf_url:
            print(f"No PDF found for {bill_url}")
            continue
        
        # Step 4: Download and parse PDF
        bill_id = bill_url.split('/')[-1]  # Extract bill ID from URL
        bill_text = download_and_parse_pdf(pdf_url, bill_id)
        if not bill_text:
            print(f"Failed to parse PDF for {bill_id}")
            continue
        
        # Step 5: Prepare queries for Grok
        queries = prepare_grok_queries(bill_text, bill_id)
        
        # Step 6: Submit queries to Grok (placeholder)
        submit_to_grok(queries)

if __name__ == "__main__":
    main()