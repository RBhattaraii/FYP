import os
import requests

diagrams = {
    "activity1_deal_score.png": """
@startuml
skinparam monochrome true
start
:User selects product;
:System fetches matching products from MongoDB;
if (Found in multiple stores?) then (yes)
  :Compare prices;
  :Calculate Deal Score (1-100);
  :Sort from lowest to highest price;
else (no)
  :Mark as Single Store item;
  :Assign default score;
endif
:Display Ranked Comparison to User;
stop
@enduml
""",
    "activity2_scraper.png": """
@startuml
skinparam monochrome true
start
:Admin clicks "Run Scraper";
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
stop
@enduml
""",
    "activity3_voucher.png": """
@startuml
skinparam monochrome true
start
:User requests Voucher Redemption;
:Fetch User Points Balance;
if (Balance >= Required Points?) then (yes)
  :Start Database Transaction;
  :Deduct Points from Ledger;
  :Create Voucher Record;
  :Commit Transaction;
  :Return Voucher Code to User;
else (no)
  :Disable Redeem Button;
  :Show "Insufficient Points" Error;
endif
stop
@enduml
""",
    "activity4_registration.png": """
@startuml
skinparam monochrome true
start
:User submits Registration Form;
if (Is Email Valid?) then (yes)
  if (Password length >= 8?) then (yes)
    if (Email already exists?) then (yes)
      :Show "Email already in use";
    else (no)
      :Hash Password (Bcrypt);
      :Save User to PostgreSQL;
      :Generate JWT Token;
      :Redirect to Dashboard;
    endif
  else (no)
    :Show "Password too short" Error;
  endif
else (no)
  :Show "Invalid Email Format" Error;
endif
stop
@enduml
""",
    "activity5_search.png": """
@startuml
skinparam monochrome true
start
:User enters search term;
:Apply Price Filters (Min/Max);
:Query MongoDB;
if (Results Found?) then (yes)
  :Render Product List;
else (no)
  :Show "No Products Found" message;
  :Suggest Alternative Keywords;
endif
stop
@enduml
""",
    "activity6_wishlist.png": """
@startuml
skinparam monochrome true
start
:User taps "Heart" icon;
if (Is User Logged In?) then (no)
  :Redirect to Login Screen;
  stop
else (yes)
  :Check SavedProducts Database;
  if (Product already saved?) then (yes)
    :Remove product from Wishlist;
    :Show "Removed" toast;
  else (no)
    :Add product to Wishlist;
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
