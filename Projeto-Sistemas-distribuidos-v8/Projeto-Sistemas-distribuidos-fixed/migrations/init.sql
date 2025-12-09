CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  external_id VARCHAR(128),
  amount NUMERIC(10,2),
  status VARCHAR(40),
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  order_id INTEGER REFERENCES orders(id),
  status VARCHAR(40),
  provider_response JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
  id SERIAL PRIMARY KEY,
  type VARCHAR(64),
  payload JSONB,
  status VARCHAR(40),
  created_at TIMESTAMP DEFAULT now()
);
