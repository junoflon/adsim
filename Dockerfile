FROM python:3.11

# Install Node.js 18
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything
COPY MiroFish/ .

# Install frontend deps and build static files
RUN cd frontend && npm ci && npm run build

# Install backend deps
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Flask will serve both API and static frontend
ENV PORT=5001
ENV FLASK_PORT=5001
EXPOSE 5001

CMD ["python", "backend/run.py"]
