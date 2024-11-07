import fdb
from flask import Flask, render_template, request, flash, redirect, url_for
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jqwdbjAHSDBhjBWd8723DWHV5rDWHD4783JHDKJVBWhdj'


host = 'localhost'  # ou o IP do servidor onde o Firebird está rodando
database = r'C:\Users\Aluno\Downloads\BANCO (1)\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)


class Livro:
    def __init__(self, id_livro, titulo, autor, ano_publicacao):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao


@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo livro')


@app.route('/excluir_livro/<int:id>')
def excluir(id):
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM livro WHERE ID_LIVRO = ?", (id,))
        con.commit()
        flash('Livro Excluido com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash('Erro ao excluir', 'error')
    finally:
        cursor.close()
        return redirect(url_for('index'))


@app.route('/editar_livro/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM LIVRO WHERE id_livro = ?', (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash("Erro: Livro não encontrado", "error")
        return redirect(url_for('index'))
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']

        cursor.execute('UPDATE LIVRO SET titulo = ?, autor = ?, ano_publicacao = ? where id_livro = ?',
                       (titulo, autor, ano_publicacao, id))
        con.commit()
        cursor.close()
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')


@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM LIVRO')
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)


@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    # Criando o cursor
    cursor = con.cursor()

    try:
        # Verificar se o livro já existe
        cursor.execute("SELECT 1 FROM livro WHERE TITULO = ?", (titulo,))
        if cursor.fetchone():  # Se existir algum registro
            flash("Erro: Livro já cadastrado.", "error")
            return redirect(url_for('novo'))

        # Inserir o novo livro (sem capturar o ID)
        cursor.execute("INSERT INTO livro (TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?)",
                       (titulo, autor, ano_publicacao))
        con.commit()
    finally:
        # Fechar o cursor manualmente, mesmo que haja erro
        cursor.close()

    flash("Livro cadastrado com sucesso!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
