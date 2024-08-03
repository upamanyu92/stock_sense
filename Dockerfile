FROM python:3.10-slim
RUN apt-get update && apt-get install -y \
    pkg-config \
    libhdf5-dev \
    build-essential \
    gcc

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
ENV FLASK_APP=linear_predict.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
