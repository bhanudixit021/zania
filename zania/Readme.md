## Zania RESTful API

### Setup and Installation
1. Clone the repository
   ```sh
   git clone <repo-url>
   cd zania
   ```
2. Build and run using Docker
   ```sh
   docker build -t zania .
   docker run -p 8000:8000 zania
   ```
3. Run tests
   ```sh
   docker run zania python manage.py test
   ```

### API Endpoints
- `GET /products/` - Retrieve all products
- `POST /products/` - Add a new product
- `POST /orders/` - Place an order
