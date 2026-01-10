# SafeRide - Capstone Project

## Overview
SafeRide is a ride-sharing and logistics platform designed to connect users with safe and reliable transportation options. The system features real-time tracking, secure messaging with translation, and an intuitive dashboard for managing rides.

## Key Features Implemented

### 1. User Authentication & Management
- **Registration & Login**: Secure user onboarding with JWT authentication.
- **Role Management**: Support for different user roles (Client, Driver/CabRider, Motorcyclist).
- **Profile Management**: Settings page to update user details and password.

### 2. Interactive Dashboard
- **Google Maps Integration**: Real-time map visualization using Google Maps API.
- **Geolocation**: Automatic detection of user's current location.
- **Driver Visualization**: Real-time display of nearby drivers on the map.
- **Route Calculation**: Distance and duration estimation between pickup and drop-off points.

### 3. Ride Ordering System
- **Instant Booking**: "Find Ride" functionality that creates orders immediately.
- **Driver Matching**: Algorithm to find the nearest available driver based on vehicle type (Car/Moto).
- **Pending Orders**: Support for creating orders even when no drivers are currently available (queued for later).
- **Order Tracking**: Dedicated "My Orders" page to view current and past ride requests.

### 4. Real-Time Communication (Chat)
- **WebSocket Integration**: Seamless real-time messaging using Django Channels.
- **Live Translation**: Integrated Google Cloud Translation API to automatically translate messages between English and Kinyarwanda.
- **Online Status**: Dynamic tracking of online users.
- **Responsive Design**: Mobile-friendly chat interface with sidebar toggles.

## Technology Stack

### Backend
- **Framework**: Django & Django REST Framework (DRF)
- **Real-time**: Django Channels (WebSockets)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Authentication**: JWT (JSON Web Tokens) via `simplejwt`

### Frontend
- **Templating**: Django Templates (Server-Side Rendering)
- **Styling**: Tailwind CSS (via CDN)
- **Scripting**: Vanilla JavaScript (ES6+) with Async/Await patterns
- **Maps**: Google Maps JavaScript API (Places, Directions, Geocoding)

## Project Structure

```
saferide/
├── api/                  # Core application logic
│   ├── migrations/       # Database migrations
│   ├── static/           # Static assets (images, CSS, JS)
│   ├── templates/        # HTML Templates
│   │   ├── components/   # Reusable UI components (navbar, sidebar)
│   │   ├── chat.html     # Real-time chat interface
│   │   ├── dashboard.html# Main map & booking interface
│   │   ├── orders.html   # Order history view
│   │   └── ...
│   ├── consumers.py      # WebSocket consumers (Chat logic)
│   ├── models.py         # Database models (User, Chat, Order)
│   ├── views.py          # API Views & Controllers
│   └── urls.py           # API Route definitions
├── saferide/             # Project configuration
│   ├── settings.py       # Global settings (Apps, DB, Keys)
│   └── asgi.py           # ASGI config for Channels
└── manage.py             # Django CLI entry point
```

## Recent Updates (Development Log)
- **Fixed Chat Connectivity**: Resolved issues with user selection in the chat sidebar not triggering the chat window.
- **Enhanced Order Creation**: Updated the booking logic to allow order creation even without immediate driver availability.
- **Order Visibility**: Fixed the Orders page to correctly display requests for both senders and receivers.
- **Translation**: Successfully integrated Google Cloud Translate for cross-language communication.

## Setup Instructions
1. **Environment Variables**: Ensure `.env` contains:
   - `GOOGLE_MAPS_API_KEY`
   - `GOOGLE_APPLICATION_CREDENTIALS` (JSON file path)
   - `SECRET_KEY`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Run Migrations**: `python manage.py migrate`
4. **Start Server**: `python manage.py runserver`
