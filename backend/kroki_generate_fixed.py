import zlib
import base64

def encode_kroki(text):
    compressed = zlib.compress(text.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    return f"https://kroki.io/plantuml/png/{encoded}"

d1 = """@startuml
skinparam monochrome true
hide circle
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 16
skinparam class {
    BackgroundColor White
    BorderColor Black
    BorderThickness 2
    ArrowColor Black
    ArrowThickness 2
}
skinparam ArrowFontSize 16
skinparam ArrowFontStyle bold
skinparam linetype ortho
skinparam nodesep 100
skinparam ranksep 100

class User {
  - user_id : String
  - email : String
  - password_hash : String
  - points : Int
  - referral_code : String
  + register() : Boolean
  + login() : String
  + update_profile() : Boolean
}

class Voucher {
  - voucher_id : String
  - code : String
  - discount_amount : Float
  - is_redeemed : Boolean
  + generate_code() : String
  + redeem() : Boolean
}

class Points_Transaction {
  - transaction_id : String
  - transaction_type : String
  - points_change : Int
  + log_transaction() : Void
}

class AuthController {
  + login_user(credentials) : Token
  + register_user(data) : User
  + verify_token(token) : Boolean
}

class PointsService {
  + add_points(user_id, amount) : Void
  + deduct_points(user_id, amount) : Boolean
  + mint_voucher(user_id, points) : Voucher
}

User "1" -- "*" Voucher : <back:white> owns > </back>
User "1" -- "*" Points_Transaction : <back:white> has > </back>
AuthController ..> User : <back:white> manages </back>
PointsService ..> User : <back:white> modifies </back>
PointsService ..> Voucher : <back:white> creates </back>
PointsService ..> Points_Transaction : <back:white> creates </back>
@enduml"""

d2 = """@startuml
skinparam monochrome true
hide circle
skinparam defaultFontName "Times New Roman"
skinparam defaultFontSize 16
skinparam class {
    BackgroundColor White
    BorderColor Black
    BorderThickness 2
    ArrowColor Black
    ArrowThickness 2
}
skinparam ArrowFontSize 16
skinparam ArrowFontStyle bold
skinparam linetype ortho
skinparam nodesep 100
skinparam ranksep 100

class Product {
  - _id : String
  - name : String
  - category : String
  - normalized_title : String
  + calculate_deal_score() : Float
}

class Store_Listing {
  - store_name : String
  - current_price : Float
  - url : String
  + update_price(new_price) : Void
}

class Price_History {
  - price : Float
  - recorded_at : DateTime
}

class Search_Cache {
  - query : String
  - tier1_results : JSON
  + is_valid() : Boolean
}

class ScraperService {
  + run_background_scrape(category) : Void
  + parse_html(html) : Dictionary
  - normalize_title(raw_title) : String
}

class SearchController {
  + search_products(query) : List
  - check_tier1_cache(query) : JSON
  - execute_deep_search(query) : List
}

Product "1" *-- "*" Store_Listing : <back:white> contains </back>
Store_Listing "1" *-- "*" Price_History : <back:white> tracks </back>
ScraperService ..> Product : <back:white> creates/updates </back>
ScraperService ..> Store_Listing : <back:white> creates/updates </back>
SearchController ..> Product : <back:white> reads </back>
SearchController ..> Search_Cache : <back:white> reads/writes </back>
@enduml"""

print("D1=" + encode_kroki(d1))
print("D2=" + encode_kroki(d2))
