FROM public.ecr.aws/lambda/python:3.11
COPY . /var/task
RUN python3.11 -m pip install -r requirements.txt
COPY . .    
CMD ["main.handler"]