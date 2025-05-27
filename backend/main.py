from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
import os
import google.generativeai as genai
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
import json

my_api_key = ""
genai.configure(api_key=my_api_key)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
TRADINGVIEW_WIDGET_BASE = "https://www.tradingview.com/widgetembed/?frameElementId=tv_{symbol}_{interval}&symbol={symbol}&interval={interval}&theme=dark&style=1&timezone=Etc%2FUTC&saveimage=1&toolbarbg=f1f3f6&studies=[]&withdateranges=1&hideideas=1&enabled_features=%5B%22study_templates%22%5D"

@app.get("/")
async def root():
    print("Root endpoint called")
    return {"message": "Hello from backend!"}

@app.get("/screenshot/")
async def get_chart_screenshot(symbol: str = Query(...), interval: str = Query(...)):
    print(f"Screenshot endpoint called with symbol={symbol}, interval={interval}")
    url = TRADINGVIEW_WIDGET_BASE.format(symbol=symbol, interval=interval)
    screenshot_path = f"screenshot_{symbol.replace(':','_')}_{interval}.png"

    try:
        async with async_playwright() as p:
            print("Launching browser for screenshot...")
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1200, "height": 800})
            print(f"Navigating to {url}")
            await page.goto(url)
            await page.wait_for_timeout(4000)
            print(f"Taking screenshot and saving to {screenshot_path}")
            await page.screenshot(path=screenshot_path)
            await browser.close()
            print("Browser closed after screenshot")
    except Exception as e:
        print(f"Error during screenshot capture: {e}")
        return JSONResponse(content={"error": "Failed during screenshot capture", "details": str(e)}, status_code=500)

    if os.path.exists(screenshot_path):
        print(f"Screenshot successfully saved at {screenshot_path}")
        return JSONResponse(content={"message": "Screenshot taken", "path": screenshot_path})
    else:
        print(f"Screenshot file not found at {screenshot_path}")
        return JSONResponse(content={"error": "Failed to create screenshot"}, status_code=500)

GEMINI_PROMPT = """You are a professional trading assistant.

Analyze the following trading chart image and identify if there is a clear trade setup. Use only price action, chart patterns, and technical analysis.

Return your analysis in this exact JSON format:
{{
  "symbol": "{symbol}",
  "interval": "{interval}",
  "trade_signal": "LONG or SHORT or NONE",
  "pattern": "Name of chart pattern or setup",
  "entry": Entry price or null,
  "stop_loss": Stop loss level or null,
  "take_profit": Take profit level or null,
  "confidence": "High/Medium/Low"
}}

Do not add any commentary or explanation. Stick to the JSON.
"""
def clean_response_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return text

@app.get("/analyze/")
async def analyze_chart(symbol: str = Query(...), interval: str = Query(...)):
    print(f"Analyze endpoint called with symbol={symbol}, interval={interval}")

    screenshot_path = f"screenshot_{symbol.replace(':','_')}_{interval}.png"
    url = TRADINGVIEW_WIDGET_BASE.format(symbol=symbol, interval=interval)

    # Step 1: Take screenshot
    try:
        async with async_playwright() as p:
            print("Launching browser for analysis screenshot...")
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 1200, "height": 800})
            print(f"Navigating to {url}")
            await page.goto(url)
            await page.wait_for_timeout(4000)
            print(f"Taking screenshot for analysis and saving to {screenshot_path}")
            await page.screenshot(path=screenshot_path)
            await browser.close()
            print("Browser closed after analysis screenshot")
    except Exception as e:
        print(f"Error during screenshot capture for analysis: {e}")
        return JSONResponse(content={"error": "Failed during screenshot capture", "details": str(e)}, status_code=500)

    if not os.path.exists(screenshot_path):
        print(f"Screenshot file not found at {screenshot_path} after capture")
        return JSONResponse(content={"error": "Failed to capture screenshot"}, status_code=500)

    # Step 2: Open image & send to Gemini model
    try:
        print(f"Opening screenshot image at {screenshot_path}")
        image = Image.open(screenshot_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return JSONResponse(content={"error": "Failed to open screenshot image", "details": str(e)}, status_code=500)

    try:
        print("Initializing Gemini model")
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        prompt = GEMINI_PROMPT.format(symbol=symbol, interval=interval)
        print("Sending request to Gemini model...")
        response = model.generate_content([prompt, image])
        print("Response received from Gemini")
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return JSONResponse(content={"error": "Failed to generate content from Gemini", "details": str(e)}, status_code=500)

    # Step 3: Parse and return response
    try:
        cleaned_content =  clean_response_text(response.text)
        print(f"Raw Gemini response: {cleaned_content}")
        parsed_json = json.loads(cleaned_content)
        print(f"Parsed Gemini JSON: {parsed_json}")
        return JSONResponse(content=parsed_json, status_code=200)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return JSONResponse(content={"error": "Failed to parse Gemini response", "raw_response": response.text}, status_code=500)
