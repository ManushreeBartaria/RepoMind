FROM python:3.10-slim AS builder
WORKDIR /mind
COPY requirements.txt .
RUN pip install --no-cache-dir -r Backend.requirements.txt

FROM python:3.10-slim 
WORKDIR /mind
COPY --from=builder usr/local usr/local
COPY . .
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
