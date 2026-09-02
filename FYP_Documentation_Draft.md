4.4	Interface Design
The PricePilot platform's interface design has been crafted to be intuitive, clean, and highly responsive to facilitate seamless interaction for the users. The system is designed so that each screen delivers immediate, clear responses when searching for products, and the layouts are simplified to prevent information overload. The minimalist nature and clean layouts ensure that users can focus on what matters most: comparing prices in real-time. The system guarantees an effortless user experience where essential features such as product discovery, price comparisons, wishlist management, and setting price alerts are always easily accessible.

4.4.1	Wireframes 
To effectively outline the structure of PricePilot, the following wireframes should be created to showcase the core concepts of the smart price comparison platform:

Figure X
Wireframe of Login / Signup Page
Note: This wireframe should show a clean authentication gateway with email/password fields, a prominent logo, and social login buttons. It represents the secure entry point into the system.

Figure Y
Wireframe of Home Page (Deals Feed)
Note: This wireframe should illustrate a top search bar, horizontal scrolling categories, and a vertical feed of product cards highlighting current deals. It focuses on intuitive product discovery.

Figure Z
Wireframe of Product Comparison Page
Note: This is the most crucial wireframe. It should feature the product image at the top, a line chart for "Price History", and a list of different e-commerce stores (e.g., Daraz, Jeevee, Oliz) with their respective prices for the same item. 

Figure A
Wireframe of Search and Filter Screen
Note: This should depict a detailed search interface with active filters (price range, store selections, categories) allowing users to narrow down specific products rapidly.

Figure B
Wireframe of Admin Web Dashboard
Note: A desktop-oriented wireframe showing a sidebar navigation and a main content area containing scraping statistics, active scrapers, and voucher management panels.

4.5	Execution 
The implementation of the proposed PricePilot system was carried out using a modular and well-structured full-stack development approach to ensure scalability, high performance, and usability. The mobile frontend was primarily built with React Native and Expo to provide an intuitive, cross-platform user interface that supports real-time interactions. The core backend aggregation engine combines Python with FastAPI for high-performance API delivery and asynchronous web scraping modules to fetch live e-commerce data.

To ensure safe and stable storage, the system employs a PostgreSQL database manipulated asynchronously via `asyncpg`. User authentication and session handling are heavily secured with password hashing algorithms. Throughout the development phases, several tools, APIs, and libraries were utilized. The frontend uses `expo-router` for file-based navigation, making the transition between screens flawless, while `expo-notifications` handles real-time push alerts. The backend relies heavily on `BeautifulSoup` and automation frameworks for accurate data extraction across various e-commerce architectures.

The implementation was carried out in a modular style within dedicated modules: a mobile user interface, an admin web panel, an asynchronous web scraping engine, a database management layer, and an authentication module. This clean separation of concerns simplified communication between layers and ensured maintainability. Strong error-handling mechanisms were established across the board, providing elegant degradation when data parsing fails or network timeouts occur.

4.5.1	System Used Libraries
Figure C
System Used Libraries Code

The development of PricePilot relies on a robust set of modern libraries. On the backend, FastAPI provides the asynchronous framework, while `asyncpg` handles high-speed PostgreSQL database connections. Security features like password hashing are powered by standard cryptographic libraries such as `passlib` and `bcrypt`. The web scraping engine utilizes `httpx` for fast, asynchronous HTTP requests and `BeautifulSoup` for HTML parsing. On the frontend, React Native alongside Expo forms the foundation. Libraries like `@react-navigation` and `expo-router` control the page flows, while `expo-secure-store` safely manages authentication tokens locally on the device.

4.5.2	Configuration & APIs Implementation
Figure D
API & Endpoint Configuration Code

A centralized routing section governs the overall behavior of the PricePilot backend. The system connects specific API endpoints (e.g., `/auth/login`, `/products/search`, `/notifications/alerts`) to their respective database operations. A unique concept implemented in this project is the "Compound ID" system. When a user searches for an item, scrapers may fetch live results that aren't yet stored in the database. The system generates a compound string (e.g., `Daraz-https://...`), allowing the API to transparently handle both database lookups and live-URL scraping on the fly without breaking the mobile routing architecture. 

4.5.3	Testing & Discussion of the System
Unit Testing and User Acceptance Testing (UAT) were heavily utilized to ensure that the system functioned correctly and remained easy to use. Module-level testing was performed to verify each of the core features, especially the web scrapers, ensuring they correctly parsed product titles, prices, and images from different HTML structures. The performance of key mobile functionalities, including login, product search, wishlist additions, and price alert setups, was meticulously evaluated. 

To ensure system robustness, valid and invalid inputs were presented in various test cases. The API successfully caught missing fields and returned proper validation errors without crashing the backend. During UAT, users simulated real-world shopping experiences, confirming that product comparisons were highly accurate and that the UI remained responsive and non-blocking, even while the backend was actively scraping new data. The push notification system correctly triggered when target prices were met, proving that the integration of the database, AI-driven entity resolution, and the mobile interface operated in perfect unison.

4.6	Screenshot
Include the screenshots of the complete end products and provide justification for each.

Figure E
Home Page Dashboard of the System
Note: The Home Page serves as the gateway to the platform's deals. It features an inviting premium brown aesthetic, showcasing the top discounted products and providing immediate access to the search functionality. 
Justification: This screenshot demonstrates the successful integration of the backend aggregation engine with the frontend, proving that live data is correctly formatted and displayed in a user-friendly manner.

Figure F
Product Comparison & Price History Page
Note: This screen displays a specific product, an interactive price history chart, and a sorted list of prices from various Nepalese e-commerce stores.
Justification: This screenshot highlights the core innovation of the PricePilot system. It visually validates the entity resolution algorithm's ability to group identical products from different sources and presents the data clearly to the consumer.

Figure G
Search Results & Filtering Interface
Note: Displays a grid of products based on a user's query, complete with active filters (like store selection or price brackets).
Justification: Shows the responsiveness and depth of the application's search capabilities, crucial for a platform dealing with massive amounts of aggregated data.

Figure H
Push Notification & Price Alerts Prompt
Note: A custom modal interface asking the user for permission to send push notifications regarding price drops.
Justification: Demonstrates the system's focus on user engagement and retention, illustrating how native device features (Push Notifications) are securely and politely requested.

Figure I
Admin Web Dashboard
Note: A desktop view of the administrative control panel, displaying active scrapers, system health statistics, and voucher generation tools.
Justification: Proves that the platform is manageable and scalable, providing system administrators with the necessary tools to monitor scraping activities and user rewards effectively.

4.7 API Endpoints Documentation

The following table outlines the 12 most critical REST API endpoints that drive the core functionality of the PricePilot system. The backend architecture follows a modular approach, categorizing operations by their respective features such as authentication, data scraping, user interactions, and product analysis.

### Core API Summary Table

| API Endpoint | HTTP Method | Primary Purpose |
|---|---|---|
| **/auth/register** | POST | Creates a new user account. |
| **/auth/login** | POST | Authenticates users and issues JWT tokens. |
| **/products/search** | GET | Executes high-performance product searches. |
| **/products/{product_id}** | GET | Retrieves full details for a specific product. |
| **/compare/create** | POST | Generates a new saved product comparison. |
| **/compare/{comparison_id}** | GET | Fetches a detailed specification matrix for a comparison. |
| **/price-history/{product_id}** | GET | Retrieves historical price trends and AI forecasts. |
| **/notifications/alerts** | POST | Registers a custom price drop alert. |
| **/wishlist/add** | POST | Saves a product to the user's wishlist. |
| **/points/balance** | GET | Retrieves the user's current reward points. |
| **/points/redeem** | POST | Exchanges reward points for discount vouchers. |
| **/admin/trigger-scraper** | POST | Manually initiates the live web scraping engine. |

### Detailed API Explanations

#### 1. Authentication APIs
* **`POST /auth/register`**: This endpoint handles new user onboarding. It accepts user details (email, password, name), securely hashes the password using bcrypt, and creates a database record. Upon success, it automatically issues an authentication token.
* **`POST /auth/login`**: The primary gateway for returning users. It validates the provided credentials against the database and, if successful, generates a JSON Web Token (JWT). This token is required in the Authorization header for all subsequent protected requests.

#### 2. Product Discovery & Analysis APIs
* **`GET /products/search`**: One of the most heavily utilized endpoints. It accepts query parameters (keywords, price ranges, categories) and searches the consolidated database across all scraped e-commerce platforms. It returns a paginated list of highly relevant products.
* **`GET /products/{product_id}`**: When a user clicks on a product, this endpoint is called to retrieve its full dataset. This includes the product's title, current price, high-resolution image URLs, specifications, and the exact store it was scraped from.
* **`GET /price-history/{product_id}`**: This endpoint fuels the interactive charts on the frontend. It queries the database for all historical price snapshots of a given product and returns them in a time-series format. It also includes an AI-driven forecast predicting potential future price drops.

#### 3. Comparison Engine APIs
* **`POST /compare/create`**: This endpoint takes an array of product IDs that the user wishes to compare side-by-side. It validates the products, creates a unique comparison session in the database, and returns the session ID.
* **`GET /compare/{comparison_id}`**: Retrieves a previously saved comparison session. It processes the raw product data into a structured "Detailed Matrix", aligning specifications like Warranty, Condition, and Shipping Times so the frontend can render a clean side-by-side table.

#### 4. User Engagement APIs
* **`POST /wishlist/add`**: Allows users to save products they are interested in for later viewing. It creates a relational link between the user's account ID and the product ID in the database.
* **`POST /notifications/alerts`**: Empowers users to set a target price for a specific product. The backend registers this threshold and actively monitors the product during its daily scraping routines. If the price drops below the threshold, a push notification is triggered.

#### 5. Gamification & Rewards APIs
* **`GET /points/balance`**: Queries the gamification engine to return the user's current reward points balance and their lifetime tier status (e.g., Bronze, Silver, Gold).
* **`POST /points/redeem`**: When a user wants to claim a reward, this endpoint verifies they have sufficient points, deducts the points from their balance, and securely generates a unique, single-use discount voucher code for partner stores.

#### 6. Administrative APIs
* **`POST /admin/trigger-scraper`**: A critical backend control mechanism. It allows system administrators to manually dispatch asynchronous web scraping tasks for specific platforms (e.g., Daraz, Hukut) without waiting for the scheduled cron jobs.
