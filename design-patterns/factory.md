# Refatoração com Factory Method

## O que foi feito

O código original concentrava toda a lógica de criação de objetos diretamente na rota `/adicionar/<tipo>` do `app.py`. A refatoração separou o projeto em três arquivos com responsabilidades distintas e aplicou o padrão **Factory Method** para centralizar a criação de objetos.

---

## Arquivos criados

### `models.py`
Contém as classes de domínio que antes viviam no `app.py`:

- `ItemRepositorio` — superclasse abstrata (herda de `ABC`). Define o esqueleto do método `salvar()` e declara `preparar_dados()` como `@abstractmethod`, obrigando todas as subclasses a implementá-lo.
- `Resumo` — salva título e conteúdo de texto.
- `Questao` — salva pergunta e resposta separadamente.
- `ArquivoDigital` — salva o arquivo fisicamente e registra o nome no banco. Usa `current_app.config['UPLOAD_FOLDER']` em vez de `app.config` para funcionar fora do contexto do `app.py`.

### `factory.py`
Contém a classe `ItemFactory` com um único método estático `criar()`. Recebe o tipo como string e os dados do formulário, e retorna o objeto concreto correto — sem que o chamador precise conhecer nenhuma classe diretamente.

---

## O que mudou no `app.py`

### Antes
```python
from flask import Flask, ...

# classes definidas aqui dentro (Resumo, Questao, ArquivoDigital...)

@app.route('/adicionar/<tipo>', methods=['POST'])
@login_required
def adicionar(tipo):
    titulo = request.form.get('titulo')
    novo_item = None

    if tipo == 'resumo':
        conteudo = request.form.get('conteudo')
        novo_item = Resumo(titulo, current_user.id, conteudo)

    elif tipo == 'questao':
        pergunta = request.form.get('conteudo')
        resposta = request.form.get('resposta')
        novo_item = Questao(titulo, current_user.id, pergunta, resposta)

    elif tipo in ['pdf', 'musica']:
        arquivo = request.files.get('arquivo')
        novo_item = ArquivoDigital(titulo, current_user.id, arquivo, tipo)

    if novo_item:
        novo_item.salvar()

    return redirect(url_for('ver_repositorio', tipo=tipo))
```

### Depois
```python
from factory import ItemFactory

@app.route('/adicionar/<tipo>', methods=['POST'])
@login_required
def adicionar(tipo):
    try:
        novo_item = ItemFactory.criar(tipo, request.form, current_user.id, request.files)
        novo_item.salvar()
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('ver_repositorio', tipo=tipo))
```

---

## Por que essa mudança importa

| Antes | Depois |
|---|---|
| A rota decidia qual classe instanciar | A `ItemFactory` centraliza essa decisão |
| A rota conhecia `Resumo`, `Questao` e `ArquivoDigital` | A rota só conhece `ItemFactory` |
| Adicionar um novo tipo exigia mexer na rota | Basta criar a classe e adicionar um `elif` na Factory |
| Violava o princípio da Responsabilidade Única | Cada arquivo tem uma responsabilidade clara |

---

## Como o Polimorfismo age junto

A Factory resolve **qual objeto criar**. O Polimorfismo resolve **como ele se comporta** depois de criado.

```
ItemFactory.criar('resumo', ...)   →   retorna Resumo(...)
                                            ↓
                                   novo_item.salvar()
                                            ↓
                                   preparar_dados()  ←  cada classe executa o seu
```

A rota chama `.salvar()` sem saber qual tipo de objeto está manipulando. O Python decide em tempo de execução qual `preparar_dados()` executar com base na classe real do objeto.

---

## Como estender no futuro

Para adicionar um novo tipo, como `Video`:

1. Criar a classe `Video` em `models.py` herdando de `ItemRepositorio`
2. Implementar `preparar_dados()` na nova classe
3. Adicionar `elif tipo == 'video':` na `ItemFactory`

A rota `/adicionar/<tipo>` e o método `salvar()` **não precisam de nenhuma modificação**.