"""
AI Price Forecasting Service for PricePilot
Implements Holt's Linear Trend Model (Double Exponential Smoothing) and Ordinary Least Squares (OLS) Linear Regression 
for tracking and predicting product price trends.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import math

def calculate_ols_regression(prices: List[float], times: List[float]) -> Tuple[float, float, float, float]:
    """
    Calculate Ordinary Least Squares (OLS) Linear Regression: Y = alpha + beta * X
    Returns:
        alpha: Intercept
        beta: Slope (price change per day)
        r_squared: Coefficient of determination
        std_error: Standard error of the estimate
    """
    n = len(prices)
    if n < 2:
        return prices[0] if n == 1 else 0.0, 0.0, 1.0, 0.0
    
    # Calculate means
    mean_x = sum(times) / n
    mean_y = sum(prices) / n
    
    # Calculate variance and covariance
    num = 0.0
    den = 0.0
    for x, y in zip(times, prices):
        num += (x - mean_x) * (y - mean_y)
        den += (x - mean_x) ** 2
        
    beta = num / den if den != 0 else 0.0
    alpha = mean_y - beta * mean_x
    
    # Calculate R-squared and Standard Error of Estimate
    ss_res = 0.0
    ss_tot = 0.0
    for x, y in zip(times, prices):
        pred_y = alpha + beta * x
        ss_res += (y - pred_y) ** 2
        ss_tot += (y - mean_y) ** 2
        
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
    std_error = math.sqrt(ss_res / (n - 2)) if n > 2 else 0.0
    
    return alpha, beta, r_squared, std_error

def holt_linear_trend_forecast(
    prices: List[float], 
    steps: int, 
    alpha: float = 0.2, 
    beta: float = 0.1
) -> List[float]:
    """
    Double Exponential Smoothing (Holt's Linear Trend Model)
    Ideal for time series exhibiting linear trend.
    Formula:
        Level: L_t = alpha * Y_t + (1 - alpha) * (L_{t-1} + T_{t-1})
        Trend: T_t = beta * (L_t - L_{t-1}) + (1 - beta) * trend
        Forecast: F_{t+h} = L_t + h * T_t
    """
    n = len(prices)
    if n < 2:
        return [prices[0]] * steps if n == 1 else [0.0] * steps
        
    # Initialization
    level = prices[0]
    trend = prices[1] - prices[0]
    
    for i in range(1, n):
        prev_level = level
        level = alpha * prices[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        
    forecasts = []
    for h in range(1, steps + 1):
        forecasts.append(max(0.0, level + h * trend))
        
    return forecasts

def generate_price_forecast(
    price_history: List[Dict[str, Any]], 
    current_price: float
) -> Dict[str, Any]:
    """
    Generate price prediction and analytical recommendations for the frontend.
    
    Returns a dict with:
        - predicted_price_15_days: Expected price in 15 days
        - predicted_price_30_days: Expected price in 30 days
        - trend_direction: "up", "down", or "stable"
        - confidence_score: Number between 0 and 100
        - recommendation: "Buy Now", "Wait", or "Neutral"
        - explanation: Academic reasoning explaining the prediction
    """
    # If no price history is available, default to current price
    if not price_history or len(price_history) < 2:
        return {
            "predicted_price_15_days": current_price,
            "predicted_price_30_days": current_price,
            "trend_direction": "stable",
            "confidence_score": 50,
            "recommendation": "Neutral",
            "explanation": "Insufficient historical data points to generate price forecasts. PricePilot will monitor the price and generate trends over the coming days."
        }
        
    # Sort history chronologically
    sorted_history = sorted(price_history, key=lambda x: x['date'])
    
    # Extract prices and compute relative date offsets (in days since start)
    prices = [p['price'] for p in sorted_history]
    
    # Parse dates
    start_date = datetime.fromisoformat(sorted_history[0]['date'].replace('Z', '+00:00'))
    times = []
    for entry in sorted_history:
        d = datetime.fromisoformat(entry['date'].replace('Z', '+00:00'))
        delta_days = (d - start_date).days + (d - start_date).seconds / 86400.0
        times.append(delta_days)
        
    # Ensure times are unique/ascending (handle same-day scrapes)
    for i in range(1, len(times)):
        if times[i] <= times[i-1]:
            times[i] = times[i-1] + 0.01
            
    # Compute Linear Regression OLS
    alpha, beta, r_squared, std_error = calculate_ols_regression(prices, times)
    
    # Holt-Winters forecast
    forecasts = holt_linear_trend_forecast(prices, steps=30)
    pred_15 = forecasts[14] if len(forecasts) >= 15 else forecasts[-1]
    pred_30 = forecasts[29] if len(forecasts) >= 30 else forecasts[-1]
    
    # OLS trend direction
    # beta is price change per day. Calculate total percentage change over last 30 days based on beta
    price_change_30_days = beta * 30
    percent_change = (price_change_30_days / current_price) if current_price != 0 else 0
    
    if percent_change > 0.02:
        trend_direction = "up"
    elif percent_change < -0.02:
        trend_direction = "down"
    else:
        trend_direction = "stable"
        
    # Calculate confidence score based on data density and OLS fit R-squared
    # More data points = higher confidence
    density_factor = min(len(prices) / 10.0, 1.0) # Cap at 10 data points
    fit_factor = max(0.0, min(1.0, r_squared)) if len(prices) >= 3 else 0.5
    confidence_score = int((0.4 * density_factor + 0.6 * fit_factor) * 100)
    # Clamp confidence score
    confidence_score = max(30, min(confidence_score, 95))
    
    # Determine recommendation
    if trend_direction == "down":
        recommendation = "Wait"
        explanation = f"Price is exhibiting a downward trend (-{abs(percent_change)*100:.1f}% expected over 30 days) according to Holt's Linear Trend analysis. We recommend waiting for further price drops."
    elif trend_direction == "up":
        recommendation = "Buy Now"
        explanation = f"Price is projected to rise (+{percent_change*100:.1f}% expected over 30 days) due to market trend shifts. Buying now is recommended to lock in the lower price."
    else:
        recommendation = "Buy Now" if current_price <= min(prices) * 1.02 else "Neutral"
        explanation = "Price is stable and currently holding near its standard benchmark range. Holt forecast indicates nominal fluctuations."
        
    return {
        "predicted_price_15_days": round(pred_15, 2),
        "predicted_price_30_days": round(pred_30, 2),
        "trend_direction": trend_direction,
        "confidence_score": confidence_score,
        "recommendation": recommendation,
        "explanation": explanation
    }
