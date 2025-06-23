FROM python:3.9-slim-buster
RUN pip install fastapi==0.95.2 Jinja2==3.1.2 pydantic==1.10.8 uvicorn==0.22.0 tinydb==4.7.1 
RUN pip install passlib==1.7.4 python-dotenv==1.0.0 python-multipart==0.0.5 redis==6.2.0 requests==2.32.4
RUN pip install bcrypt==4.0.1 paho-mqtt==1.6.1 python-jose==3.3.0 email-validator==1.1.3 
RUN mkdir /app
RUN mkdir /app/data
COPY api.py /app/api.py
COPY environments   /app/environments
COPY html       /app/html
COPY models     /app/models
COPY routes     /app/routes
COPY dynsec     /app/dynsec
COPY secutils   /app/secutils
WORKDIR /app
CMD ["/usr/local/bin/python", "/app/api.py"]
