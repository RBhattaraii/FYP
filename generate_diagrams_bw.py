import os
import requests

diagrams = {
    "diagram1_login.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99
hide footbox

participant "Shopper" as User
participant "Mobile App" as App
participant "Backend System" as API
participant "Database" as DB

User -> App : Enter Email and Password
App -> API : Send Credentials
API -> DB : Check User Details
DB -> API : Return Verification Result
API -> App : Authentication Success
App -> User : Show Dashboard

note over User, DB : User Authentication Flow
@enduml
""",
    "diagram2_compare.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99
hide footbox

participant "Shopper" as User
participant "Mobile App" as App
participant "FastAPI Backend" as API
participant "Deal Score Engine" as Algo
participant "MongoDB" as DB

User -> App : Select Product to Compare
App -> API : Request Comparison Data
API -> DB : Fetch Identical Products
DB -> API : Return Scraped Prices
API -> Algo : Process Price Data
Algo -> Algo : Analyze Historical Price Drops
Algo -> API : Return Calculated Deal Score
API -> API : Sort Deals from Best to Worst
API -> App : Return Ranked List
App -> User : Display Best Deals

note over User, DB : Product Comparison and Scoring
@enduml
""",
    "diagram3_voucher.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99
hide footbox

participant "Shopper" as User
participant "Mobile App" as App
participant "Points Service" as API
participant "PostgreSQL Ledger" as DB

User -> App : Request to Redeem Voucher
App -> API : Send Redemption Request
API -> DB : Verify Points Balance
DB -> API : Confirm Sufficient Points
API -> DB : Deduct Points and Create Voucher
DB -> DB : Safely Update Ledger
DB -> API : Transaction Successful
API -> App : Return Voucher Code
App -> User : Display Voucher Code

note over User, DB : Voucher Redemption Process
@enduml
""",
    "diagram4_scraper.png": """
@startuml
skinparam monochrome true
skinparam NoteBackgroundColor #FFFF99
hide footbox

participant "Administrator" as Admin
participant "Admin Dashboard" as App
participant "FastAPI System" as API
participant "Scraping Engine" as Scraper
participant "External E-Commerce" as Store
participant "Database" as DB

Admin -> App : Trigger Web Scraper
App -> API : Send Scrape Request
API -> Scraper : Start Background Job
Scraper -> API : Confirm Job Started
API -> App : Return Success Message
App -> Admin : Show Scraping Started

Scraper -> Store : Fetch Product Pages
Store -> Scraper : Return HTML Data
Scraper -> Scraper : Parse and Extract Prices
Scraper -> DB : Save New Products
DB -> Scraper : Confirm Save

note over Admin, DB : Asynchronous Web Scraping Engine
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
