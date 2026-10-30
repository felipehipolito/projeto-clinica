-- schema.sql — banco de dados da Clínica Vida (MySQL 8)
-- Execute no MySQL Workbench: File > Open SQL Script > raio ⚡

DROP DATABASE IF EXISTS clinica;
CREATE DATABASE clinica
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE clinica;

-- 1. Usuários do sistema (equipe da clínica)
CREATE TABLE usuario (
  id_usuario INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome       VARCHAR(80)  NOT NULL,
  email      VARCHAR(120) NOT NULL,
  senha      VARCHAR(100) NOT NULL,              -- senha em texto plano
  perfil     ENUM('admin','recepcao') NOT NULL DEFAULT 'recepcao',
  criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usuario),
  UNIQUE KEY uq_usuario_email (email)
) ENGINE = InnoDB;

-- 2. Pacientes
CREATE TABLE paciente (
  id_paciente     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome            VARCHAR(100) NOT NULL,
  cpf             VARCHAR(14)  NOT NULL,         -- formato tradicional de CPF (ex: 123.456.789-00)
  data_nascimento DATE         NOT NULL,
  telefone        VARCHAR(20)  NOT NULL,
  email           VARCHAR(120) NULL,
  consentimento_em DATETIME    NOT NULL,
  criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_paciente),
  UNIQUE KEY uq_paciente_cpf (cpf),
  INDEX idx_paciente_nome (nome)
) ENGINE = InnoDB;

-- 3. Médicos
CREATE TABLE medico (
  id_medico     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome          VARCHAR(100) NOT NULL,
  crm           VARCHAR(20)  NOT NULL,
  especialidade VARCHAR(60)  NOT NULL,
  email         VARCHAR(120) NULL,
  PRIMARY KEY (id_medico),
  UNIQUE KEY uq_medico_crm (crm)
) ENGINE = InnoDB;

-- 4. Agendamentos: liga paciente, médico e o usuário que agendou
CREATE TABLE agendamento (
  id_agendamento INT UNSIGNED NOT NULL AUTO_INCREMENT,
  id_paciente    INT UNSIGNED NOT NULL,
  id_medico      INT UNSIGNED NOT NULL,
  data_consulta  DATE         NOT NULL,
  hora_consulta  TIME         NOT NULL,
  status         ENUM('agendada','realizada','cancelada') NOT NULL DEFAULT 'agendada',
  observacao     VARCHAR(255) NULL,
  criado_por     INT UNSIGNED NOT NULL,
  criado_em      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_agendamento),
  -- o mesmo médico não atende duas consultas no mesmo horário
  UNIQUE KEY uq_medico_horario (id_medico, data_consulta, hora_consulta),
  INDEX idx_agenda_data (data_consulta, hora_consulta),
  CONSTRAINT fk_agenda_paciente FOREIGN KEY (id_paciente) REFERENCES paciente (id_paciente),
  CONSTRAINT fk_agenda_medico   FOREIGN KEY (id_medico)   REFERENCES medico (id_medico),
  CONSTRAINT fk_agenda_usuario  FOREIGN KEY (criado_por)  REFERENCES usuario (id_usuario)
) ENGINE = InnoDB;

-- 1. Inserção de 3 registros na tabela usuario
INSERT INTO usuario (nome, email, senha, perfil) VALUES
  ('Carlos Andrade', 'carlos.andrade@clinicavida.com', 'senha123', 'admin'),
  ('Mariana Santos', 'mariana.santos@clinicavida.com', 'senha123', 'recepcao'),
  ('Roberto Lima', 'roberto.lima@clinicavida.com', 'senha123', 'recepcao');

-- 2. Inserção de 3 registros na tabela paciente
INSERT INTO paciente (nome, cpf, data_nascimento, telefone, email, consentimento_em) VALUES
  ('Ana Beatriz Souza', '123.456.789-01', '1990-04-12', '(11) 98765-4321', 'ana.souza@email.com', '2026-09-01 09:00:00'),
  ('Bruno Henrique Lima', '234.567.890-12', '1985-09-30', '(11) 97654-3210', NULL, '2026-09-02 09:00:00'),
  ('Carlos Eduardo Silva', '345.678.901-23', '1972-01-18', '(11) 96543-2109', 'carlos.silva@email.com', '2026-09-03 09:00:00');

-- 3. Inserção de 3 registros na tabela medico
INSERT INTO medico (nome, crm, especialidade, email) VALUES
  ('Dr. Marcos Oliveira', 'CRM-SP 123456', 'Cardiologia', 'marcos@clinicavida.com'),
  ('Dra. Fernanda Alves', 'CRM-SP 234567', 'Pediatria', 'fernanda@clinicavida.com'),
  ('Dr. Ricardo Nunes', 'CRM-SP 345678', 'Ortopedia', NULL);

-- 4. Inserção de 3 registros na tabela agendamento
INSERT INTO agendamento (id_paciente, id_medico, data_consulta, hora_consulta, status, observacao, criado_por) VALUES
  (1, 2, '2026-10-06', '09:30:00', 'agendada', NULL, 1),
  (2, 3, '2026-10-02', '10:00:00', 'realizada', NULL, 3),
  (3, 1, '2026-10-09', '14:00:00', 'agendada', 'Retorno com exames', 1);