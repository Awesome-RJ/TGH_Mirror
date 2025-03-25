FROM 5hojib/aeon:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Create and activate the virtual environment
RUN python3 -m venv tgh-env
RUN tgh-env/bin/activate

# Install dependencies
COPY requirements.txt .
RUN tgh-env/bin/activate && pip install --no-cache-dir -r requirements.txt

COPY . .

# Update the start.sh to activate the virtual environment
RUN echo "source /usr/src/app/tgh-env/bin/activate" > /usr/src/app/start.sh

CMD ["bash", "start.sh"]
