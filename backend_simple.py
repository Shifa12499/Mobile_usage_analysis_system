from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App categories mapping
APP_CATEGORIES = {
    'YouTube': 'Entertainment',
    'Netflix': 'Entertainment',
    'Prime Video': 'Entertainment',
    'Instagram': 'Social Media',
    'Facebook': 'Social Media',
    'WhatsApp': 'Social Media',
    'Twitter': 'Social Media',
    'Snapchat': 'Social Media',
    'TikTok': 'Social Media',
    'Chrome': 'Productivity',
    'Safari': 'Productivity',
    'Gmail': 'Productivity',
    'Outlook': 'Productivity',
    'Spotify': 'Entertainment',
    'Amazon': 'Shopping',
    'Maps': 'Navigation',
    'Uber': 'Travel',
    'Games': 'Gaming'
}

def get_app_category(app_name):
    """Get category for an app, default to 'Other'"""
    return APP_CATEGORIES.get(app_name, 'Other')

@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze mobile usage data using Pandas"""
    contents = await file.read()

    with open("uploaded.csv", "wb") as f:
        f.write(contents)

    # Read CSV with Pandas
    df = pd.read_csv("uploaded.csv")
    
    # Add category column
    df['category'] = df['app_name'].apply(get_app_category)
    
    print("=" * 60)
    print("📊 PANDAS DATAFRAME INFO:")
    print(f"Shape: {df.shape}")
    print("\nColumns:", df.columns.tolist())
    print("\nSample Data:")
    print(df.head())
    print("=" * 60)

    # Calculate total usage
    total_usage = int(df['usage_minutes'].sum())
    print(f"\n📈 Total Usage: {total_usage} minutes")

    # Find most used app
    app_usage_df = df.groupby('app_name')['usage_minutes'].sum().sort_values(ascending=False)
    top_app = app_usage_df.index[0]
    print(f"🏆 Most Used App: {top_app}")

    # Find peak hour
    hour_usage_df = df.groupby('hour')['usage_minutes'].sum().sort_values(ascending=False)
    peak_hour = str(hour_usage_df.index[0])
    print(f"⏰ Peak Hour: {peak_hour}")

    # Get app-wise usage for chart
    app_usage = [{"app": app, "minutes": int(minutes)}
                 for app, minutes in app_usage_df.items()]
    
    print("\n📱 App Usage Breakdown:")
    for app in app_usage:
        print(f"   • {app['app']}: {app['minutes']} minutes")
    
    # Calculate category-wise usage
    category_usage_df = df.groupby('category')['usage_minutes'].sum().sort_values(ascending=False)
    category_usage = [{"category": cat, "minutes": int(minutes)}
                      for cat, minutes in category_usage_df.items()]
    
    print("\n🏷️ Category Usage Breakdown:")
    for cat in category_usage:
        print(f"   • {cat['category']}: {cat['minutes']} minutes")
    print("=" * 60)

    result = {
        "total_usage_minutes": total_usage,
        "most_used_app": str(top_app),
        "peak_usage_hour": peak_hour,
        "app_usage": app_usage,
        "category_usage": category_usage,
        "engine": "Pandas"
    }
    
    # Cleanup uploaded file
    if os.path.exists("uploaded.csv"):
        os.remove("uploaded.csv")
    
    return result

@app.get("/")
async def root():
    return {"message": "Mobile Usage Analysis API with Pandas", "status": "running"}
