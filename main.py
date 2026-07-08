from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):
    text = req.text

    vendor = ""

    vendor_patterns = [
        r"Vendor[:\s]+(.+)",
        r"Supplier[:\s]+(.+)",
        r"Bill From[:\s]+(.+)",
    ]

    for pattern in vendor_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    amount = 0.0
    amt = re.search(r"(?:Total(?: Due)?|Amount Due|Grand Total)[:\s\$€£]*([0-9]+(?:\.[0-9]{1,2})?)", text, re.I)
    if amt:
        amount = float(amt.group(1))

    currency = "USD"
    cur = re.search(r"\b(USD|EUR|GBP)\b", text)
    if cur:
        currency = cur.group(1)

    date = ""
    d = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if d:
        date = d.group(1)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )