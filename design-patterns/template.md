# Refatoração com Template Method

## O que foi feito

O padrão **Template Method** foi aplicado no `models.py`, enriquecendo o método `salvar()` da superclasse `ItemRepositorio` com hooks opcionais que as subclasses podem sobrescrever para adicionar comportamento antes ou depois de salvar.

---

## O que mudou no `models.py`

### Antes
```python
def salvar(self):
    dados = self.preparar_dados()
    conn = sqlite3.connect('database.db')
    conn.cursor().execute(
        "INSERT INTO repositorio (...) VALUES (?, ?, ?, ?, ?)", dados
    )
    conn.commit()
    conn.close()
```

### Depois
```python
def antes_de_salvar(self):
    pass  # hook opcional

def depois_de_salvar(self):
    pass  # hook opcional

def salvar(self):
    self.antes_de_salvar()          # passo 1 — hook
    dados = self.preparar_dados()   # passo 2 — variável (polimorfismo)
    conn = sqlite3.connect('database.db')
    conn.cursor().execute(
        "INSERT INTO repositorio (...) VALUES (?, ?, ?, ?, ?)", dados
    )
    conn.commit()
    conn.close()
    self.depois_de_salvar()         # passo 3 — hook
```

---

## O esqueleto do algoritmo

O Template Method define um algoritmo fixo na superclasse com passos que podem ser sobrescritos pelas subclasses:

```
salvar()
  │
  ├── antes_de_salvar()    ← hook — subclasses podem sobrescrever
  ├── preparar_dados()     ← abstrato — subclasses DEVEM sobrescrever
  ├── salva no banco       ← fixo — nunca muda
  └── depois_de_salvar()  ← hook — subclasses podem sobrescrever
```

A diferença entre os passos:

| Passo | Tipo | Comportamento |
|---|---|---|
| `antes_de_salvar()` | Hook | `pass` por padrão — opcional sobrescrever |
| `preparar_dados()` | Abstrato | Obrigatório implementar em cada subclasse |
| salva no banco | Fixo | Nunca muda, definido na superclasse |
| `depois_de_salvar()` | Hook | `pass` por padrão — opcional sobrescrever |

---

## Como cada subclasse se comporta

### `Resumo` e `Questao`
Não sobrescrevem nenhum hook — herdam o `pass` da superclasse e funcionam normalmente sem nenhuma validação extra.

### `ArquivoDigital`
Sobrescreve `antes_de_salvar()` para validar se um arquivo foi enviado antes de tentar salvar:

```python
class ArquivoDigital(ItemRepositorio):
    def antes_de_salvar(self):
        if not self.arquivo_obj or not self.arquivo_obj.filename:
            raise ValueError("Nenhum arquivo enviado")
```

Se nenhum arquivo for enviado, o `ValueError` é lançado antes de qualquer coisa ser salva no banco. Esse erro é capturado na rota do `app.py` e exibido como mensagem flash para o usuário.

---

## Duas camadas de validação

A validação de arquivo funciona em duas camadas complementares:

| Camada | Onde | Como |
|---|---|---|
| Frontend | `repositorio.html` | Atributo `required` no `<input type="file">` bloqueia o envio sem arquivo |
| Backend | `antes_de_salvar()` em `ArquivoDigital` | Lança `ValueError` caso a requisição chegue sem arquivo |

O frontend protege o usuário comum. O backend protege o sistema contra requisições feitas diretamente sem passar pelo formulário.

---

## Por que isso é Template Method e não apenas Polimorfismo

O Polimorfismo já existia no projeto antes — `preparar_dados()` era sobrescrito por cada subclasse. O Template Method **formaliza e estende** esse conceito:

- Define um **algoritmo completo** em `salvar()`, não só um método isolado
- Introduz **hooks** — pontos de extensão opcionais que não quebram nada se não forem sobrescritos
- Garante que a **ordem dos passos** nunca muda, independente de qual subclasse está sendo usada

```
Polimorfismo puro      →  subclasse reimplementa UM método
Template Method        →  superclasse define O ALGORITMO INTEIRO
                          e deixa pontos específicos em aberto
```

---

## Como estender no futuro

Para adicionar comportamento em qualquer subclasse, basta sobrescrever um dos hooks sem tocar no `salvar()`:

```python
class Resumo(ItemRepositorio):
    def depois_de_salvar(self):
        print(f"Resumo '{self.titulo}' salvo com sucesso!")  # log, notificação, etc.
```

O fluxo do `salvar()` permanece intacto para todas as outras classes.