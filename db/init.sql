CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE NOT NULL,
    year INT,
    make VARCHAR(50),
    model VARCHAR(50),
    trim VARCHAR(50),
    price INT,
    miles INT,
    dealer_name VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);