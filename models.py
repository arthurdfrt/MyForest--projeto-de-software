# models.py
import os
import sqlite3
from abc import ABC, abstractmethod
from werkzeug.utils import secure_filename
from flask import current_app

class ItemRepositorio(ABC):
    def __init__(self, titulo, usuario_id):
        self.titulo = titulo
        self.usuario_id = usuario_id
        self.tipo = "indefinido"

    @abstractmethod
    def preparar_dados(self):
        pass

    def antes_de_salvar(self):
        pass

    def depois_de_salvar(self):
        pass

    def salvar(self):
        self.antes_de_salvar()
        dados = self.preparar_dados()
        conn = sqlite3.connect('database.db')
        conn.cursor().execute(
            "INSERT INTO repositorio (tipo, titulo, conteudo, resposta, usuario_id) VALUES (?, ?, ?, ?, ?)",
            dados
        )
        conn.commit()
        conn.close()
        self.depois_de_salvar()

class Resumo(ItemRepositorio):
    def __init__(self, titulo, usuario_id, conteudo):
        super().__init__(titulo, usuario_id)
        self.tipo = "resumo"
        self.conteudo = conteudo

    def preparar_dados(self):
        return (self.tipo, self.titulo, self.conteudo, "", self.usuario_id)


class Questao(ItemRepositorio):
    def __init__(self, titulo, usuario_id, pergunta, resposta):
        super().__init__(titulo, usuario_id)
        self.tipo = "questao"
        self.pergunta = pergunta
        self.resposta = resposta

    def preparar_dados(self):
        return (self.tipo, self.titulo, self.pergunta, self.resposta, self.usuario_id)


class ArquivoDigital(ItemRepositorio):
    def __init__(self, titulo, usuario_id, arquivo_obj, tipo_arquivo):
        super().__init__(titulo, usuario_id)
        self.tipo = tipo_arquivo
        self.arquivo_obj = arquivo_obj

    def antes_de_salvar(self):
        if not self.arquivo_obj or not self.arquivo_obj.filename:
            raise ValueError("Nenhum arquivo enviado")

    def preparar_dados(self):
        nome_arquivo = ""
        if self.arquivo_obj and self.arquivo_obj.filename:
            nome_arquivo = secure_filename(self.arquivo_obj.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            self.arquivo_obj.save(os.path.join(upload_folder, nome_arquivo))
        return (self.tipo, self.titulo, nome_arquivo, "", self.usuario_id)