# Vercel Deployment Guide for VRO Daptar

## Option 1: Deploy SvelteKit as Main Project (Recommended)

### Repository Structure
```
vro-daptar/
├── src/
│   ├── lib/
│   │   └── gsheet-helper.ts
│   ├── routes/
│   │   ├── api/
│   │   │   ├── inspections/+server.ts
│   │   │   └── inspect/+server.ts
│   │   ├── inspect/+page.svelte
│   │   ├── +page.svelte
│   │   └── +layout.svelte
├── credentials.json          # ← MOVE THIS FILE HERE
├── package.json
├── svelte.config.js
├── vercel.json
├── .env.example
├── README.md
└── [other files...]
```

### Steps to Restructure:

1. **Move SvelteKit files to root:**
   ```bash
   # Copy all files from vro-daptar-svelte to root
   cp vro-daptar-svelte/* ./
   cp vro-daptar-svelte/.* ./  # Include hidden files
   ```

2. **Move credentials:**
   ```bash
   mv vro-daptar-svelte/credentials.json ./
   ```

3. **Remove old Flask files (optional):**
   ```bash
   rm -rf templates/ *.py requirements.txt Procfile
   ```

## Option 2: Deploy from Subdirectory

If you want to keep both versions, deploy from the `vro-daptar-svelte` subdirectory.

## Vercel Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Convert to SvelteKit and prepare for Vercel deployment"
git push origin main
```

### 2. Connect to Vercel

1. **Go to Vercel Dashboard:**
   - Visit https://vercel.com/dashboard
   - Click "New Project"

2. **Import Repository:**
   - Connect your GitHub account
   - Select `arc198614/vro_daptar` repository
   - For Option 2: Set "Root Directory" to `vro-daptar-svelte`

3. **Configure Build Settings:**
   - **Framework Preset:** SvelteKit
   - **Root Directory:** (leave empty for Option 1, `vro-daptar-svelte` for Option 2)
   - **Build Command:** `npm run build`
   - **Output Directory:** `.svelte-kit/output` (auto-detected)

### 3. Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```
GOOGLE_SHEET_ID = 11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU
GOOGLE_CREDENTIALS_JSON = {"type":"service_account","project_id":"sdmoffice",...}
GOOGLE_DRIVE_FOLDER_ID = # Optional: your Drive folder ID
```

**Important:** Copy the entire `credentials.json` content as the value for `GOOGLE_CREDENTIALS_JSON`.

### 4. Domain Setup (Optional)

- Vercel will provide a default domain: `your-project.vercel.app`
- You can add a custom domain in Project Settings → Domains

### 5. Deploy

- Click "Deploy"
- Wait for build completion (usually 2-3 minutes)
- Your app will be live!

## File Locations Summary

### Essential Files for Deployment:
```
vro-daptar/
├── credentials.json              # ← Google service account credentials
├── package.json                  # ← Dependencies and scripts
├── svelte.config.js             # ← Vercel adapter configuration
├── vercel.json                  # ← Vercel-specific settings
├── src/
│   ├── lib/
│   │   └── gsheet-helper.ts     # ← Google APIs integration
│   ├── routes/
│   │   ├── api/                 # ← Serverless API endpoints
│   │   ├── +page.svelte         # ← Dashboard page
│   │   ├── inspect/+page.svelte # ← Inspection form
│   │   └── +layout.svelte       # ← App layout
├── app.html                     # ← HTML template
└── app.d.ts                     # ← TypeScript declarations
```

### Files NOT Needed for Deployment:
- `test_google_apis.py` (local testing only)
- `*.py` files (Flask version)
- `templates/` (Flask templates)
- `requirements.txt` (Python dependencies)
- `Procfile` (Heroku config)

## Troubleshooting

### Build Fails:
1. Check that `credentials.json` is in the correct location
2. Ensure all environment variables are set
3. Verify `package.json` has correct dependencies

### API Errors:
1. Run `python test_google_apis.py` locally to verify Google API setup
2. Check Vercel function logs for detailed error messages
3. Ensure Google APIs are enabled in Google Cloud Console

### File Upload Issues:
1. Verify `GOOGLE_DRIVE_FOLDER_ID` is set (or leave empty for root)
2. Check that service account has Drive permissions
3. Ensure Google Drive API is enabled

## Post-Deployment Testing

1. **Test Dashboard:** Visit the deployed URL
2. **Test Form:** Navigate to `/inspect`
3. **Test File Upload:** Submit a form with file attachments
4. **Check Logs:** Use Vercel dashboard → Functions to monitor API calls

## Cost Considerations

- **Vercel Hobby Plan:** Free for personal projects
- **Google APIs:** Free quota should be sufficient for moderate usage
- **Google Drive:** Free storage for uploaded files

Your SvelteKit app is now ready for production deployment! 🚀