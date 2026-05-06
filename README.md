# 🌱 Projeto de Estudos — Flask + OOP + Design Patterns

Aplicação web de produtividade desenvolvida com Flask, com foco em demonstrar conceitos de **Programação Orientada a Objetos** e **Padrões de Projeto** aplicados em um contexto real.

---

## 🧠 Padrão de Projeto Aplicado — Factory Method

### O problema
A rota `/adicionar/<tipo>` concentrava a responsabilidade de decidir qual classe instanciar (`Resumo`, `Questao` ou `ArquivoDigital`), violando o princípio da **Responsabilidade Única (SRP)**. Qualquer novo tipo exigiria modificar diretamente a rota.

### A solução
Foi criada a classe `ItemFactory`, que centraliza toda a lógica de criação de objetos. A rota passou de um bloco `if/elif` extenso para apenas 3 linhas:

```python
# Antes
if tipo == 'resumo':
    novo_item = Resumo(titulo, current_user.id, conteudo)
elif tipo == 'questao':
    novo_item = Questao(titulo, current_user.id, pergunta, resposta)
elif tipo in ['pdf', 'musica']:
    novo_item = ArquivoDigital(titulo, current_user.id, arquivo, tipo)

# Depois
novo_item = ItemFactory.criar(tipo, request.form, current_user.id, request.files)
novo_item.salvar()
```

### Como funciona

| Camada | Responsabilidade |
|---|---|
| `ItemFactory.criar()` | Decide **qual** objeto instanciar com base no tipo |
| Polimorfismo + `salvar()` | Garante que qualquer objeto criado se comporte da mesma forma |
| Rota `/adicionar/<tipo>` | Apenas lida com HTTP — sem conhecer nenhuma classe concreta |

### Como estender
Para adicionar um novo tipo (ex: `Video`), basta:
1. Criar a classe `Video` herdando de `ItemRepositorio`
2. Implementar `preparar_dados()` na nova classe
3. Adicionar um `elif` na `ItemFactory`

A rota e o método `salvar()` **não precisam de nenhuma modificação**.

---

## 🏗️ Conceitos de OOP Demonstrados

- **Herança** — `Resumo`, `Questao` e `ArquivoDigital` herdam de `ItemRepositorio`
- **Polimorfismo** — todas as subclasses implementam `preparar_dados()` de forma diferente, mas são chamadas da mesma forma
- **Encapsulamento** — a lógica de criação de objetos fica isolada na `ItemFactory`
- **Abstração** — `ItemRepositorio` define o contrato via `ABC` e `@abstractmethod`

---

## 🚀 Funcionalidades

- ⏱️ Timer de estudos com contabilização de tempo
- 🌳 Jardim virtual que cresce conforme o tempo estudado
- 🎯 Metas de estudo com recompensas
- 📚 Repositório de resumos, questões, PDFs e músicas
- 👤 Sistema de login e cadastro de usuários

---

## 🛠️ Tecnologias

- Python + Flask
- SQLite
- Flask-Login
- Werkzeug
