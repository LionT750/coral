FROM dhi.io/alpine-base:3.23-alpine3.23-dev

WORKDIR /app

# Install python and build dependencies
RUN apk add --no-cache python3 py3-pip gcc musl-dev postgresql-dev graphviz graphviz-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
