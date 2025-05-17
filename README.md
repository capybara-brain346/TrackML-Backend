![ChatGPT Image Apr 26, 2025, 02_40_29 PM](https://github.com/user-attachments/assets/320afee0-1db2-4978-8fc4-28c8e1827e28)
# TrackML

![diagram-export-5-17-2025-10_20_27-PM](https://github.com/user-attachments/assets/6e66b545-5460-4f73-aae8-ded9af9e99c1)

TrackML is a comprehensive tool for tracking and managing machine learning models. It helps users keep track of models they've explored, studied, or plan to use in the future, with powerful features powered by Gemini AI and HuggingFace integration.

## Features

- 📝 Track ML model details including name, developer, type, and parameters
- 🏷️ Organize models with tags and status updates
- 🔍 Search and filter models by various criteria
- 📊 Dashboard view with model statistics and insights
- 🌙 Dark mode support
- 🤖 Auto-fill model information from HuggingFace
- 📈 Model insights and comparative analysis using Gemini AI
- 📱 Responsive design for all devices
- 🔒 Secure authentication system
- 🌐 Cross-Origin Resource Sharing (CORS) enabled
- ☁️ AWS EC2 deployment ready

## Architecture

### Frontend Architecture
- **Framework**: React 18+ with Vite for fast development and building
- **Language**: TypeScript for type safety
- **Styling**: TailwindCSS for utility-first styling
- **Routing**: React Router v6 for client-side navigation
- **State Management**: React Context API
- **API Integration**: Axios for HTTP requests
- **Build Tool**: Vite

### Backend Architecture
- **Framework**: Flask for lightweight and flexible REST API
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: JWT-based authentication
- **API Integration**:
  - Google Gemini API for AI-powered insights
  - HuggingFace API for model information
- **CORS**: Flask-CORS for secure cross-origin requests
- **Environment**: Python 3.8+

### Infrastructure
- **Hosting**: AWS EC2
- **Domain & SSL**: AWS Route 53 & ACM
- **Database**: AWS RDS (Optional)
- **Static Files**: AWS S3 (Optional)

### Nginx Reverse Proxy & Caching

#### Reverse Proxy Configuration
- **Load Balancing**: Round-robin distribution across backend servers
- **SSL Termination**: HTTPS handling at proxy level
- **Header Management**:
  - X-Real-IP forwarding
  - X-Forwarded-For handling
  - Custom header modifications
- **Request Routing**:
  - Path-based routing
  - Subdomain routing
  - WebSocket support

#### Caching Implementation
- **Caching Layers**:
  ```nginx
  proxy_cache_path /path/to/cache levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m use_temp_path=off;
  ```
  - Multi-level cache hierarchy
  - Memory-based caching (10MB zone)
  - Disk-based caching (10GB max)
  - 60-minute cache retention

- **Cache Configuration**:
  - Static asset caching
  - API response caching
  - Cache bypass rules
  - Cache purge mechanisms

- **Cache Control**:
  ```nginx
  location /api/v1/ {
      proxy_cache my_cache;
      proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
      proxy_cache_valid 200 60m;
      proxy_cache_valid 404 1m;
      proxy_cache_key $scheme$request_method$host$request_uri;
  }
  ```
  - Status-based cache rules
  - Method-based caching
  - Custom cache keys
  - Stale cache handling

#### Performance Optimizations
- **Compression**:
  ```nginx
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml;
  gzip_min_length 1000;
  gzip_comp_level 6;
  ```
  - GZIP compression
  - Brotli compression support
  - Compression thresholds
  - Content type filtering

- **Buffer Settings**:
  ```nginx
  client_body_buffer_size 10K;
  client_header_buffer_size 1k;
  client_max_body_size 8m;
  large_client_header_buffers 2 1k;
  ```
  - Request buffering
  - Response buffering
  - Body size limits
  - Header size optimization

- **Connection Handling**:
  ```nginx
  keepalive_timeout 65;
  keepalive_requests 100;
  ```
  - Keep-alive settings
  - Connection pooling
  - Worker processes
  - Event handling

#### Security Measures
- **Rate Limiting**:
  ```nginx
  limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
  ```
  - IP-based limiting
  - Burst handling
  - Zone configuration
  - Custom rate rules

- **Security Headers**:
  ```nginx
  add_header X-Frame-Options "SAMEORIGIN";
  add_header X-XSS-Protection "1; mode=block";
  add_header X-Content-Type-Options "nosniff";
  ```
  - XSS protection
  - CSRF prevention
  - Content sniffing prevention
  - Frame protection

#### Monitoring & Logging
- **Access Logging**:
  ```nginx
  log_format custom '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time';
  ```
  - Custom log formats
  - Error logging
  - Performance logging
  - Debug logging

- **Metrics Collection**:
  - Response time tracking
  - Cache hit/miss ratios
  - Error rate monitoring
  - Bandwidth usage

#### High Availability Setup
- **Failover Configuration**:
  - Backup servers
  - Health checks
  - Automatic failover
  - Load balancing

- **SSL Configuration**:
  ```nginx
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
  ssl_prefer_server_ciphers off;
  ```
  - Modern SSL protocols
  - Strong cipher suites
  - OCSP stapling
  - Session handling

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm/yarn
- AWS Account (for deployment)
- Google Cloud Console Account (for Gemini API)
- HuggingFace Account

### Local Development Setup

#### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TrackML.git
cd TrackML/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Update .env with your credentials:
```
GOOGLE_API_KEY=your_gemini_api_key
HF_ACCESS_TOKEN=your_huggingface_token
FRONTEND_URL=http://localhost:3000
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

6. Run the development server:
```bash
python run.py
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Update .env with your backend URL:
```
VITE_API_URL=http://localhost:5000
```

5. Start development server:
```bash
npm run dev
```

### Production Deployment on AWS EC2

#### EC2 Instance Setup

1. Launch an EC2 instance:
   - Choose Ubuntu Server 22.04 LTS
   - t2.micro for testing, t2.small/medium for production
   - Configure Security Group:
     - SSH (Port 22)
     - HTTP (Port 80)
     - HTTPS (Port 443)
     - Custom TCP (Port 5000) for backend
     - Custom TCP (Port 3000) for frontend

2. Connect to your instance:
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip nodejs npm nginx
```

#### Backend Deployment

1. Clone and setup the application:
```bash
git clone https://github.com/yourusername/TrackML.git
cd TrackML/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Setup Gunicorn:
```bash
pip install gunicorn
```

3. Create systemd service:
```bash
sudo nano /etc/systemd/system/trackml.service
```

Add:
```
[Unit]
Description=TrackML Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TrackML/backend
Environment="PATH=/home/ubuntu/TrackML/backend/venv/bin"
ExecStart=/home/ubuntu/TrackML/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

4. Start the service:
```bash
sudo systemctl start trackml
sudo systemctl enable trackml
```

#### Frontend Deployment

1. Build the frontend:
```bash
cd frontend
npm install
npm run build
```

2. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/trackml
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /home/ubuntu/TrackML/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/trackml /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Project Structure

```
TrackML/
├── backend/
│   ├── models/        # Database models
│   │   └── models.py  # SQLAlchemy models
│   ├── routes/        # API endpoints
│   │   ├── auth_routes.py
│   │   └── model_routes.py
│   ├── services/      # Business logic
│   │   ├── gemini_service.py
│   │   └── huggingface_service.py
│   ├── config.py      # Configuration
│   └── run.py         # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── public/
└── deployment/
    ├── nginx/         # Nginx configuration
    └── systemd/       # Systemd service files
```

## API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user

### Model Endpoints
- `GET /api/v1/models` - List all models
- `GET /api/v1/models/<id>` - Get specific model
- `POST /api/v1/models` - Create new model
- `PUT /api/v1/models/<id>` - Update model
- `DELETE /api/v1/models/<id>` - Delete model
- `GET /api/v1/models/search` - Search models
- `POST /api/v1/models/autofill` - Auto-fill model details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. CORS Issues:
   - Verify FRONTEND_URL in backend .env matches your frontend URL
   - Check CORS configuration in run.py

2. Database Connectivity:
   - Ensure DATABASE_URL is correctly formatted
   - Check database service is running

3. API Key Issues:
   - Verify all API keys are correctly set in .env
   - Check API key permissions and quotas

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini API for AI insights
- HuggingFace for model information
- AWS for hosting infrastructure
