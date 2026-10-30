from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_clinica'

# Função auxiliar para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('clinica.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criação inicial das tabelas no SQLite
def init_db():
    conn = get_db_connection()
    
    # Tabela Usuario
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela Medico
    conn.execute('''
        CREATE TABLE IF NOT EXISTS medico (
            id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT NOT NULL UNIQUE,
            especialidade TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    ''')

    # Tabela Paciente
    conn.execute('''
        CREATE TABLE IF NOT EXISTS paciente (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            data_nascimento TEXT NOT NULL,
            telefone TEXT NOT NULL,
            endereco TEXT NOT NULL
        )
    ''')

    # Tabela Agendamento
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agendamento (
            id_agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medico INTEGER NOT NULL,
            data_consulta TEXT NOT NULL,
            hora_consulta TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'agendada',
            FOREIGN KEY (id_paciente) REFERENCES paciente (id_paciente),
            FOREIGN KEY (id_medico) REFERENCES medico (id_medico),
            UNIQUE (id_medico, data_consulta, hora_consulta)
        )
    ''')
    
    # Insere usuário padrão caso não exista
    user = conn.execute('SELECT * FROM usuario WHERE email = ?', ('carlos.andrade@clinicavida.com',)).fetchone()
    if not user:
        conn.execute('INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)',
                     ('Carlos Andrade', 'carlos.andrade@clinicavida.com', 'senha123'))
        
    conn.commit()
    conn.close()

init_db()

# --- ROTAS DE AUTENTICAÇÃO E PAINEL ---
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuario WHERE email = ? AND senha = ?', (email, senha)).fetchone()
        conn.close()

        if user:
            session['usuario'] = user['email']
            return redirect(url_for('painel'))
        else:
            flash('E-mail ou senha inválidos. Tente novamente.', 'erro')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('painel.html', usuario=session['usuario'])

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


# --- ROTAS DE USUÁRIOS ---
@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        try:
            conn.execute('INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)', (nome, email, senha))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'sucesso')
        except sqlite3.IntegrityError:
            flash('Erro: O e-mail informado já está cadastrado.', 'erro')
        
        return redirect(url_for('usuarios'))

    lista_usuarios = conn.execute('SELECT * FROM usuario').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=lista_usuarios)

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    usuario_edit = conn.execute('SELECT * FROM usuario WHERE id_usuario = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        conn.execute('UPDATE usuario SET nome = ?, email = ?, senha = ? WHERE id_usuario = ?', (nome, email, senha, id))
        conn.commit()
        conn.close()
        flash('Usuário atualizado com sucesso!', 'sucesso')
        return redirect(url_for('usuarios'))

    lista_usuarios = conn.execute('SELECT * FROM usuario').fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=lista_usuarios, usuario_edit=usuario_edit)

@app.route('/usuarios/excluir/<int:id>')
def excluir_usuario(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM usuario WHERE id_usuario = ?', (id,))
    conn.commit()
    conn.close()
    flash('Usuário excluído com sucesso!', 'sucesso')
    return redirect(url_for('usuarios'))


# --- ROTAS DE MÉDICOS ---
@app.route('/medicos', methods=['GET', 'POST'])
def medicos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form.get('nome')
        crm = request.form.get('crm')
        especialidade = request.form.get('especialidade')
        telefone = request.form.get('telefone')

        try:
            conn.execute('INSERT INTO medico (nome, crm, especialidade, telefone) VALUES (?, ?, ?, ?)',
                         (nome, crm, especialidade, telefone))
            conn.commit()
            flash('Médico cadastrado com sucesso!', 'sucesso')
        except sqlite3.IntegrityError:
            flash('Erro: O CRM informado já está cadastrado.', 'erro')

        return redirect(url_for('medicos'))

    lista_medicos = conn.execute('SELECT * FROM medico').fetchall()
    conn.close()
    return render_template('medicos.html', medicos=lista_medicos)

@app.route('/medicos/editar/<int:id>', methods=['GET', 'POST'])
def editar_medico(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    medico_edit = conn.execute('SELECT * FROM medico WHERE id_medico = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form.get('nome')
        crm = request.form.get('crm')
        especialidade = request.form.get('especialidade')
        telefone = request.form.get('telefone')

        conn.execute('UPDATE medico SET nome = ?, crm = ?, especialidade = ?, telefone = ? WHERE id_medico = ?',
                     (nome, crm, especialidade, telefone, id))
        conn.commit()
        conn.close()
        flash('Médico atualizado com sucesso!', 'sucesso')
        return redirect(url_for('medicos'))

    lista_medicos = conn.execute('SELECT * FROM medico').fetchall()
    conn.close()
    return render_template('medicos.html', medicos=lista_medicos, medico_edit=medico_edit)

@app.route('/medicos/excluir/<int:id>')
def excluir_medico(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM medico WHERE id_medico = ?', (id,))
    conn.commit()
    conn.close()
    flash('Médico excluído com sucesso!', 'sucesso')
    return redirect(url_for('medicos'))


# --- ROTAS DE PACIENTES ---
@app.route('/pacientes', methods=['GET', 'POST'])
def pacientes():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        data_nascimento = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')

        try:
            conn.execute('INSERT INTO paciente (nome, cpf, data_nascimento, telefone, endereco) VALUES (?, ?, ?, ?, ?)',
                         (nome, cpf, data_nascimento, telefone, endereco))
            conn.commit()
            flash('Paciente cadastrado com sucesso!', 'sucesso')
        except sqlite3.IntegrityError:
            flash('Erro: O CPF informado já está cadastrado.', 'erro')

        return redirect(url_for('pacientes'))

    lista_pacientes = conn.execute('SELECT * FROM paciente').fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=lista_pacientes)

@app.route('/pacientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    paciente_edit = conn.execute('SELECT * FROM paciente WHERE id_paciente = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        data_nascimento = request.form.get('data_nascimento')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')

        conn.execute('UPDATE paciente SET nome = ?, cpf = ?, data_nascimento = ?, telefone = ?, endereco = ? WHERE id_paciente = ?',
                     (nome, cpf, data_nascimento, telefone, endereco, id))
        conn.commit()
        conn.close()
        flash('Paciente atualizado com sucesso!', 'sucesso')
        return redirect(url_for('pacientes'))

    lista_pacientes = conn.execute('SELECT * FROM paciente').fetchall()
    conn.close()
    return render_template('pacientes.html', pacientes=lista_pacientes, paciente_edit=paciente_edit)

@app.route('/pacientes/excluir/<int:id>')
def excluir_paciente(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM paciente WHERE id_paciente = ?', (id,))
    conn.commit()
    conn.close()
    flash('Paciente excluído com sucesso!', 'sucesso')
    return redirect(url_for('pacientes'))


# --- ROTAS DE AGENDAMENTOS ---
@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        id_paciente = request.form.get('id_paciente')
        id_medico = request.form.get('id_medico')
        data_consulta = request.form.get('data_consulta')
        hora_consulta = request.form.get('hora_consulta')
        descricao = request.form.get('descricao')

        # Validação de choque de horários do médico
        conflito = conn.execute('''
            SELECT * FROM agendamento 
            WHERE id_medico = ? AND data_consulta = ? AND hora_consulta = ? AND status != 'cancelada'
        ''', (id_medico, data_consulta, hora_consulta)).fetchone()

        if conflito:
            flash('Erro: Este médico já possui uma consulta agendada nesta data e horário!', 'erro')
        else:
            conn.execute('''
                INSERT INTO agendamento (id_paciente, id_medico, data_consulta, hora_consulta, descricao, status)
                VALUES (?, ?, ?, ?, ?, 'agendada')
            ''', (id_paciente, id_medico, data_consulta, hora_consulta, descricao))
            conn.commit()
            flash('Agendamento realizado com sucesso!', 'sucesso')

        return redirect(url_for('agendamentos'))

    # Consulta dos agendamentos realizando JOIN com Paciente e Medico para exibir os nomes
    lista_agendamentos = conn.execute('''
        SELECT a.id_agendamento, a.data_consulta, a.hora_consulta, a.descricao, a.status,
               p.nome AS nome_paciente, m.nome AS nome_medico
        FROM agendamento a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN medico m ON a.id_medico = m.id_medico
        ORDER BY a.data_consulta DESC, a.hora_consulta ASC
    ''').fetchall()

    pacientes = conn.execute('SELECT id_paciente, nome FROM paciente').fetchall()
    medicos = conn.execute('SELECT id_medico, nome FROM medico').fetchall()
    conn.close()

    return render_template('agendamentos.html', agendamentos=lista_agendamentos, pacientes=pacientes, medicos=medicos)

@app.route('/agendamentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_agendamento(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    agendamento_edit = conn.execute('SELECT * FROM agendamento WHERE id_agendamento = ?', (id,)).fetchone()

    if request.method == 'POST':
        id_paciente = request.form.get('id_paciente')
        id_medico = request.form.get('id_medico')
        data_consulta = request.form.get('data_consulta')
        hora_consulta = request.form.get('hora_consulta')
        descricao = request.form.get('descricao')

        # Validação de conflito excluindo o próprio registro sendo editado
        conflito = conn.execute('''
            SELECT * FROM agendamento 
            WHERE id_medico = ? AND data_consulta = ? AND hora_consulta = ? AND id_agendamento != ? AND status != 'cancelada'
        ''', (id_medico, data_consulta, hora_consulta, id)).fetchone()

        if conflito:
            flash('Erro: Este médico já possui uma consulta agendada nesta data e horário!', 'erro')
        else:
            conn.execute('''
                UPDATE agendamento 
                SET id_paciente = ?, id_medico = ?, data_consulta = ?, hora_consulta = ?, descricao = ?
                WHERE id_agendamento = ?
            ''', (id_paciente, id_medico, data_consulta, hora_consulta, descricao, id))
            conn.commit()
            flash('Agendamento atualizado com sucesso!', 'sucesso')

        conn.close()
        return redirect(url_for('agendamentos'))

    lista_agendamentos = conn.execute('''
        SELECT a.id_agendamento, a.data_consulta, a.hora_consulta, a.descricao, a.status,
               p.nome AS nome_paciente, m.nome AS nome_medico
        FROM agendamento a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN medico m ON a.id_medico = m.id_medico
    ''').fetchall()

    pacientes = conn.execute('SELECT id_paciente, nome FROM paciente').fetchall()
    medicos = conn.execute('SELECT id_medico, nome FROM medico').fetchall()
    conn.close()

    return render_template('agendamentos.html', agendamentos=lista_agendamentos, pacientes=pacientes, medicos=medicos, agendamento_edit=agendamento_edit)

@app.route('/agendamentos/cancelar/<int:id>')
def cancelar_agendamento(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("UPDATE agendamento SET status = 'cancelada' WHERE id_agendamento = ?", (id,))
    conn.commit()
    conn.close()
    flash('Agendamento cancelado com sucesso!', 'sucesso')
    return redirect(url_for('agendamentos'))

if __name__ == '__main__':
    app.run(debug=True)