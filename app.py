import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Currency Converter API")

# UI
@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <html>
        <head>
            <title>Currency Converter API</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
                input { padding: 8px; margin: 5px; width: 100px; }
                button { padding: 8px 12px; margin-top: 10px; }
                #result { margin-top: 20px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>💱 Currency Converter API</h1>
            <p>Enter currencies and amount to convert:</p>
            <input type="text" id="from_currency" placeholder="From (USD)">
            <input type="text" id="to_currency" placeholder="To (INR)">
            <input type="number" id="amount" placeholder="Amount">
            <br>
            <button onclick="convert()">Convert</button>
            <div id="result"></div>
            
            <script>
                async function convert() {
                    const from = document.getElementById("from_currency").value.trim();
                    const to = document.getElementById("to_currency").value.trim();
                    const amount = document.getElementById("amount").value.trim();
                    
                    if (!from || !to || !amount) {
                        alert("Please fill all fields");
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/convert?from_currency=${from}&to_currency=${to}&amount=${amount}`);
                        const data = await response.json();
                        
                        if (data.error) {
                            document.getElementById("result").innerText = "Error: " + data.error;
                        } else {
                            document.getElementById("result").innerText = 
                                `${data.amount} ${data.from} = ${data.converted} ${data.to}`;
                        }
                    } catch (err) {
                        document.getElementById("result").innerText = "Error: Unable to fetch data";
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# API
@app.get("/convert")
def convert_currency(from_currency: str, to_currency: str, amount: float):
    from_currency_clean = from_currency.strip().upper()
    to_currency_clean = to_currency.strip().upper()

    try:
        response = requests.get(
            "https://api.frankfurter.app/latest",
            params={
                "amount": amount,
                "from": from_currency_clean,
                "to": to_currency_clean
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        print("API response:", data)  # DEBUG: check API response in terminal
    except requests.RequestException:
        return {
            "from": from_currency_clean,
            "to": to_currency_clean,
            "amount": amount,
            "converted": None,
            "error": "Error fetching data from forex API"
        }

    rates = data.get("rates", {})
    if to_currency_clean not in rates:
        return {
            "from": from_currency_clean,
            "to": to_currency_clean,
            "amount": amount,
            "converted": None,
            "error": "Invalid currency codes or request failed"
        }

    converted_amount = round(rates[to_currency_clean], 2)

    return {
        "from": from_currency_clean,
        "to": to_currency_clean,
        "amount": amount,
        "converted": converted_amount,
        "error": None
    }
