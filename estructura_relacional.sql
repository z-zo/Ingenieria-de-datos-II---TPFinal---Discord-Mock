
-- ESTRUCTURA RELACIONAL (DER)

CREATE TABLE Users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
);

CREATE TABLE Servers (
    server_id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    owner_id BIGINT REFERENCES Users(user_id)
);

CREATE TABLE Channels (
    channel_id BIGINT PRIMARY KEY,
    server_id BIGINT REFERENCES Servers(server_id),
    name VARCHAR(100),
    last_activity_at TIMESTAMP 
);

CREATE TABLE ServerMembers (
    server_id BIGINT REFERENCES Servers(server_id),
    user_id BIGINT REFERENCES Users(user_id),
    message_count INT DEFAULT 0, 
    PRIMARY KEY (server_id, user_id)
);

CREATE TABLE permissions (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL 
);

CREATE TABLE Roles (
    role_id INT PRIMARY KEY,
    server_id BIGINT REFERENCES Servers(server_id),
    name VARCHAR(50)
);
-- tabla intermedia para asignar un rol específico a un miembro específico
CREATE TABLE member_roles (
    user_id BIGINT,
    server_id BIGINT,
    role_id INT REFERENCES Roles(role_id),
    FOREIGN KEY (server_id, user_id) REFERENCES ServerMembers(server_id, user_id),
    PRIMARY KEY (user_id, server_id, role_id)
);
CREATE TABLE role_permissions (
    role_id INT REFERENCES Roles(role_id),
    permission_id INT REFERENCES permissions(id),
    granted BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (role_id, permission_id)
);


-- INSERTS DE DATOS (Para que funcione el Orquestador)

-- Insertamos todos los usuarios del equipo
INSERT INTO Users (user_id, username, email) VALUES
(1, 'arquitecto', 'arquitecto@universidad.edu'),
(2, 'sebastian', 'sebastian@universidad.edu'),
(3, 'guillermo', 'guillermo@universidad.edu'),
(4, 'alejandro', 'alejandro@universidad.edu'),
(5, 'luciano', 'luciano@universidad.edu'),
(6, 'camila', 'camila@universidad.edu');

-- Insertamos servidor de prueba
INSERT INTO Servers (server_id, name, owner_id) VALUES
(100, 'Servidor de Bases de Datos II', 1);

-- Insertamos canales (deben coincidir con los de ScyllaDB)
INSERT INTO Channels (channel_id, server_id, name, last_activity_at) VALUES
(10, 100, 'general', CURRENT_TIMESTAMP),
(20, 100, 'off-topic', CURRENT_TIMESTAMP),
(1001, 100, 'consultas-nosql', CURRENT_TIMESTAMP);

-- unir a todos los usuarios al servidor 100, esto les perminte tener rol y permisos para enviar mensajes
INSERT INTO ServerMembers (server_id, user_id, message_count) VALUES
(100, 1, 0),
(100, 2, 0),
(100, 3, 0),
(100, 4, 0),
(100, 5, 0),
(100, 6 , 0); -- todo empiezan sin mensajes

-- Tabla de permisos
INSERT INTO permissions (id, name) VALUES
(1, 'SEND_MESSAGES'),
(2, 'MANAGE_CHANNELS');

INSERT INTO Roles (role_id, server_id, name) VALUES
(10, 100, 'Admin'),
(11, 100, 'Usuario');

INSERT INTO role_permissions (role_id, permission_id, granted) VALUES
(10, 1, TRUE),
(10, 2, TRUE),
(11, 1, TRUE);

-- asignamos al ususario 1 del servidor(el unico), el rol_id 10 que seria "Admin"
INSERT INTO member_roles (user_id, server_id, role_id) VALUES
(1, 100, 10);

-- todos los otros usuarios son "Usuario" (11)
INSERT INTO member_roles (user_id, server_id, role_id) VALUES
(2, 100, 11),
(3, 100, 11),
(4, 100, 11),
(5, 100, 11);