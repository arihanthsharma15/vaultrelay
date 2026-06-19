-- 01-init-customer-db.sql
-- Runs automatically on first Postgres container startup
-- (mounted into /docker-entrypoint-initdb.d/ in docker-compose.yml).
--
-- Creates a SEPARATE database (customer_demo) to simulate "the customer's
-- own database" that Sentry connects to — kept isolated from Guardian's
-- own `vaultrelay` database (audit logs, tenants, api_keys).
--
-- Also creates vaultrelay_ro: a role that can ONLY read customer_demo.
-- It must NOT be able to touch the `vaultrelay` database at all — this
-- is the actual security boundary FR-SENTRY-08 depends on (Sentry refuses
-- to start if its DB user isn't read-only).

CREATE DATABASE customer_demo;

CREATE ROLE vaultrelay_ro WITH LOGIN PASSWORD 'vaultrelay_ro';

GRANT CONNECT ON DATABASE customer_demo TO vaultrelay_ro;

\c customer_demo

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    signup_date DATE NOT NULL,
    country TEXT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount NUMERIC(10, 2) NOT NULL,
    order_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed'
);

INSERT INTO customers (name, email, phone, signup_date, country) VALUES
    ('Asha Mehta',      'asha.mehta@example.com',      '+91-98765-43210', '2023-01-15', 'India'),
    ('Liam O''Connor',  'liam.oconnor@example.com',    '+1-415-555-0182', '2023-02-20', 'USA'),
    ('Priya Raman',     'priya.raman@example.com',     '+91-90000-11122', '2023-03-05', 'India'),
    ('Chen Wei',        'chen.wei@example.com',        '+86-138-0013-8000','2023-04-10', 'China'),
    ('Sofia Ricci',     'sofia.ricci@example.com',     '+39-345-678-9012', '2023-05-18', 'Italy'),
    ('Daniel Kim',      'daniel.kim@example.com',      '+82-10-1234-5678', '2023-06-22', 'South Korea'),
    ('Fatima Noor',     'fatima.noor@example.com',     '+971-50-123-4567', '2023-07-30', 'UAE'),
    ('Lucas Silva',     'lucas.silva@example.com',     '+55-11-91234-5678','2023-08-14', 'Brazil'),
    ('Emma Johansson',  'emma.j@example.com',          '+46-70-123-4567',  '2023-09-02', 'Sweden'),
    ('Arjun Nair',      'arjun.nair@example.com',      '+91-99887-76655',  '2023-10-11', 'India');

INSERT INTO orders (customer_id, amount, order_date, status) VALUES
    (1, 1200.00, '2024-01-05', 'completed'),
    (1,  850.50, '2024-02-10', 'completed'),
    (1, 2300.00, '2024-03-18', 'completed'),
    (2,  430.00, '2024-01-22', 'completed'),
    (3, 1750.00, '2024-02-01', 'completed'),
    (3, 1980.00, '2024-03-09', 'completed'),
    (3,  610.00, '2024-04-15', 'completed'),
    (4,  220.00, '2024-01-30', 'cancelled'),
    (5,  990.00, '2024-02-14', 'completed'),
    (6,  340.00, '2024-03-02', 'completed'),
    (7,  125.00, '2024-01-11', 'completed'),
    (8,  500.00, '2024-02-28', 'completed'),
    (9,  675.00, '2024-03-21', 'completed'),
    (10, 1100.00, '2024-04-02', 'completed');

GRANT USAGE ON SCHEMA public TO vaultrelay_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vaultrelay_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO vaultrelay_ro;

SELECT 'customers' AS table_name, count(*) AS rows FROM customers
UNION ALL
SELECT 'orders', count(*) FROM orders;
