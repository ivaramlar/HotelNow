# Hotel and Car Recommendation System

This project is a web application built with Django that provides a collaborative recommendation system for hotels, alongside a search and query interface for both hotels and cars. The platform allows users to explore hotels and cars, perform detailed searches using Whoosh-based indices, and receive personalized hotel recommendations based on user ratings and content similarities.

## Features

### Hotel Recommendations
- **Collaborative Filtering:** Recommend hotels based on user-provided ratings and the similarity of other users' preferences.
- **Content-Based Filtering:** Recommend hotels using features like price, surface area, number of rooms, and bathrooms.

### Car Search
- Fetch and display car listings scraped from MercadoLibre, allowing users to browse and search by:
  - **Brand**
  - **Price**
  - **Description**

### Hotel Search
- Fetch and display hotel listings scraped from Tecnocasa, enabling users to:
  - Search hotels by title or description using a Whoosh-based search engine.
  - Filter hotels based on price, type, and other features.

### Admin Dashboard
- Add, edit, or delete hotels, car brands, and car details via the Django admin panel.

### Custom Features
- **Web Scraping:** Extract real-time car and hotel data from external sources using BeautifulSoup.
- **Recommendation Engine:** Implemented using custom mathematical functions (e.g., Pearson correlation and Cosine similarity).
- **Search Engine Integration:** Facilitate fast and efficient searches through Whoosh.

## Tools and Technologies
- **Backend:** Django with SQLite for database management.
- **Frontend:** HTML, CSS, and Django templates for UI rendering.
- **Web Scraping:** BeautifulSoup for data extraction from MercadoLibre and Tecnocasa.
- **Search Engine:** Whoosh for indexing and querying hotel and car data.
- **Recommendation Algorithms:** Custom Python functions for calculating similarities and generating recommendations.

## How to Use
1. **Set up the Virtual Environment**: Activate the virtual environment using:
   ```bash
   source myvenv/bin/activate
