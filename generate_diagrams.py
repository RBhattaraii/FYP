import os
import requests

diagrams = {
    "diagram1_login.png": """
@startuml
skinparam maxMessageSize 150
skinparam ParticipantBackgroundColor #FFFFEE
skinparam ParticipantBorderColor #A80036
skinparam SequenceLifeLineBorderColor #A80036
skinparam SequenceArrowColor #A80036

actor ": User" as User
participant "app : MobileApp" as App
participant "api : FastAPIEngine" as API
database "db : PostgreSQL" as DB

User -> App : login(email, password)
activate App
App -> API : POST /auth/login
activate API
API -> DB : getUserByEmail(email)
activate DB
DB --> API : userRecord
deactivate DB
API -> API : verifyHash(password)
alt Valid Credentials
    API -> API : generateJWT(userId)
    API --> App : 200 OK (token)
    App --> User : showDashboard()
else Invalid Credentials
    API --> App : 401 Unauthorized
    App --> User : showError("Invalid Credentials")
end
deactivate API
deactivate App
@enduml
""",
    "diagram2_compare.png": """
@startuml
skinparam maxMessageSize 150
skinparam ParticipantBackgroundColor #FFFFEE
skinparam ParticipantBorderColor #A80036
skinparam SequenceLifeLineBorderColor #A80036
skinparam SequenceArrowColor #A80036

actor ": Shopper" as Shopper
participant "app : MobileApp" as App
participant "compareService : ComparisonEngine" as Compare
participant "algo : DealScoreAlgorithm" as Algo
database "nosql : MongoDB" as DB

Shopper -> App : selectProduct(productId)
activate App
App -> Compare : GET /compare/{productId}
activate Compare
Compare -> DB : fetchIdenticalProducts(productId)
activate DB
DB --> Compare : List<ScrapedProduct>
deactivate DB
loop for each ScrapedProduct
    Compare -> Algo : calculateScore(currentPrice, averagePrice)
    activate Algo
    Algo --> Compare : dealScore
    deactivate Algo
end
Compare -> Compare : sortListingsByScore()
Compare --> App : RankedComparisonData
deactivate Compare
App --> Shopper : displayDeals()
deactivate App
@enduml
""",
    "diagram3_voucher.png": """
@startuml
skinparam maxMessageSize 150
skinparam ParticipantBackgroundColor #FFFFEE
skinparam ParticipantBorderColor #A80036
skinparam SequenceLifeLineBorderColor #A80036
skinparam SequenceArrowColor #A80036

actor ": User" as User
participant "app : MobileApp" as App
participant "pointsApi : VoucherService" as API
database "ledger : PostgreSQL" as DB

User -> App : redeemVoucher(voucherId)
activate App
App -> API : POST /points/redeem(voucherId, token)
activate API
API -> API : validateToken(token)
API -> DB : getPointsBalance(userId)
activate DB
DB --> API : currentBalance
deactivate DB
alt currentBalance >= requiredPoints
    API -> DB : beginTransaction()
    activate DB
    DB -> DB : deductPoints(userId, requiredPoints)
    DB -> DB : insertVoucher(userId, voucherId)
    DB --> API : commitTransaction()
    deactivate DB
    API --> App : 200 OK (voucherCode)
    App --> User : displaySuccess(voucherCode)
else currentBalance < requiredPoints
    API --> App : 400 Bad Request
    App --> User : showError("Insufficient Points")
end
deactivate API
deactivate App
@enduml
""",
    "diagram4_scraper.png": """
@startuml
skinparam maxMessageSize 150
skinparam ParticipantBackgroundColor #FFFFEE
skinparam ParticipantBorderColor #A80036
skinparam SequenceLifeLineBorderColor #A80036
skinparam SequenceArrowColor #A80036

actor ": Admin" as Admin
participant "dashboard : AdminDashboard" as App
participant "api : FastAPIService" as API
participant "worker : BackgroundTask" as Worker
participant "external : DarazAPI" as Daraz
database "db : MongoDB" as DB

Admin -> App : triggerScraper(store="daraz")
activate App
App -> API : POST /scraper/trigger
activate API
API -> Worker : scheduleTask(run_scraper)
activate Worker
API --> App : 202 Accepted
deactivate API
App --> Admin : showStatus("Scraping Queued")
deactivate App

Worker -> Daraz : HTTP GET /category
activate Daraz
Daraz --> Worker : HTML Document
deactivate Daraz

Worker -> Worker : parseHTML()
Worker -> Worker : extractProductData()
Worker -> DB : bulkUpsert(ProductData)
activate DB
DB --> Worker : acknowledge()
deactivate DB
Worker -> API : updateStatus("Complete")
deactivate Worker
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
