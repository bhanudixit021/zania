# README.md
## Zania RESTful API

### Setup and Installation
1. Clone the repository
   ```sh
   git clone git@github.com:bhanudixit021/zania.git
   cd zania
   ```
2. Set environment variables (Required: `APIKEY`)
   ```sh
   export APIKEY="your-api-key"
   ```
3. Build and run using Docker
   ```sh
   docker build -t zania .
   docker run -p 8000:8000 -e APIKEY=$APIKEY zania
   ```
4. Run tests
   ```sh
   docker run -e APIKEY=$APIKEY zania python manage.py test
   ```

### API Endpoints
- `GET /v1/products/` - Retrieve all products (Requires `APIKEY` in headers)
- `POST /v1/products/` - Add a new product (Requires `APIKEY` in headers)
- `POST /v1/orders/` - Place an order (Requires `APIKEY` in headers)

### Environment Variables
**Must-Have:**
- `APIKEY` - Required for authentication.

**Good-to-Have:**
- `DEBUG` - Set to `True` for debugging, `False` for production.
- `DATABASE_URL` - Custom database URL if using PostgreSQL or another DB.
- `LOG_LEVEL` - Define log verbosity (INFO, DEBUG, ERROR).
