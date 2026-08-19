import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from supabase import create_client

# Create files from GitHub Secrets
with open("credentials.json", "w") as f:
    f.write(os.environ["GOOGLE_CREDENTIALS"])

with open("token.json", "w") as f:
    f.write(os.environ["GOOGLE_TOKEN"])

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# Load credentials
creds = Credentials.from_authorized_user_file(
    "token.json",
    SCOPES
)

# Refresh token if needed
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

# Build Search Console service
service = build(
    "searchconsole",
    "v1",
    credentials=creds
)

SITE_URL = "https://shivrajpatilnew.vercel.app/"

# Get sitemap data
response = service.sitemaps().list(
    siteUrl=SITE_URL
).execute()

# Connect Supabase
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# Save data
for sitemap in response.get("sitemap", []):

    discovered_pages = 0
    discovered_videos = 0

    for content in sitemap.get("contents", []):
        if content.get("type") == "web":
            discovered_pages = int(content.get("submitted", 0))

        elif content.get("type") == "video":
            discovered_videos = int(content.get("submitted", 0))

    result = supabase.table("sitemap_status").insert({
        "sitemap_url": sitemap.get("path"),
        "sitemap_type": sitemap.get("type"),
        "submitted_at": sitemap.get("lastSubmitted"),
        "last_read_at": sitemap.get("lastDownloaded"),
        "status": "Success" if sitemap.get("errors") == "0" else "Error",
        "discovered_pages": discovered_pages,
        "discovered_videos": discovered_videos
    }).execute()

    print(f"Inserted: {sitemap.get('path')}")

print("Sync completed successfully.")
