-- db_dump.sql
-- DDL для PostgreSQL — таблицы схемы (12 таблиц) + несколько тестовых записей.
-- Запустите в PostgreSQL: psql -U postgres -d yourdb -f db_dump.sql

CREATE TABLE roles (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL UNIQUE,
    description text
);

CREATE TABLE users (
    id serial PRIMARY KEY,
    username varchar(120) NOT NULL UNIQUE,
    password varchar(256) NOT NULL,
    full_name varchar(200),
    email varchar(200) UNIQUE,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE user_roles (
    user_id integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id integer NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE groups (
    id serial PRIMARY KEY,
    name varchar(200) NOT NULL,
    description text
);

CREATE TABLE clients (
    id serial PRIMARY KEY,
    full_name varchar(200),
    email varchar(200) UNIQUE,
    phone varchar(50),
    created_at timestamp without time zone DEFAULT now(),
    group_id integer REFERENCES groups(id)
);

CREATE TABLE templates (
    id serial PRIMARY KEY,
    name varchar(200) NOT NULL,
    subject varchar(300),
    body_html text,
    creator_id integer REFERENCES users(id)
);

CREATE TABLE campaigns (
    id serial PRIMARY KEY,
    name varchar(300) NOT NULL,
    template_id integer REFERENCES templates(id),
    creator_id integer REFERENCES users(id),
    created_at timestamp without time zone DEFAULT now(),
    scheduled_at timestamp without time zone,
    status varchar(50) DEFAULT 'draft'
);

CREATE TABLE campaign_recipients (
    id serial PRIMARY KEY,
    campaign_id integer REFERENCES campaigns(id) ON DELETE CASCADE,
    client_id integer REFERENCES clients(id),
    status varchar(50) DEFAULT 'pending'
);

CREATE TABLE emails (
    id serial PRIMARY KEY,
    campaign_id integer REFERENCES campaigns(id),
    client_id integer REFERENCES clients(id),
    subject varchar(500),
    body text,
    status varchar(50) DEFAULT 'queued',
    sent_at timestamp without time zone,
    message_id varchar(200)
);

CREATE TABLE attachments (
    id serial PRIMARY KEY,
    filename varchar(300),
    filepath varchar(500),
    uploaded_at timestamp without time zone DEFAULT now(),
    owner_id integer REFERENCES users(id)
);

CREATE TABLE logs (
    id serial PRIMARY KEY,
    level varchar(20),
    message text,
    created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE settings (
    id serial PRIMARY KEY,
    key varchar(200) UNIQUE,
    value text
);

-- Добавляем роли
INSERT INTO roles (name, description) VALUES
('admin', 'Администратор системы'),
('manager', 'Менеджер кампаний'),
('client', 'Клиент/контакт');

-- Тестовые пользователи
INSERT INTO users (username, password, full_name, email) VALUES
('admin', 'admin', 'Администратор ВКР', 'admin@example.com'),
('manager', 'manager', 'Менеджер Петров', 'manager@example.com'),
('client', 'client', 'Клиент Иванов', 'client@example.com');

-- Связи роли/пользователь
INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1), (2, 2), (3, 3);

-- Тестовые группы и клиенты
INSERT INTO groups (name, description) VALUES
('Студенты 1 курс', 'Первая группа'),
('Преподаватели', 'Преподавательский состав');

INSERT INTO clients (full_name, email, phone, group_id) VALUES
('Алексей Смирнов', 'a.smirnov@example.com', '+7-900-000-0001', 1),
('Мария Петрова', 'm.petrova@example.com', '+7-900-000-0002', 2),
('Иван Сергеев', 'i.sergeev@example.com', '+7-900-000-0003', 1);

-- Пример шаблона
INSERT INTO templates (name, subject, body_html, creator_id) VALUES
('Приветствие студентам', 'Добро пожаловать, {{full_name}}', '<p>Уважаемый(ая) {{full_name}},<br>Добро пожаловать в университет!</p>', 1);

-- Пример кампании
INSERT INTO campaigns (name, template_id, creator_id, status) VALUES
('Кампания_Приветствие', 1, 1, 'draft');
