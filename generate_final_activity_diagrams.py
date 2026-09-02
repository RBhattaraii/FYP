import os
import requests

diagrams = {
    "activity1_deal_score.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|USER|
start
:User selects product;

|MOBILE APP|
:Send product ID to API;

|BACKEND|
:System fetches matching products from MongoDB;
if (Found in multiple stores?) then (yes)
  :Compare prices;
  :Calculate Deal Score (1-100);
  :Sort from lowest to highest price;
else (no)
  :Mark as Single Store item;
  :Assign default score;
endif
:Return Ranked Data;

|MOBILE APP|
:Display Ranked Comparison to User;
stop
@enduml
""",
    "activity2_scraper.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|ADMIN|
start
:Admin clicks "Run Scraper";

|BACKEND|
:System authenticates Admin;
fork
  :Scrape Daraz.com.np;
  :Extract HTML DOM;
fork again
  :Scrape Hukut.com;
  :Extract HTML DOM;
end fork
:Clean and Normalize Data;
if (Data Valid?) then (yes)
  :Save to MongoDB;
else (no)
  :Log Error;
endif
:Send Completion Notification;

|ADMIN|
stop
@enduml
""",
    "activity3_search.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|USER|
start
:User enters search keyword;
:Selects Category/Price Filters;
:Clicks Search;

|MOBILE APP|
:Send Search Request;

|BACKEND|
:Query MongoDB for matching products;
if (Products found?) then (yes)
  :Sort products by relevance;
  :Return Product List;
  
  |MOBILE APP|
  :Render Product List UI;
else (no)
  |BACKEND|
  :Return Empty List;
  
  |MOBILE APP|
  :Show "No Products Found" message;
  :Suggest alternative keywords;
endif
stop
@enduml
""",
    "activity4_voucher_checkout.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|USER|
start
:User inputs Voucher Code at Checkout;
:Clicks Apply;

|MOBILE APP|
:Send Voucher Code;

|BACKEND|
:System queries PostgreSQL for Voucher;
if (Voucher exists?) then (yes)
  if (Is Voucher expired?) then (no)
    if (Is Voucher already used?) then (no)
      :Mark Voucher as "Used" in DB;
      :Calculate new total;
      :Return Discount Applied;
      
      |MOBILE APP|
      :Update final price on UI;
    else (yes)
      |BACKEND|
      :Return Error;
      |MOBILE APP|
      :Show "Voucher already used" error;
    endif
  else (yes)
    |BACKEND|
    :Return Error;
    |MOBILE APP|
    :Show "Voucher expired" error;
  endif
else (no)
  |BACKEND|
  :Return Error;
  |MOBILE APP|
  :Show "Invalid Voucher Code" error;
endif
stop
@enduml
""",
    "activity5_admin_analytics.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|ADMIN|
start
:Admin opens Analytics Dashboard;

|MOBILE APP|
:Request Analytics Data;

|BACKEND|
fork
  :Count Total Users (PostgreSQL);
fork again
  :Count Total Products (MongoDB);
fork again
  :Calculate Average Deal Scores;
end fork
:Aggregate all statistics;
:Return Statistics;

|MOBILE APP|
:Generate visual charts;
:Render Dashboard UI;
stop
@enduml
""",
    "activity6_wishlist.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99

|USER|
start
:User taps "Heart" icon;

|MOBILE APP|
if (Is User Logged In?) then (no)
  :Redirect to Login Screen;
  stop
else (yes)
  :Send Wishlist Request;
  
  |BACKEND|
  :Check SavedProducts Database;
  if (Product already saved?) then (yes)
    :Remove product from Wishlist;
    :Return Removed Status;
    
    |MOBILE APP|
    :Show "Removed" toast;
  else (no)
    |BACKEND|
    :Add product to Wishlist;
    :Return Saved Status;
    
    |MOBILE APP|
    :Show "Saved" toast;
  endif
endif
stop
@enduml
"""
}

output_dir = r"C:\Users\NITOR 5\.gemini\antigravity-ide\brain\21def897-9bb6-4def-8b67-9100d17652e1"

for filename, puml in diagrams.items():
    url = "https://kroki.io/plantuml/png"
    response = requests.post(url, data=puml.encode('utf-8'), headers={'Content-Type': 'text/plain'})
    if response.status_code == 200:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Generated {filename}")
    else:
        print(f"Failed to generate {filename}: {response.status_code}")
