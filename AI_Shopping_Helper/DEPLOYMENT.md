# AI Shopping Helper

## Deployment Instructions

### Phase 1: Development Setup (Local)

#### Prerequisites
- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- Git

#### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Shopping_Helper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up SQLite database (default)**
   The project uses a file-based SQLite database by default. Copy `.env.example` to `.env` and edit `DATABASE_URL` if you want a custom path. Initialize the DB with the provided script:
   ```bash
   python -c "from backend.database.db_connection import init_db; init_db()"
   ```

6. **Initialize database**
   ```bash
   python -c "from backend.database.db_connection import init_db; init_db()"
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

### Phase 2: Production Deployment

#### Option A: DigitalOcean VPS Deployment

1. **Create DigitalOcean Droplet**
   - Ubuntu 22.04 LTS
   - Minimum 2GB RAM, 1 CPU
   - Enable monitoring and backups

2. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3-pip python3-venv nginx -y
   
   # Install Chrome for Selenium
   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
   sudo apt update
   sudo apt install google-chrome-stable -y
   
   # Install Tesseract for OCR
   sudo apt install tesseract-ocr -y
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repository-url> /var/www/ai-shopping-helper
   cd /var/www/ai-shopping-helper
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Set up environment
   cp .env.example .env
   # Edit .env with production values
   
   # Set permissions
   sudo chown -R www-data:www-data /var/www/ai-shopping-helper
   ```

4. **Database**
   No separate database server is required — the app uses SQLite. If you prefer MySQL or another RDBMS for production, set `DATABASE_URL` accordingly and ensure you have the appropriate driver/connector installed.

5. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/ai-shopping-helper
   ```
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
       
       location /static {
           alias /var/www/ai-shopping-helper/frontend/static;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/ai-shopping-helper /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Configure Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/ai-shopping-helper.service
   ```
   ```ini
   [Unit]
   Description=AI Shopping Helper
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/ai-shopping-helper
   Environment=PATH=/var/www/ai-shopping-helper/venv/bin
   ExecStart=/var/www/ai-shopping-helper/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ai-shopping-helper
   sudo systemctl start ai-shopping-helper
   ```

#### Option B: Hostinger Shared Hosting (Frontend Only)

1. **Build Static Frontend**
   ```bash
   # Create static version for shared hosting
   mkdir static-build
   cp -r frontend/* static-build/
   
   # Update API endpoints to point to DigitalOcean VPS
   # Edit static-build/static/js/main.js
   # Change API_BASE_URL to your VPS domain
   ```

2. **Upload to Hostinger**
   - Use File Manager or FTP
   - Upload static-build contents to public_html

### Phase 3: Domain and SSL Setup

1. **Configure Domain**
   - Point domain to DigitalOcean IP
   - Set up DNS records

2. **Install SSL Certificate**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

### Phase 4: Database Population

1. **Run Data Collection Script**
   ```bash
   cd /var/www/ai-shopping-helper
   source venv/bin/activate
   python scripts/data_collector.py
   ```

2. **Set up Cron Jobs for Regular Updates**
   ```bash
   crontab -e
   ```
   ```bash
   # Update product data daily at 2 AM
   0 2 * * * /var/www/ai-shopping-helper/venv/bin/python /var/www/ai-shopping-helper/scripts/data_collector.py
   ```

### Monitoring and Maintenance

1. **Application Monitoring**
   ```bash
   # Check service status
   sudo systemctl status ai-shopping-helper
   
   # View logs
   sudo journalctl -u ai-shopping-helper -f
   
   # Monitor nginx
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Database Backups (SQLite)**
   Create a simple backup script that copies the SQLite file to a timestamped backup location:
   ```bash
   #!/bin/bash
   DB_PATH=/var/www/ai-shopping-helper/data/shopping_assistant.db
   BACKUP_DIR=/backups
   mkdir -p "$BACKUP_DIR"
   cp "$DB_PATH" "$BACKUP_DIR/shopping_assistant_$(date +%Y%m%d_%H%M%S).db"
   find "$BACKUP_DIR" -name "shopping_assistant_*.db" -mtime +7 -delete
   ```

3. **Performance Optimization**
   - Configure nginx caching
   - Configure nginx caching
   - Monitor server resources
   - Set up log rotation

### Scaling Considerations

1. **Database Optimization**
   - Add indexes for frequent queries
   - Consider read replicas for high traffic
   - Implement connection pooling

2. **Application Scaling**
   - Use load balancer for multiple servers
   - Implement Redis caching
   - Consider containerization with Docker

3. **CDN Integration**
   - Use CloudFlare for static assets
   - Image optimization and caching
   - Global content delivery

### Security Checklist

- [ ] Strong database passwords
- [ ] SSL certificate installed
- [ ] Firewall configured (only ports 22, 80, 443)
- [ ] Regular security updates
- [ ] Application security headers
- [ ] Rate limiting implemented
- [ ] Input validation and sanitization
- [ ] Secure session management

### Troubleshooting

**Common Issues:**

1. **Database Connection Errors**
   - Verify `DATABASE_URL` in `.env` and that the SQLite file exists and is writable
   - Check file permissions for the `data/` directory
   - If using an external DB (MySQL/Postgres), ensure the service is running and credentials are correct

2. **Selenium/Chrome Issues**
   - Install missing dependencies
   - Update Chrome version
   - Check display settings for headless mode

3. **OCR Not Working**
   - Install Tesseract properly
   - Check language packs
   - Verify image formats

4. **High Memory Usage**
   - Monitor process memory
   - Implement connection pooling
   - Optimize database queries

**Log Locations:**
- Application logs: `/var/log/ai-shopping-helper/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u ai-shopping-helper`
