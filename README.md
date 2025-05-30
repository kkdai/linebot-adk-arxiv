# LINE Bot with Google ADK (Agent SDK), Google Gemini, and ArXiv Integration

## Project Background

This project is a LINE bot that uses Google ADK (Agent SDK) and Google Gemini models to interact with the arXiv repository. The bot can search for academic papers, summarize them by providing their abstracts, and answer questions based on those abstracts. It supports both Google Gemini API and Google VertexAI for model hosting.

## Screenshot

![image](https://github.com/user-attachments/assets/2bcbd827-0047-4a3a-8645-f8075d996c10)
*(Note: The screenshot might not reflect the current ArXiv agent functionality.)*

## Features

- Text message processing using AI models (Google ADK with Google Gemini).
- Specialized ArXiv agent for:
  - Searching for papers on arXiv based on user queries.
  - Summarizing specific arXiv papers (providing their abstracts).
  - Answering questions about specific arXiv papers based on their abstracts.
- Support for function calling with custom tools for the ArXiv agent.
- Integration with LINE Messaging API.
- Built with FastAPI for high-performance async processing.
- Containerized with Docker for easy deployment.

## Technologies Used

- Python 3.9+
- FastAPI
- LINE Messaging API
- Google ADK (Agent SDK)
- Google Gemini API
- Google VertexAI (optional alternative to Gemini API)
- `arxiv` (for interacting with arXiv API)
- Docker
- Google Cloud Run (for deployment)

## Setup

1. Clone the repository to your local machine.
2. Set the following environment variables:
   - `ChannelSecret`: Your LINE channel secret
   - `ChannelAccessToken`: Your LINE channel access token
   - For Google Gemini API:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
   - For VertexAI (alternative to Gemini API):
     - `GOOGLE_GENAI_USE_VERTEXAI`: Set to "True" to use VertexAI
     - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID
     - `GOOGLE_CLOUD_LOCATION`: Your Google Cloud region (e.g., "us-central1")

3. Install the required dependencies (ensure `arxiv` is included in your `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. Set up your LINE bot webhook URL to point to your server's endpoint.

## Usage

Send text messages to the LINE bot to interact with the ArXiv agent. Examples:

- To search for papers: "Find papers on quantum computing"
- To summarize a paper: "Summarize arXiv 2303.10130" or "Summarize <https://arxiv.org/abs/2303.10130>"
- To ask a question about a paper: "What are the main findings of paper 2303.10130 regarding its methodology?"

The bot will use its tools to fetch information from arXiv and respond.

## Available Tools & Agents

The bot utilizes a single, specialized agent:

**ArXiv Agent (named `arxiv_agent` in the code):**

- **Description:** An AI assistant specializing in interacting with the arXiv repository. It can search for papers, summarize specific papers by providing their abstracts, and answer questions about papers based on their abstracts.
- **Model:** `gemini-2.0-flash` (as specified in `main.py`)
- **Tools:**
  - `search_arxiv_papers(query: str)`: Searches arXiv for papers based on a query. Returns a list of papers including their title, authors, publication date, summary (abstract), arXiv ID, primary category, and PDF link.
  - `summarize_arxiv_paper(arxiv_id_or_url: str)`: Fetches and returns the details (including title, authors, abstract) of a specific arXiv paper identified by its ID or URL. The summary provided is the paper's abstract.
  - `answer_paper_question(arxiv_id_or_url: str, question: str)`: Attempts to answer a specific question about an arXiv paper by analyzing its abstract.

## Deployment Options

### Local Development

Use ngrok or similar tools to expose your local server to the internet for webhook access:

```bash
ngrok http 8000
```

### Docker Deployment

You can use the included Dockerfile to build and deploy the application:

```bash
docker build -t linebot-adk-arxiv .
# For Gemini API:
docker run -p 8000:8000 \
  -e ChannelSecret=YOUR_SECRET \
  -e ChannelAccessToken=YOUR_TOKEN \
  -e GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY \
  linebot-adk-arxiv

# For VertexAI:
docker run -p 8000:8000 \
  -e ChannelSecret=YOUR_SECRET \
  -e ChannelAccessToken=YOUR_TOKEN \
  -e GOOGLE_GENAI_USE_VERTEXAI=True \
  -e GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT \
  -e GOOGLE_CLOUD_LOCATION=YOUR_GCP_REGION \
  linebot-adk-arxiv
```

### Google Cloud Deployment

#### Prerequisites

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Create a Google Cloud project and enable the following APIs:
   - Cloud Run API
   - Container Registry API or Artifact Registry API
   - Cloud Build API

#### Steps for Deployment

1. Authenticate with Google Cloud:

   ```bash
   gcloud auth login
   ```

2. Set your Google Cloud project:

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

3. Build and push the Docker image to Google Container Registry (or Artifact Registry):

   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/linebot-adk-arxiv
   ```

4. Deploy to Cloud Run:

   For Gemini API:

   ```bash
   gcloud run deploy linebot-adk-arxiv \
     --image gcr.io/YOUR_PROJECT_ID/linebot-adk-arxiv \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars ChannelSecret=YOUR_SECRET,ChannelAccessToken=YOUR_TOKEN,GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
   ```

   For VertexAI (recommended for production):

   ```bash
   gcloud run deploy linebot-adk-arxiv \
     --image gcr.io/YOUR_PROJECT_ID/linebot-adk-arxiv \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars ChannelSecret=YOUR_SECRET,ChannelAccessToken=YOUR_TOKEN,GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT,GOOGLE_CLOUD_LOCATION=YOUR_GCP_REGION
   ```

5. Get the service URL:

   ```bash
   gcloud run services describe linebot-adk-arxiv --platform managed --region asia-east1 --format 'value(status.url)'
   ```

6. Set the service URL as your LINE Bot webhook URL in the LINE Developer Console.

#### Setting Up Secrets in Google Cloud (Recommended)

For better security, store your API keys as secrets:

1. Create secrets for your sensitive values:

   ```bash
   echo -n "YOUR_SECRET" | gcloud secrets create line-channel-secret --data-file=-
   echo -n "YOUR_TOKEN" | gcloud secrets create line-channel-token --data-file=-
   
   # For Gemini API
   echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create google-api-key --data-file=-
   
   # For VertexAI (store configuration as secrets if needed)
   # echo -n "True" | gcloud secrets create google-genai-use-vertexai --data-file=- # Only if you want to store this boolean as secret
   # echo -n "YOUR_GCP_PROJECT" | gcloud secrets create google-cloud-project --data-file=- # Only if you want to store this as secret
   # echo -n "YOUR_GCP_REGION" | gcloud secrets create google-cloud-location --data-file=- # Only if you want to store this as secret
   ```

2. Give the Cloud Run service access to these secrets:

   ```bash
   gcloud secrets add-iam-policy-binding line-channel-secret --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   gcloud secrets add-iam-policy-binding line-channel-token --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   
   # For Gemini API
   gcloud secrets add-iam-policy-binding google-api-key --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   
   # For VertexAI (if storing configurations as secrets)
   # gcloud secrets add-iam-policy-binding google-genai-use-vertexai --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   # gcloud secrets add-iam-policy-binding google-cloud-project --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   # gcloud secrets add-iam-policy-binding google-cloud-location --member=serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com --role=roles/secretmanager.secretAccessor
   ```

3. Deploy with secrets:

   For Gemini API:

   ```bash
   gcloud run deploy linebot-adk-arxiv \
     --image gcr.io/YOUR_PROJECT_ID/linebot-adk-arxiv \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --update-secrets=ChannelSecret=line-channel-secret:latest,ChannelAccessToken=line-channel-token:latest,GOOGLE_API_KEY=google-api-key:latest
   ```

   For VertexAI (if `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` are passed as env vars and not secrets):

   ```bash
   gcloud run deploy linebot-adk-arxiv \
     --image gcr.io/YOUR_PROJECT_ID/linebot-adk-arxiv \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --update-secrets=ChannelSecret=line-channel-secret:latest,ChannelAccessToken=line-channel-token:latest \
     --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT,GOOGLE_CLOUD_LOCATION=YOUR_GCP_REGION
   ```

   (Adjust the `--update-secrets` and `--set-env-vars` flags based on which configurations you\'ve stored as secrets vs. passed directly).

## Maintenance and Monitoring

After deployment, you can monitor your service through the Google Cloud Console:

1. View logs:

   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=linebot-adk-arxiv"
   ```

2. Check service metrics: Access the Cloud Run dashboard in Google Cloud Console

3. Set up alerts for error rates or high latency in Cloud Monitoring
