-- =============================================================
-- SmartGastro – Datos iniciales (справочники)
-- Migración: 002_seed_data.sql
-- =============================================================

USE smartgastro;

INSERT INTO roles (name) VALUES
    ('owner'),
    ('accountant'),
    ('seller'),
    ('cashier'),
    ('cook');

INSERT INTO units (name) VALUES
    ('g'),
    ('kg'),
    ('l'),
    ('ml'),
    ('pcs');

INSERT INTO payment_methods (name) VALUES
    ('cash'),
    ('card'),
    ('mercadopago');

INSERT INTO cancellation_reasons (name) VALUES
    ('rain'),
    ('organizer_cancelled'),
    ('no_permit'),
    ('force_majeure'),
    ('other');
