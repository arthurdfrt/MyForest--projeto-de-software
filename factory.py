from models import Resumo, Questao, ArquivoDigital

class ItemFactory:
    @staticmethod
    def criar(tipo, form_data, usuario_id, files = None):
        if tipo == 'resumo':
            return Resumo(
                titulo=form_data['titulo'],
                usuario_id=usuario_id,
                conteudo=form_data['conteudo']
            )
        elif tipo == 'questao':
            return Questao(
                titulo=form_data['titulo'],
                usuario_id=usuario_id,
                pergunta=form_data['conteudo'],
                resposta=form_data['resposta']
            )
        elif tipo in ['pdf', 'musica']:
            return ArquivoDigital(
                titulo=form_data['titulo'],
                usuario_id=usuario_id,
                arquivo_obj=files.get('arquivo') if files else None,
                tipo_arquivo=tipo
            )
        else:
            raise ValueError(f"Tipo desconhecido: {tipo}")