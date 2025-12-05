# How to Deploy Your HTTrack Actor to Apify

## Option 1: Install Apify CLI and Deploy (Recommended)

### Step 1: Install Apify CLI

Open PowerShell as Administrator and run:

```powershell
npm install -g apify-cli
```

If you don't have Node.js/npm installed, download and install it first from:
https://nodejs.org/ (LTS version recommended)

### Step 2: Login to Apify

```powershell
apify login
```

This will open a browser window for authentication. Follow the prompts.

### Step 3: Navigate to Your Project

```powershell
cd "C:\Users\asus\OneDrive\Desktop\Shree Swami Smartha\httrack"
```

### Step 4: Push to Apify

```powershell
apify push
```

This will:
- Build your Docker image
- Upload it to Apify
- Create/update your Actor on the platform

### Step 5: Access Your Actor

After successful push, you'll get a link like:
```
https://console.apify.com/actors/<your-actor-id>
```

## Option 2: Use Apify Console (Manual Upload)

If you prefer not to use CLI:

### Step 1: Create ZIP of Your Project

Create a ZIP file containing:
- Dockerfile
- requirements.txt
- src/ folder
- .actor/ folder
- README.md

### Step 2: Go to Apify Console

1. Visit: https://console.apify.com/
2. Click "Actors" in the sidebar
3. Click "+ Create new"
4. Choose "Import from code"

### Step 3: Upload Your Code

1. Upload the ZIP file OR connect your GitHub repository
2. Configure Actor settings
3. Click "Build"

## Option 3: Use Git Integration

### Step 1: Create GitHub Repository

```powershell
# Initialize git (if not already)
cd "C:\Users\asus\OneDrive\Desktop\Shree Swami Smartha\httrack"
git init
git add .
git commit -m "Initial commit - HTTrack Website Scraper Actor"
```

### Step 2: Push to GitHub

```powershell
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/httrack-actor.git
git branch -M main
git push -u origin main
```

### Step 3: Connect to Apify

1. Go to Apify Console
2. Create new Actor
3. Choose "Connect GitHub repository"
4. Select your repository
5. Configure and build

## Quick Test Before Deploying

Test locally first:

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the Actor locally
python -m src
```

Or if you have Docker:

```powershell
# Build Docker image
docker build -t httrack-scraper .

# Run container
docker run -e APIFY_INPUT_JSON='{"url":"https://example.com"}' httrack-scraper
```

## Verify Installation

After pushing, verify your Actor:

1. Go to Apify Console
2. Find your Actor: "Website Scraper"
3. Click "Try it"
4. Enter test input:
   ```json
   {
     "url": "https://example.com"
   }
   ```
5. Click "Start"
6. Check logs and output

## Troubleshooting

### Error: "apify: command not found"

**Solution**: Install Apify CLI:
```powershell
npm install -g apify-cli
```

### Error: "npm: command not found"

**Solution**: Install Node.js from https://nodejs.org/

### Error: "Docker build failed"

**Solution**: 
1. Install Docker Desktop for Windows
2. Ensure Docker is running
3. Try building locally first: `docker build -t test .`

### Error: "Authentication failed"

**Solution**:
1. Run `apify logout`
2. Run `apify login` again
3. Complete authentication in browser

## Actor Configuration

Your Actor is configured with:

- **Name**: httrack-website-scraper
- **Title**: Website Scraper
- **Version**: 1.0
- **Runtime**: Python 3.13
- **Base image**: apify/actor-python:3.13

## Next Steps After Deployment

1. **Test**: Run with various URLs
2. **Monitor**: Check logs and performance
3. **Share**: Make public or keep private
4. **Integrate**: Use via API or webhooks
5. **Scale**: Adjust memory/CPU if needed

## Useful Commands

```powershell
# Check Apify CLI version
apify --version

# Login
apify login

# Push Actor
apify push

# Run locally
apify run

# View logs
apify logs

# Info about current Actor
apify info
```

## Support

- **Apify Docs**: https://docs.apify.com/
- **CLI Docs**: https://docs.apify.com/cli/
- **Community**: https://discord.gg/jyEM2PRvMU
- **Support**: support@apify.com

## Summary

Choose the method that works best for you:
- **Fastest**: Install CLI and `apify push`
- **Easiest**: Upload ZIP in Console
- **Best for teams**: Git integration

All methods result in the same deployed Actor!

