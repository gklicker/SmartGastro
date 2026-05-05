-- =============================================================
-- SmartGastro – Хранимые процедуры
-- Migración: 003_procedures.sql
-- =============================================================

USE smartgastro;

DELIMITER $$

-- -------------------------------------------------------------
-- sp_add_menu_item
-- Crea una nueva posición de menú con sus ingredientes.
-- IN:  p_name        VARCHAR  – nombre del plato
--      p_price       DECIMAL  – precio de venta
--      p_description TEXT     – descripción (puede ser NULL)
--      p_ingredients JSON     – [{"ingredient_id":1,"quantity":200}, ...]
-- OUT: p_new_id      INT      – id del menu_item creado
--      p_error       VARCHAR  – mensaje de error, NULL si OK
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_add_menu_item $$
CREATE PROCEDURE sp_add_menu_item(
    IN  p_name        VARCHAR(150),
    IN  p_price       DECIMAL(10,2),
    IN  p_description TEXT,
    IN  p_ingredients JSON,
    OUT p_new_id      INT,
    OUT p_error       VARCHAR(255)
)
BEGIN
    DECLARE v_i         INT DEFAULT 0;
    DECLARE v_count     INT;
    DECLARE v_ingr_id   INT;
    DECLARE v_qty       DECIMAL(10,3);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 p_error = MESSAGE_TEXT;
        SET p_new_id = NULL;
    END;

    SET p_error = NULL;

    IF p_name IS NULL OR TRIM(p_name) = '' THEN
        SET p_error = 'El nombre del plato no puede estar vacío';
        SET p_new_id = NULL;
        LEAVE sp_add_menu_item;
    END IF;

    IF p_price IS NULL OR p_price <= 0 THEN
        SET p_error = 'El precio debe ser mayor a cero';
        SET p_new_id = NULL;
        LEAVE sp_add_menu_item;
    END IF;

    IF JSON_LENGTH(p_ingredients) = 0 THEN
        SET p_error = 'El plato debe tener al menos un ingrediente';
        SET p_new_id = NULL;
        LEAVE sp_add_menu_item;
    END IF;

    START TRANSACTION;

    INSERT INTO menu_items (name, price, description, active)
    VALUES (TRIM(p_name), p_price, p_description, 1);

    SET p_new_id = LAST_INSERT_ID();

    SET v_count = JSON_LENGTH(p_ingredients);
    WHILE v_i < v_count DO
        SET v_ingr_id = JSON_UNQUOTE(JSON_EXTRACT(p_ingredients, CONCAT('$[', v_i, '].ingredient_id')));
        SET v_qty     = JSON_UNQUOTE(JSON_EXTRACT(p_ingredients, CONCAT('$[', v_i, '].quantity')));

        IF NOT EXISTS (SELECT 1 FROM ingredients WHERE id = v_ingr_id) THEN
            SET p_error = CONCAT('Ingrediente no encontrado: ', v_ingr_id);
            ROLLBACK;
            SET p_new_id = NULL;
            LEAVE sp_add_menu_item;
        END IF;

        INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity)
        VALUES (p_new_id, v_ingr_id, v_qty);

        SET v_i = v_i + 1;
    END WHILE;

    COMMIT;
END$$


-- -------------------------------------------------------------
-- sp_update_event_status
-- Cambia el estado de un evento; si se cancela, exige razón.
-- IN:  p_event_id    INT
--      p_status      ENUM  – planned | ongoing | completed | cancelled
--      p_reason_id   INT   – id de cancellation_reasons (solo si cancelled)
--      p_comment     TEXT  – comentario libre
--      p_user_id     INT   – usuario que realiza el cambio
-- OUT: p_error       VARCHAR
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_update_event_status $$
CREATE PROCEDURE sp_update_event_status(
    IN  p_event_id  INT,
    IN  p_status    VARCHAR(20),
    IN  p_reason_id INT,
    IN  p_comment   TEXT,
    IN  p_user_id   INT,
    OUT p_error     VARCHAR(255)
)
BEGIN
    DECLARE v_current_status VARCHAR(20);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 p_error = MESSAGE_TEXT;
    END;

    SET p_error = NULL;

    SELECT status INTO v_current_status FROM events WHERE id = p_event_id;

    IF v_current_status IS NULL THEN
        SET p_error = CONCAT('Evento no encontrado: ', p_event_id);
        LEAVE sp_update_event_status;
    END IF;

    IF v_current_status = 'completed' OR v_current_status = 'cancelled' THEN
        SET p_error = CONCAT('No se puede modificar un evento en estado: ', v_current_status);
        LEAVE sp_update_event_status;
    END IF;

    IF p_status = 'cancelled' AND p_reason_id IS NULL THEN
        SET p_error = 'Se requiere una razón de cancelación';
        LEAVE sp_update_event_status;
    END IF;

    IF p_status = 'cancelled' AND NOT EXISTS (SELECT 1 FROM cancellation_reasons WHERE id = p_reason_id) THEN
        SET p_error = CONCAT('Razón de cancelación no encontrada: ', p_reason_id);
        LEAVE sp_update_event_status;
    END IF;

    START TRANSACTION;

    UPDATE events
    SET
        status                 = p_status,
        cancellation_reason_id = IF(p_status = 'cancelled', p_reason_id, NULL),
        cancellation_comment   = IF(p_status = 'cancelled', p_comment, cancellation_comment)
    WHERE id = p_event_id;

    COMMIT;
END$$


-- -------------------------------------------------------------
-- sp_register_stock_entry
-- Registra la recepción de ingredientes de un proveedor
-- y actualiza el stock correspondiente.
-- IN:  p_warehouse_id  INT      – NULL si destino es foodtruck
--      p_foodtruck_id  INT      – NULL si destino es warehouse
--      p_ingredient_id INT
--      p_quantity      DECIMAL
--      p_unit_cost     DECIMAL
--      p_supplier_name VARCHAR
--      p_received_by   INT      – user_id
--      p_notes         TEXT
-- OUT: p_entry_id      INT      – id del registro creado
--      p_error         VARCHAR
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_register_stock_entry $$
CREATE PROCEDURE sp_register_stock_entry(
    IN  p_warehouse_id  INT,
    IN  p_foodtruck_id  INT,
    IN  p_ingredient_id INT,
    IN  p_quantity      DECIMAL(10,3),
    IN  p_unit_cost     DECIMAL(10,2),
    IN  p_supplier_name VARCHAR(150),
    IN  p_received_by   INT,
    IN  p_notes         TEXT,
    OUT p_entry_id      INT,
    OUT p_error         VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 p_error = MESSAGE_TEXT;
        SET p_entry_id = NULL;
    END;

    SET p_error = NULL;

    IF (p_warehouse_id IS NULL AND p_foodtruck_id IS NULL) OR
       (p_warehouse_id IS NOT NULL AND p_foodtruck_id IS NOT NULL) THEN
        SET p_error = 'Debe especificarse exactamente un destino: warehouse o foodtruck';
        SET p_entry_id = NULL;
        LEAVE sp_register_stock_entry;
    END IF;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        SET p_error = 'La cantidad debe ser mayor a cero';
        SET p_entry_id = NULL;
        LEAVE sp_register_stock_entry;
    END IF;

    IF p_supplier_name IS NULL OR TRIM(p_supplier_name) = '' THEN
        SET p_error = 'El nombre del proveedor no puede estar vacío';
        SET p_entry_id = NULL;
        LEAVE sp_register_stock_entry;
    END IF;

    START TRANSACTION;

    INSERT INTO stock_entries
        (warehouse_id, foodtruck_id, ingredient_id, quantity, unit_cost, supplier_name, received_by, notes)
    VALUES
        (p_warehouse_id, p_foodtruck_id, p_ingredient_id, p_quantity, p_unit_cost, p_supplier_name, p_received_by, p_notes);

    SET p_entry_id = LAST_INSERT_ID();

    -- Actualizar stock según destino
    IF p_warehouse_id IS NOT NULL THEN
        INSERT INTO warehouse_stock (warehouse_id, ingredient_id, quantity)
        VALUES (p_warehouse_id, p_ingredient_id, p_quantity)
        ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;
    ELSE
        INSERT INTO foodtruck_stock (foodtruck_id, ingredient_id, quantity)
        VALUES (p_foodtruck_id, p_ingredient_id, p_quantity)
        ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;
    END IF;

    COMMIT;
END$$


-- -------------------------------------------------------------
-- sp_move_stock
-- Mueve una cantidad de ingrediente entre dos ubicaciones
-- (warehouse ↔ warehouse | warehouse ↔ foodtruck | foodtruck ↔ foodtruck).
-- IN:  p_from_warehouse_id  INT  – NULL si origen es foodtruck
--      p_from_foodtruck_id  INT  – NULL si origen es warehouse
--      p_to_warehouse_id    INT  – NULL si destino es foodtruck
--      p_to_foodtruck_id    INT  – NULL si destino es warehouse
--      p_ingredient_id      INT
--      p_quantity           DECIMAL
--      p_moved_by           INT  – user_id
--      p_notes              TEXT
-- OUT: p_movement_id        INT
--      p_error              VARCHAR
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_move_stock $$
CREATE PROCEDURE sp_move_stock(
    IN  p_from_warehouse_id INT,
    IN  p_from_foodtruck_id INT,
    IN  p_to_warehouse_id   INT,
    IN  p_to_foodtruck_id   INT,
    IN  p_ingredient_id     INT,
    IN  p_quantity          DECIMAL(10,3),
    IN  p_moved_by          INT,
    IN  p_notes             TEXT,
    OUT p_movement_id       INT,
    OUT p_error             VARCHAR(255)
)
BEGIN
    DECLARE v_available DECIMAL(10,3) DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 p_error = MESSAGE_TEXT;
        SET p_movement_id = NULL;
    END;

    SET p_error = NULL;

    IF (p_from_warehouse_id IS NULL AND p_from_foodtruck_id IS NULL) OR
       (p_from_warehouse_id IS NOT NULL AND p_from_foodtruck_id IS NOT NULL) THEN
        SET p_error = 'Debe especificarse exactamente un origen';
        SET p_movement_id = NULL;
        LEAVE sp_move_stock;
    END IF;

    IF (p_to_warehouse_id IS NULL AND p_to_foodtruck_id IS NULL) OR
       (p_to_warehouse_id IS NOT NULL AND p_to_foodtruck_id IS NOT NULL) THEN
        SET p_error = 'Debe especificarse exactamente un destino';
        SET p_movement_id = NULL;
        LEAVE sp_move_stock;
    END IF;

    IF p_quantity IS NULL OR p_quantity <= 0 THEN
        SET p_error = 'La cantidad debe ser mayor a cero';
        SET p_movement_id = NULL;
        LEAVE sp_move_stock;
    END IF;

    -- Verificar stock disponible en origen
    IF p_from_warehouse_id IS NOT NULL THEN
        SELECT COALESCE(quantity, 0) INTO v_available
        FROM warehouse_stock
        WHERE warehouse_id = p_from_warehouse_id AND ingredient_id = p_ingredient_id;
    ELSE
        SELECT COALESCE(quantity, 0) INTO v_available
        FROM foodtruck_stock
        WHERE foodtruck_id = p_from_foodtruck_id AND ingredient_id = p_ingredient_id;
    END IF;

    IF v_available < p_quantity THEN
        SET p_error = CONCAT('Stock insuficiente. Disponible: ', v_available, ', solicitado: ', p_quantity);
        SET p_movement_id = NULL;
        LEAVE sp_move_stock;
    END IF;

    START TRANSACTION;

    -- Descontar del origen
    IF p_from_warehouse_id IS NOT NULL THEN
        UPDATE warehouse_stock
        SET quantity = quantity - p_quantity
        WHERE warehouse_id = p_from_warehouse_id AND ingredient_id = p_ingredient_id;
    ELSE
        UPDATE foodtruck_stock
        SET quantity = quantity - p_quantity
        WHERE foodtruck_id = p_from_foodtruck_id AND ingredient_id = p_ingredient_id;
    END IF;

    -- Sumar al destino
    IF p_to_warehouse_id IS NOT NULL THEN
        INSERT INTO warehouse_stock (warehouse_id, ingredient_id, quantity)
        VALUES (p_to_warehouse_id, p_ingredient_id, p_quantity)
        ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;
    ELSE
        INSERT INTO foodtruck_stock (foodtruck_id, ingredient_id, quantity)
        VALUES (p_to_foodtruck_id, p_ingredient_id, p_quantity)
        ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;
    END IF;

    -- Registrar el movimiento
    INSERT INTO stock_movements
        (from_warehouse_id, from_foodtruck_id, to_warehouse_id, to_foodtruck_id,
         ingredient_id, quantity, moved_by, notes)
    VALUES
        (p_from_warehouse_id, p_from_foodtruck_id, p_to_warehouse_id, p_to_foodtruck_id,
         p_ingredient_id, p_quantity, p_moved_by, p_notes);

    SET p_movement_id = LAST_INSERT_ID();

    COMMIT;
END$$


-- -------------------------------------------------------------
-- sp_close_receipt
-- Cierra un ticket: valida stock, descuenta ingredientes del
-- foodtruck y actualiza total_amount.
-- IN:  p_receipt_id  INT
--      p_cashier_id  INT  – debe coincidir con el cajero del ticket
-- OUT: p_error       VARCHAR
-- -------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_close_receipt $$
CREATE PROCEDURE sp_close_receipt(
    IN  p_receipt_id INT,
    IN  p_cashier_id INT,
    OUT p_error      VARCHAR(255)
)
BEGIN
    DECLARE v_foodtruck_id  INT;
    DECLARE v_status        VARCHAR(20);
    DECLARE v_done          INT DEFAULT 0;

    DECLARE v_menu_item_id  INT;
    DECLARE v_qty_sold      INT;
    DECLARE v_ingr_id       INT;
    DECLARE v_ingr_qty      DECIMAL(10,3);
    DECLARE v_available     DECIMAL(10,3);
    DECLARE v_total         DECIMAL(10,2);

    DECLARE cur_items CURSOR FOR
        SELECT ri.menu_item_id, ri.quantity
        FROM receipt_items ri
        WHERE ri.receipt_id = p_receipt_id;

    DECLARE cur_ingr CURSOR FOR
        SELECT mii.ingredient_id, mii.quantity * v_qty_sold
        FROM menu_item_ingredients mii
        WHERE mii.menu_item_id = v_menu_item_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        GET DIAGNOSTICS CONDITION 1 p_error = MESSAGE_TEXT;
    END;

    SET p_error = NULL;

    SELECT status, foodtruck_id INTO v_status, v_foodtruck_id
    FROM receipts WHERE id = p_receipt_id;

    IF v_status IS NULL THEN
        SET p_error = CONCAT('Ticket no encontrado: ', p_receipt_id);
        LEAVE sp_close_receipt;
    END IF;

    IF v_status != 'open' THEN
        SET p_error = CONCAT('El ticket no está abierto. Estado actual: ', v_status);
        LEAVE sp_close_receipt;
    END IF;

    START TRANSACTION;

    -- Verificar y descontar stock por cada ítem del ticket
    OPEN cur_items;
    items_loop: LOOP
        FETCH cur_items INTO v_menu_item_id, v_qty_sold;
        IF v_done THEN LEAVE items_loop; END IF;

        SET v_done = 0;

        OPEN cur_ingr;
        ingr_loop: LOOP
            FETCH cur_ingr INTO v_ingr_id, v_ingr_qty;
            IF v_done THEN LEAVE ingr_loop; END IF;

            SELECT COALESCE(quantity, 0) INTO v_available
            FROM foodtruck_stock
            WHERE foodtruck_id = v_foodtruck_id AND ingredient_id = v_ingr_id;

            IF v_available < v_ingr_qty THEN
                CLOSE cur_ingr;
                CLOSE cur_items;
                ROLLBACK;
                SET p_error = CONCAT('Stock insuficiente para ingrediente id=', v_ingr_id,
                                     '. Disponible: ', v_available, ', necesario: ', v_ingr_qty);
                LEAVE sp_close_receipt;
            END IF;

            UPDATE foodtruck_stock
            SET quantity = quantity - v_ingr_qty
            WHERE foodtruck_id = v_foodtruck_id AND ingredient_id = v_ingr_id;

        END LOOP ingr_loop;
        CLOSE cur_ingr;

        SET v_done = 0;
    END LOOP items_loop;
    CLOSE cur_items;

    -- Calcular y guardar total
    SELECT COALESCE(SUM(subtotal), 0) INTO v_total
    FROM receipt_items WHERE receipt_id = p_receipt_id;

    UPDATE receipts
    SET status       = 'closed',
        total_amount = v_total,
        closed_at    = NOW()
    WHERE id = p_receipt_id;

    COMMIT;
END$$

DELIMITER ;
