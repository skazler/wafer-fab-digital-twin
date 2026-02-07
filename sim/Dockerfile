FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# use -u to force unbuffered output to see the logs in real-time
CMD ["python", "-u", "tool_sim.py"]
