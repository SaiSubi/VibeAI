# 🚀 VibeAI Google Cloud Run Deployment Guide

This guide will walk you through deploying your VibeAI backend to Google Cloud Run.

## 📋 Prerequisites

1. **Google Cloud Account** - Sign up at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud CLI** - Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Docker** - For local testing (optional)

## 🛠️ Setup Steps

### 1. Install and Authenticate Google Cloud CLI

```bash
# Install gcloud CLI (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login
```

### 2. Create a New Project

```bash
# Create a new project (replace with your desired project name)
gcloud projects create vibeai-backend-123

# Set the project as default
gcloud config set project vibeai-backend-123
```

### 3. Enable Billing

- Go to [Google Cloud Console](https://console.cloud.google.com)
- Select your project
- Navigate to Billing
- Link a billing account (required even for free tier)

### 4. Configure Environment Variables

Copy `env.example` to `.env` and fill in your actual values:

```bash
cp env.example .env
# Edit .env with your actual API keys and configuration
```

**Important:** Update `SPOTIFY_REDIRECT_URI` to point to your Cloud Run service URL once deployed.

## 🚀 Deployment Options

### Option 1: Quick Deploy Script

1. **Edit the deployment script:**
   ```bash
   # Edit deploy.sh and replace 'your-project-id' with your actual project ID
   nano deploy.sh
   ```

2. **Make it executable and run:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Option 2: Manual Deployment

1. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Build and push the image:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/vibeai-backend
   ```

3. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy vibeai-backend \
     --image gcr.io/YOUR_PROJECT_ID/vibeai-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080 \
     --memory 512Mi \
     --cpu 1
   ```

### Option 3: Automated Cloud Build

1. **Push your code to a Git repository**
2. **Connect your repository to Cloud Build**
3. **Cloud Build will automatically build and deploy using `cloudbuild.yaml`**

## 🔧 Configuration

### Environment Variables in Cloud Run

Set these in the Google Cloud Console or via CLI:

```bash
gcloud run services update vibeai-backend \
  --region us-central1 \
  --set-env-vars SPOTIFY_CLIENT_ID=your_id,SPOTIFY_CLIENT_SECRET=your_secret
```

### Database Configuration

For production, consider using:
- **Cloud SQL** (PostgreSQL) - Managed database service
- **Firestore** - NoSQL document database (1GB free tier)

## 📊 Monitoring and Logs

### View Logs
```bash
gcloud logs tail --service=vibeai-backend --region=us-central1
```

### View Service Details
```bash
gcloud run services describe vibeai-backend --region=us-central1
```

### Update Service
```bash
gcloud run services update vibeai-backend --region=us-central1
```

## 💰 Cost Optimization

### Free Tier Limits
- **Cloud Run**: 2 million requests/month
- **Cloud Build**: 120 build-minutes/day
- **Container Registry**: 0.5 GB storage

### Scaling Configuration
- **Min instances**: 0 (scales to zero when not in use)
- **Max instances**: 10 (prevents runaway costs)
- **Memory**: 512Mi (adequate for most workloads)

## 🔒 Security Considerations

1. **Environment Variables**: Store sensitive data in Cloud Run environment variables
2. **CORS**: Configure `ALLOWED_ORIGINS` properly
3. **Authentication**: Consider adding authentication if needed
4. **HTTPS**: Automatically provided by Cloud Run

## 🚨 Troubleshooting

### Common Issues

1. **Build fails**: Check Dockerfile syntax and dependencies
2. **Service won't start**: Check environment variables and logs
3. **CORS errors**: Verify `ALLOWED_ORIGINS` configuration
4. **Database connection**: Ensure database is accessible from Cloud Run

### Useful Commands

```bash
# Check service status
gcloud run services list --region=us-central1

# View recent logs
gcloud logs read --service=vibeai-backend --limit=50

# Test the service
curl https://your-service-url.run.app/health
```

## 📚 Next Steps

1. **Set up a custom domain** (optional)
2. **Configure monitoring and alerts**
3. **Set up CI/CD pipeline**
4. **Scale to multiple regions** (if needed)

## 🆘 Need Help?

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Google Cloud Support](https://cloud.google.com/support)

---

**Happy Deploying! 🎉**
