-- Star schema built from the orders_clean staging table (see src/etl.py).
-- One fact table (order_items) and three dimensions (customers, products, geography).

DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS geography;

-- ── DIMENSION: customers ────────────────────────────────────────────────
CREATE TABLE customers (
    customer_id   TEXT NOT NULL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment       TEXT NOT NULL
        CHECK(segment IN ('Consumer', 'Corporate', 'Home Office'))
);

INSERT INTO customers
SELECT DISTINCT customer_id, customer_name, segment
FROM orders_clean;

-- ── DIMENSION: products ─────────────────────────────────────────────────
-- MIN() resolves the known product_name variants per product_id
CREATE TABLE products (
    product_id   TEXT NOT NULL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL
        CHECK(category IN ('Furniture', 'Office Supplies', 'Technology')),
    sub_category TEXT NOT NULL
);

INSERT INTO products
SELECT
    product_id,
    MIN(product_name) AS product_name,
    MIN(category)     AS category,
    MIN(sub_category) AS sub_category
FROM orders_clean
GROUP BY product_id;

-- ── DIMENSION: geography ────────────────────────────────────────────────
CREATE TABLE geography (
    postal_code TEXT NOT NULL PRIMARY KEY,
    city        TEXT NOT NULL,
    state       TEXT NOT NULL,
    region      TEXT NOT NULL
        CHECK(region IN ('West', 'East', 'Central', 'South')),
    country     TEXT NOT NULL
);

INSERT INTO geography
SELECT
    postal_code,
    MIN(city)    AS city,
    MIN(state)   AS state,
    MIN(region)  AS region,
    MIN(country) AS country
FROM orders_clean
GROUP BY postal_code;

-- ── FACT: order_items ───────────────────────────────────────────────────
-- Carries the Enrich-step (2.2) derived columns so downstream phases don't
-- have to recompute profit/sales or date parts in every query.
CREATE TABLE order_items (
    row_id         INTEGER NOT NULL PRIMARY KEY,
    order_id       TEXT    NOT NULL,
    customer_id    TEXT    NOT NULL,
    product_id     TEXT    NOT NULL,
    postal_code    TEXT    NOT NULL,
    order_date     TEXT    NOT NULL,
    ship_date      TEXT    NOT NULL,
    ship_mode      TEXT    NOT NULL
        CHECK(ship_mode IN ('Standard Class','Second Class','First Class','Same Day')),
    quantity       INTEGER NOT NULL CHECK(quantity > 0),
    sales          REAL    NOT NULL CHECK(sales >= 0),
    discount       REAL    NOT NULL CHECK(discount >= 0 AND discount <= 1),
    profit         REAL    NOT NULL,
    profit_margin  REAL    NOT NULL,
    ship_lag_days  INTEGER NOT NULL CHECK(ship_lag_days >= 0),
    order_year     INTEGER NOT NULL,
    order_month    INTEGER NOT NULL CHECK(order_month BETWEEN 1 AND 12),
    order_quarter  INTEGER NOT NULL CHECK(order_quarter BETWEEN 1 AND 4),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id),
    FOREIGN KEY (postal_code) REFERENCES geography(postal_code)
);

INSERT INTO order_items
SELECT
    row_id, order_id, customer_id, product_id, postal_code,
    order_date, ship_date, ship_mode,
    quantity, sales, discount, profit,
    profit_margin, ship_lag_days, order_year, order_month, order_quarter
FROM orders_clean;
