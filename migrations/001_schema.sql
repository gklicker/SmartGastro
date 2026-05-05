-- =============================================================
-- SmartGastro – Schema inicial
-- Migración: 001_schema.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS smartgastro
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smartgastro;

-- -------------------------------------------------------------
-- СПРАВОЧНИКИ
-- -------------------------------------------------------------

CREATE TABLE roles (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE units (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE   -- g, kg, l, pcs
);

CREATE TABLE payment_methods (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE   -- cash, card, mercadopago
);

CREATE TABLE cancellation_reasons (
    id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- -------------------------------------------------------------
-- ПОЛЬЗОВАТЕЛИ И ФУДТРАКИ
-- -------------------------------------------------------------

CREATE TABLE users (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    login         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    role_id       INT UNSIGNED NOT NULL,
    active        TINYINT(1)   NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE foodtrucks (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    description   TEXT,
    license_plate VARCHAR(20),
    active        TINYINT(1)  NOT NULL DEFAULT 1,
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_foodtruck (
    user_id      INT UNSIGNED NOT NULL,
    foodtruck_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (user_id, foodtruck_id),
    CONSTRAINT fk_uf_user      FOREIGN KEY (user_id)      REFERENCES users(id),
    CONSTRAINT fk_uf_foodtruck FOREIGN KEY (foodtruck_id) REFERENCES foodtrucks(id)
);

-- -------------------------------------------------------------
-- ИНГРЕДИЕНТЫ И МЕНЮ
-- -------------------------------------------------------------

CREATE TABLE ingredients (
    id               INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(150)   NOT NULL,
    unit_id          INT UNSIGNED   NOT NULL,
    min_stock_alert  DECIMAL(10,3)  NOT NULL DEFAULT 0,
    CONSTRAINT fk_ingredients_unit FOREIGN KEY (unit_id) REFERENCES units(id)
);

CREATE TABLE menu_items (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150)  NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    description TEXT,
    active      TINYINT(1)    NOT NULL DEFAULT 1
);

-- Унифицированная таблица: простые товары (1 строка) и рецепты (N строк)
CREATE TABLE menu_item_ingredients (
    menu_item_id  INT UNSIGNED  NOT NULL,
    ingredient_id INT UNSIGNED  NOT NULL,
    quantity      DECIMAL(10,3) NOT NULL,
    PRIMARY KEY (menu_item_id, ingredient_id),
    CONSTRAINT fk_mii_menu       FOREIGN KEY (menu_item_id)  REFERENCES menu_items(id),
    CONSTRAINT fk_mii_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

-- -------------------------------------------------------------
-- СКЛАД
-- -------------------------------------------------------------

CREATE TABLE warehouses (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    address     VARCHAR(255),
    description TEXT
);

CREATE TABLE warehouse_stock (
    id            INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    warehouse_id  INT UNSIGNED  NOT NULL,
    ingredient_id INT UNSIGNED  NOT NULL,
    quantity      DECIMAL(10,3) NOT NULL DEFAULT 0,
    UNIQUE KEY uq_wh_ingredient (warehouse_id, ingredient_id),
    CONSTRAINT fk_whs_warehouse  FOREIGN KEY (warehouse_id)  REFERENCES warehouses(id),
    CONSTRAINT fk_whs_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

CREATE TABLE foodtruck_stock (
    id            INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    foodtruck_id  INT UNSIGNED  NOT NULL,
    ingredient_id INT UNSIGNED  NOT NULL,
    quantity      DECIMAL(10,3) NOT NULL DEFAULT 0,
    UNIQUE KEY uq_ft_ingredient (foodtruck_id, ingredient_id),
    CONSTRAINT fk_fts_foodtruck  FOREIGN KEY (foodtruck_id)  REFERENCES foodtrucks(id),
    CONSTRAINT fk_fts_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

-- Поступление от поставщика (либо на склад, либо на фудтрак)
CREATE TABLE stock_entries (
    id            INT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
    warehouse_id  INT UNSIGNED   NULL,
    foodtruck_id  INT UNSIGNED   NULL,
    ingredient_id INT UNSIGNED   NOT NULL,
    quantity      DECIMAL(10,3)  NOT NULL,
    unit_cost     DECIMAL(10,2)  NOT NULL,
    total_cost    DECIMAL(10,2)  GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    supplier_name VARCHAR(150)   NOT NULL,
    received_by   INT UNSIGNED   NOT NULL,
    received_at   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes         TEXT,
    CONSTRAINT fk_se_warehouse  FOREIGN KEY (warehouse_id)  REFERENCES warehouses(id),
    CONSTRAINT fk_se_foodtruck  FOREIGN KEY (foodtruck_id)  REFERENCES foodtrucks(id),
    CONSTRAINT fk_se_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
    CONSTRAINT fk_se_user       FOREIGN KEY (received_by)   REFERENCES users(id),
    CONSTRAINT chk_se_location  CHECK (
        (warehouse_id IS NOT NULL AND foodtruck_id IS NULL) OR
        (warehouse_id IS NULL     AND foodtruck_id IS NOT NULL)
    )
);

-- Перемещение между складами / фудтраками
CREATE TABLE stock_movements (
    id                INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    from_warehouse_id INT UNSIGNED  NULL,
    from_foodtruck_id INT UNSIGNED  NULL,
    to_warehouse_id   INT UNSIGNED  NULL,
    to_foodtruck_id   INT UNSIGNED  NULL,
    ingredient_id     INT UNSIGNED  NOT NULL,
    quantity          DECIMAL(10,3) NOT NULL,
    moved_by          INT UNSIGNED  NOT NULL,
    moved_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes             TEXT,
    CONSTRAINT fk_sm_from_wh  FOREIGN KEY (from_warehouse_id) REFERENCES warehouses(id),
    CONSTRAINT fk_sm_from_ft  FOREIGN KEY (from_foodtruck_id) REFERENCES foodtrucks(id),
    CONSTRAINT fk_sm_to_wh    FOREIGN KEY (to_warehouse_id)   REFERENCES warehouses(id),
    CONSTRAINT fk_sm_to_ft    FOREIGN KEY (to_foodtruck_id)   REFERENCES foodtrucks(id),
    CONSTRAINT fk_sm_ingr     FOREIGN KEY (ingredient_id)     REFERENCES ingredients(id),
    CONSTRAINT fk_sm_user     FOREIGN KEY (moved_by)          REFERENCES users(id),
    CONSTRAINT chk_sm_from    CHECK (from_warehouse_id IS NOT NULL OR from_foodtruck_id IS NOT NULL),
    CONSTRAINT chk_sm_to      CHECK (to_warehouse_id   IS NOT NULL OR to_foodtruck_id   IS NOT NULL)
);

-- -------------------------------------------------------------
-- СОБЫТИЯ
-- -------------------------------------------------------------

CREATE TABLE events (
    id                     INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name                   VARCHAR(150) NOT NULL,
    address                VARCHAR(255),
    date_start             DATETIME     NOT NULL,
    date_end               DATETIME     NOT NULL,
    status                 ENUM('planned','ongoing','completed','cancelled') NOT NULL DEFAULT 'planned',
    cancellation_reason_id INT UNSIGNED NULL,
    cancellation_comment   TEXT,
    created_by             INT UNSIGNED NOT NULL,
    created_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ev_reason     FOREIGN KEY (cancellation_reason_id) REFERENCES cancellation_reasons(id),
    CONSTRAINT fk_ev_created_by FOREIGN KEY (created_by)             REFERENCES users(id)
);

CREATE TABLE event_foodtrucks (
    event_id     INT UNSIGNED NOT NULL,
    foodtruck_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (event_id, foodtruck_id),
    CONSTRAINT fk_evft_event     FOREIGN KEY (event_id)     REFERENCES events(id),
    CONSTRAINT fk_evft_foodtruck FOREIGN KEY (foodtruck_id) REFERENCES foodtrucks(id)
);

-- -------------------------------------------------------------
-- ПРОДАЖИ
-- -------------------------------------------------------------

CREATE TABLE receipts (
    id                INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    foodtruck_id      INT UNSIGNED  NOT NULL,
    cashier_id        INT UNSIGNED  NOT NULL,
    event_id          INT UNSIGNED  NULL,
    payment_method_id INT UNSIGNED  NOT NULL,
    status            ENUM('open','closed','cancelled','refunded') NOT NULL DEFAULT 'open',
    total_amount      DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at         DATETIME      NULL,
    CONSTRAINT fk_rc_foodtruck FOREIGN KEY (foodtruck_id)      REFERENCES foodtrucks(id),
    CONSTRAINT fk_rc_cashier   FOREIGN KEY (cashier_id)        REFERENCES users(id),
    CONSTRAINT fk_rc_event     FOREIGN KEY (event_id)          REFERENCES events(id),
    CONSTRAINT fk_rc_payment   FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
);

CREATE TABLE receipt_items (
    id           INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    receipt_id   INT UNSIGNED  NOT NULL,
    menu_item_id INT UNSIGNED  NOT NULL,
    quantity     INT UNSIGNED  NOT NULL DEFAULT 1,
    unit_price   DECIMAL(10,2) NOT NULL,
    subtotal     DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    CONSTRAINT fk_ri_receipt   FOREIGN KEY (receipt_id)   REFERENCES receipts(id),
    CONSTRAINT fk_ri_menu_item FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);
