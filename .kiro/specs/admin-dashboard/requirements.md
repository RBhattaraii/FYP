# Requirements Document

## Introduction

The Admin Dashboard feature provides system administrators with comprehensive visibility into platform metrics, user activity, product inventory, scraper operations, and store performance. This feature extends the existing mobile application with a new admin-only tab and implements secure authentication using environment-based credentials.

## Glossary

- **Admin_User**: A user with administrative privileges who can access system-wide metrics and controls
- **Mobile_App**: The React Native/Expo-based mobile application that serves as the primary user interface
- **Backend_API**: The FastAPI-based server that processes requests and manages data
- **Admin_Tab**: A new navigation tab in the bottom tab bar dedicated to administrative functions
- **Dashboard_Screen**: The main administrative interface displaying system metrics and controls
- **Environment_Credentials**: Authentication credentials stored in the .env file (ADMIN_USERNAME, ADMIN_PASSWORD)
- **Total_Products_Metric**: The count of all products currently stored in the system
- **Category_Breakdown_Metric**: Distribution of products across different product categories
- **Store_Distribution_Metric**: Distribution of products across different online stores
- **Scraper_Status_Metric**: Current operational status and health of web scraping services
- **Tab_Navigation**: The bottom navigation bar containing tabs for different app sections
- **Authentication_Flow**: The process of verifying admin credentials before granting access
- **Dashboard_Component**: A reusable UI component displaying a specific metric or data visualization

## Requirements

### Requirement 1: Admin Authentication

**User Story:** As a system administrator, I want to securely authenticate using environment-based credentials, so that only authorized personnel can access administrative functions.

#### Acceptance Criteria

1.1. THE Backend_API SHALL store admin credentials in environment variables named ADMIN_USERNAME and ADMIN_PASSWORD

1.2. WHEN an Admin_User enters credentials on the login screen, THE Backend_API SHALL validate the credentials against the environment variables

1.3. IF the provided credentials match the environment variables, THEN THE Backend_API SHALL issue a valid JWT token with admin role

1.4. IF the provided credentials do not match the environment variables, THEN THE Backend_API SHALL return an authentication error within 500 milliseconds

1.5. THE Backend_API SHALL not expose admin credentials in API responses, logs, or error messages

1.6. WHEN an Admin_User attempts to access admin endpoints without a valid admin token, THE Backend_API SHALL return HTTP 403 Forbidden status

### Requirement 2: Admin Tab Navigation

**User Story:** As a system administrator, I want a dedicated admin tab in the bottom navigation, so that I can quickly access administrative functions.

#### Acceptance Criteria

2.1. THE Mobile_App SHALL add an Admin_Tab to the Tab_Navigation as the sixth tab

2.2. THE Admin_Tab SHALL display a shield icon (Ionicons shield-outline when inactive, shield when active)

2.3. THE Admin_Tab SHALL use the theme's warningOrange color when active

2.4. WHEN an Admin_User is authenticated, THE Admin_Tab SHALL be visible in the Tab_Navigation

2.5. WHEN a non-admin user is authenticated, THE Admin_Tab SHALL not be visible in the Tab_Navigation

2.6. WHEN the Admin_User taps the Admin_Tab, THE Mobile_App SHALL navigate to the Dashboard_Screen

### Requirement 3: Total Products Display

**User Story:** As a system administrator, I want to view the total number of products in the system, so that I can monitor inventory size.

#### Acceptance Criteria

3.1. THE Backend_API SHALL calculate the Total_Products_Metric by counting all rows in the products table

3.2. THE Backend_API SHALL return the Total_Products_Metric in the dashboard endpoint response

3.3. THE Dashboard_Screen SHALL display the Total_Products_Metric with a label "Total Products"

3.4. THE Dashboard_Component SHALL format numbers greater than 999 with comma separators

3.5. WHEN the Total_Products_Metric is zero, THE Dashboard_Screen SHALL display "0" without showing an error state

### Requirement 4: Category Breakdown Display

**User Story:** As a system administrator, I want to view product distribution across categories, so that I can understand inventory composition.

#### Acceptance Criteria

4.1. THE Backend_API SHALL calculate the Category_Breakdown_Metric by grouping products by category and counting each group

4.2. THE Backend_API SHALL return the Category_Breakdown_Metric as an array of category names with their product counts

4.3. THE Dashboard_Screen SHALL display the Category_Breakdown_Metric using a visual chart component

4.4. THE Dashboard_Component SHALL display category names and their corresponding product counts

4.5. THE Dashboard_Component SHALL sort categories by product count in descending order

4.6. WHEN a category has zero products, THE Backend_API SHALL exclude that category from the Category_Breakdown_Metric

4.7. THE Dashboard_Screen SHALL display the top 10 categories by product count

### Requirement 5: Store Distribution Display

**User Story:** As a system administrator, I want to view product distribution across stores, so that I can monitor data source coverage.

#### Acceptance Criteria

5.1. THE Backend_API SHALL calculate the Store_Distribution_Metric by grouping products by store_name and counting each group

5.2. THE Backend_API SHALL return the Store_Distribution_Metric as an array of store names with their product counts

5.3. THE Dashboard_Screen SHALL display the Store_Distribution_Metric using a visual chart component

5.4. THE Dashboard_Component SHALL display store names and their corresponding product counts

5.5. THE Dashboard_Component SHALL sort stores by product count in descending order

5.6. WHEN a store has zero products, THE Backend_API SHALL exclude that store from the Store_Distribution_Metric

5.7. THE Dashboard_Screen SHALL display all stores that have at least one product

### Requirement 6: Scraper Status Display

**User Story:** As a system administrator, I want to view the operational status of all scrapers, so that I can ensure data collection is functioning correctly.

#### Acceptance Criteria

6.1. THE Backend_API SHALL calculate the Scraper_Status_Metric by checking the last_scrape_time for each store in the scrape_metadata table

6.2. THE Backend_API SHALL classify scraper status as "active" when last_scrape_time is within 48 hours of the current time

6.3. THE Backend_API SHALL classify scraper status as "stale" when last_scrape_time is older than 48 hours

6.4. THE Backend_API SHALL classify scraper status as "inactive" when no scrape_metadata record exists for a store

6.5. THE Backend_API SHALL return the Scraper_Status_Metric as an array containing store names, their status, and last_scrape_time

6.6. THE Dashboard_Screen SHALL display each scraper with its store name, current status, and last successful scrape timestamp

6.7. THE Dashboard_Component SHALL use green color for "active" status, yellow for "stale" status, and red for "inactive" status

6.8. THE Dashboard_Screen SHALL format timestamps in relative time format (e.g., "2 hours ago", "3 days ago")

### Requirement 7: Admin Access Control

**User Story:** As a system administrator, I want admin functions to be restricted to authorized users only, so that system security is maintained.

#### Acceptance Criteria

7.1. THE Backend_API SHALL verify admin role for all requests to admin endpoints

7.2. WHEN a request to an admin endpoint contains a non-admin token, THE Backend_API SHALL return HTTP 403 Forbidden status

7.3. WHEN a request to an admin endpoint contains an invalid or expired token, THE Backend_API SHALL return HTTP 401 Unauthorized status

7.4. THE Mobile_App SHALL clear admin authentication state when the JWT token expires

7.5. WHEN admin authentication expires, THE Mobile_App SHALL redirect the Admin_User to the admin login screen

7.6. THE Mobile_App SHALL store admin authentication tokens securely using expo-secure-store

### Requirement 8: Dashboard Data Refresh

**User Story:** As a system administrator, I want to refresh dashboard metrics on demand, so that I can view the most current data.

#### Acceptance Criteria

8.1. THE Dashboard_Screen SHALL display a refresh button in the header

8.2. WHEN the Admin_User taps the refresh button, THE Mobile_App SHALL request updated metrics from the Backend_API

8.3. WHEN the refresh request is in progress, THE Dashboard_Screen SHALL display a loading indicator

8.4. WHEN the refresh request completes successfully, THE Dashboard_Screen SHALL update all displayed metrics

8.5. WHEN the refresh request fails, THE Dashboard_Screen SHALL display an error message and retain the previous metric values

8.6. THE Dashboard_Screen SHALL automatically refresh metrics when the screen gains focus

8.7. THE Backend_API SHALL respond to dashboard metric requests within 2 seconds

### Requirement 9: Dashboard Performance

**User Story:** As a system administrator, I want the dashboard to load quickly, so that I can access information without delays.

#### Acceptance Criteria

9.1. THE Backend_API SHALL execute all dashboard metric queries in parallel

9.2. THE Backend_API SHALL cache dashboard metrics for 60 seconds to reduce database load

9.3. THE Backend_API SHALL return cached metrics when a request occurs within the cache validity period

9.4. THE Backend_API SHALL calculate fresh metrics when the cache has expired

9.5. THE Dashboard_Screen SHALL display a skeleton loading state while fetching initial metrics

9.6. THE Mobile_App SHALL cache dashboard metrics locally for offline viewing

9.7. WHEN the Mobile_App is offline, THE Dashboard_Screen SHALL display cached metrics with a "Last updated" timestamp

### Requirement 10: Admin Login Screen

**User Story:** As a system administrator, I want a dedicated login screen for admin access, so that I can authenticate separately from regular users.

#### Acceptance Criteria

10.1. THE Mobile_App SHALL provide an admin login screen separate from the user login screen

10.2. THE admin login screen SHALL contain input fields for username and password

10.3. THE admin login screen SHALL display "Admin Login" as the screen title

10.4. WHEN the Admin_User submits credentials, THE Mobile_App SHALL send an authentication request to the Backend_API admin login endpoint

10.5. WHEN authentication succeeds, THE Mobile_App SHALL store the admin token securely and navigate to the Dashboard_Screen

10.6. WHEN authentication fails, THE admin login screen SHALL display an error message "Invalid admin credentials"

10.7. THE admin login screen SHALL mask password input characters

10.8. THE admin login screen SHALL disable the login button while authentication is in progress
