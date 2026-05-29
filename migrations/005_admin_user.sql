-- Usuario admin por defecto para desarrollo
-- password: admin123

USE smartgastro;

INSERT IGNORE INTO users (login, password_hash, full_name, role_id)
VALUES (
    'admin',
    '$2b$12$nKnRgmYP1EEjy4KVE0kr8elWYWzpR0E2HY8vpt/2wqZe0RgiFxnni',
    'Admin User',
    (SELECT id FROM roles WHERE name = 'owner')
);
