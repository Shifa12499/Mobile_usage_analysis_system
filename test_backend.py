import requests

# Test the backend API
url = "http://localhost:8002/analyze"

# Read the CSV file
with open("usage.csv", "rb") as f:
    files = {"file": ("usage.csv", f, "text/csv")}
    
    print("🚀 Testing Backend API with PySpark...")
    print(f"Uploading: usage.csv")
    print("-" * 60)
    
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Spark Analysis Results:")
        print("-" * 60)
        print(f"📊 Total Usage: {data['total_usage_minutes']} minutes")
        print(f"🏆 Most Used App: {data['most_used_app']}")
        print(f"⏰ Peak Hour: {data['peak_usage_hour']}")
        print("\n📱 App Usage Breakdown:")
        for app in data['app_usage']:
            print(f"   • {app['app']}: {app['minutes']} minutes")
        print("-" * 60)
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
