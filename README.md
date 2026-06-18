# 🌱 Projeto de Estudos — Flask + OOP + Design Patterns

Aplicação web de produtividade desenvolvida com Flask, com foco em demonstrar conceitos de **Programação Orientada a Objetos** e **Padrões de Projeto** aplicados em um contexto real.

---

## 🧠 Padrões de Projeto Aplicados

O projeto aplica três padrões de projeto, cada um documentado em detalhes na pasta `design-patterns/`:

| Padrão | Categoria | Onde é aplicado | Documentação |
|---|---|---|---|
| **Factory Method** | Criacional | Criação de itens no repositório (`Resumo`, `Questao`, `ArquivoDigital`) | [factory.md](https://github.com/arthurdfrt/MyForest--projeto-de-software/blob/main/design-patterns/factory.md) |
| **Template Method** | Comportamental | Fluxo de salvamento de itens com hooks opcionais | [template.md](https://github.com/arthurdfrt/MyForest--projeto-de-software/blob/main/design-patterns/template.md) |
| **Proxy** | Estrutural | Acesso centralizado ao banco de dados com logging | [proxy.md](https://github.com/arthurdfrt/MyForest--projeto-de-software/blob/main/design-patterns/proxy.md) |

Cada arquivo explica o problema que motivou a aplicação do padrão, o que mudou no código (com exemplos antes/depois) e como estender a solução no futuro.

---

## 🏗️ Conceitos de OOP Demonstrados

- **Herança** — `Resumo`, `Questao` e `ArquivoDigital` herdam de `ItemRepositorio`
- **Polimorfismo** — todas as subclasses implementam `preparar_dados()` de forma diferente, mas são chamadas da mesma forma
- **Encapsulamento** — a lógica de criação de objetos fica isolada na `ItemFactory`, e o acesso ao banco fica isolado no `DatabaseProxy`
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

---

## 📝 Feedback dos Usuários

Coletamos feedback de colegas e amigos sobre usabilidade, interface, utilidade e bugs encontrados no projeto.

🔗 [Respostas do formulário de feedback](https://docs.google.com/spreadsheets/d/1NtfM8vC6Z_Stbw9a5PQRaNWJumbKhyaPZ6x6B_pSPec/edit?usp=sharing)