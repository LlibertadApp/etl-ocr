FROM public.ecr.aws/lambda/python:3.10-arm64
COPY . /var/task
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt
COPY . .    
CMD ["main.handler"]