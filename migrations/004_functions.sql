-- =============================================================
-- SmartGastro – Funciones
-- Migración: 004_functions.sql
-- =============================================================

USE smartgastro;

DELIMITER $$

-- -------------------------------------------------------------
-- fn_available_quantity
-- Devuelve cuántas porciones de un menu_item puede vender
-- un foodtruck dado el stock actual de sus ingredientes.
-- El cuello de botella lo determina el ingrediente más escaso.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_available_quantity $$
CREATE FUNCTION fn_available_quantity(
    p_menu_item_id INT,
    p_foodtruck_id INT
)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_max_portions INT DEFAULT 2147483647;  -- INT_MAX como techo inicial
    DECLARE v_portions     INT;
    DECLARE v_done         INT DEFAULT 0;
    DECLARE v_ingr_id      INT;
    DECLARE v_required     DECIMAL(10,3);
    DECLARE v_available    DECIMAL(10,3);

    DECLARE cur CURSOR FOR
        SELECT ingredient_id, quantity
        FROM menu_item_ingredients
        WHERE menu_item_id = p_menu_item_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    OPEN cur;
    loop_ingr: LOOP
        FETCH cur INTO v_ingr_id, v_required;
        IF v_done THEN LEAVE loop_ingr; END IF;

        SELECT COALESCE(quantity, 0) INTO v_available
        FROM foodtruck_stock
        WHERE foodtruck_id = p_foodtruck_id AND ingredient_id = v_ingr_id;

        SET v_portions = FLOOR(v_available / v_required);

        IF v_portions < v_max_portions THEN
            SET v_max_portions = v_portions;
        END IF;
    END LOOP;
    CLOSE cur;

    -- Si el plato no tiene ingredientes o no existe devuelve 0
    IF v_max_portions = 2147483647 THEN
        RETURN 0;
    END IF;

    RETURN v_max_portions;
END$$


-- -------------------------------------------------------------
-- fn_check_stock_alert
-- Devuelve 1 si algún ingrediente del foodtruck está por debajo
-- de su umbral mínimo, 0 si todo está en orden.
-- Pasar p_foodtruck_id = NULL para revisar todos los foodtrucks.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_check_stock_alert $$
CREATE FUNCTION fn_check_stock_alert(
    p_ingredient_id INT,
    p_foodtruck_id  INT
)
RETURNS TINYINT(1)
READS SQL DATA
BEGIN
    DECLARE v_count INT DEFAULT 0;

    IF p_foodtruck_id IS NOT NULL THEN
        SELECT COUNT(*) INTO v_count
        FROM foodtruck_stock fs
        JOIN ingredients i ON i.id = fs.ingredient_id
        WHERE fs.ingredient_id = p_ingredient_id
          AND fs.foodtruck_id  = p_foodtruck_id
          AND fs.quantity < i.min_stock_alert;
    ELSE
        SELECT COUNT(*) INTO v_count
        FROM foodtruck_stock fs
        JOIN ingredients i ON i.id = fs.ingredient_id
        WHERE fs.ingredient_id = p_ingredient_id
          AND fs.quantity < i.min_stock_alert;
    END IF;

    RETURN IF(v_count > 0, 1, 0);
END$$


-- -------------------------------------------------------------
-- fn_receipt_total
-- Calcula el total de un ticket sumando subtotales de sus ítems.
-- Útil para verificar o recalcular sin cerrar el ticket.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_receipt_total $$
CREATE FUNCTION fn_receipt_total(
    p_receipt_id INT
)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(10,2) DEFAULT 0;

    SELECT COALESCE(SUM(subtotal), 0) INTO v_total
    FROM receipt_items
    WHERE receipt_id = p_receipt_id;

    RETURN v_total;
END$$


-- -------------------------------------------------------------
-- fn_event_revenue
-- Devuelve la recaudación total de un evento
-- considerando solo tickets cerrados.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_event_revenue $$
CREATE FUNCTION fn_event_revenue(
    p_event_id INT
)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_revenue DECIMAL(10,2) DEFAULT 0;

    SELECT COALESCE(SUM(r.total_amount), 0) INTO v_revenue
    FROM receipts r
    WHERE r.event_id = p_event_id
      AND r.status   = 'closed';

    RETURN v_revenue;
END$$


-- -------------------------------------------------------------
-- fn_ingredient_total_stock
-- Devuelve el stock total de un ingrediente en TODOS los
-- foodtrucks y warehouses combinados.
-- Útil para que el dueño tenga visión global del inventario.
-- -------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_ingredient_total_stock $$
CREATE FUNCTION fn_ingredient_total_stock(
    p_ingredient_id INT
)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_wh_stock DECIMAL(10,3) DEFAULT 0;
    DECLARE v_ft_stock DECIMAL(10,3) DEFAULT 0;

    SELECT COALESCE(SUM(quantity), 0) INTO v_wh_stock
    FROM warehouse_stock
    WHERE ingredient_id = p_ingredient_id;

    SELECT COALESCE(SUM(quantity), 0) INTO v_ft_stock
    FROM foodtruck_stock
    WHERE ingredient_id = p_ingredient_id;

    RETURN v_wh_stock + v_ft_stock;
END$$

DELIMITER ;
