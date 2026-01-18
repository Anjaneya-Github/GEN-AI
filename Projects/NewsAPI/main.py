from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests, os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI(title="Trending News API")
templates = Jinja2Templates(directory=".")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://gnews.io/api/v4/top-headlines"

def fetch_news(country="in", category=None):
    if not NEWS_API_KEY or NEWS_API_KEY == "your_api_key_here":
        raise HTTPException(status_code=500, detail="Server configuration error: NEWS_API_KEY is missing or invalid.")

    params = {"apikey": NEWS_API_KEY, "country": country}
    if category:
        params["category"] = category

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        try:
            detail = http_err.response.json().get("message", str(http_err))
        except ValueError:
            detail = str(http_err)
        raise HTTPException(status_code=http_err.response.status_code, detail=detail)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending")
def get_trending_news(country: str = "in", category: Optional[str] = None):
    data = fetch_news(country, category)
    headlines = [{"title": a["title"], "url": a["url"]} for a in data.get("articles", [])]
    return {"trending_headlines": headlines}

@app.get("/", response_class=HTMLResponse)
def root(request: Request, country: str = "in", category: Optional[str] = None):
    articles = []
    error_message = None
    try:
        data = fetch_news(country, category)
        articles = data.get("articles", [])
    except Exception as e:
        error_message = str(e)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "articles": articles,
        "country": country,
        "category": category,
        "error": error_message
    })
    