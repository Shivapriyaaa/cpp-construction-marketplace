FROM public.ecr.aws/lambda/python:3.9

# Set NLTK data path environment variable
ENV NLTK_DATA=/tmp/nltk_data

# Copy requirements first for better caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data to /tmp during build (optional, but helps with cold start)
RUN python -c "import nltk; nltk.download('punkt', download_dir='/tmp/nltk_data'); nltk.download('averaged_perceptron_tagger', download_dir='/tmp/nltk_data'); nltk.download('wordnet', download_dir='/tmp/nltk_data')"

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy function code and templates
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY templates/ ${LAMBDA_TASK_ROOT}/templates/

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ]