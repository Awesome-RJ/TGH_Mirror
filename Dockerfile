FROM 5hojib/aeon:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN python3 -m venv uv
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "start.sh"]
