# Refatoração com Proxy

## O que foi feito

O padrão estrutural **Proxy** foi aplicado para centralizar o acesso ao banco de dados. Antes, cada rota do `app.py` abria e fechava sua própria conexão SQLite diretamente, repetindo o mesmo bloco de código em todos os lugares. Agora, um único objeto `db` intermedia todo o acesso, adicionando logging sem que as rotas precisem saber disso.

---

## Por que usar Proxy aqui

O acesso ao banco era feito assim em praticamente toda rota:

```python
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("SELECT ...")
conn.commit()
conn.close()
```

Isso gerava três problemas:

- **Repetição** — o mesmo bloco de abrir/fechar conexão espalhado por dezenas de rotas
- **Acoplamento direto** — as rotas conheciam detalhes de implementação do SQLite
- **Nenhum ponto central** — para adicionar logging, validação ou trocar de banco no futuro, seria necessário alterar cada rota individualmente

O Proxy resolve isso ao interpor um objeto entre quem pede os dados (a rota) e quem realmente acessa o banco (a classe `Database`). A rota não percebe a diferença — ela só chama `.buscar()` ou `.executar()`.

---

## Estrutura criada

### `database.py`

```python
class Database:
    """Objeto real — acesso direto ao banco"""
    def buscar(self, query, params=()):
        conn = sqlite3.connect('database.db')
        result = conn.cursor().execute(query, params).fetchall()
        conn.close()
        return result
    # buscar_um() e executar() seguem a mesma lógica


class DatabaseProxy:
    """Proxy — intercepta e adiciona comportamento extra"""
    def __init__(self):
        self._db = Database()

    def buscar(self, query, params=()):
        print(f"[LOG] SELECT: {query[:60]}")
        return self._db.buscar(query, params)
    # buscar_um() e executar() seguem a mesma lógica


db = DatabaseProxy()  # instância usada por todas as rotas
```

---

## O que mudou nas rotas

### Antes
```python
@app.route('/jardim')
@login_required
def jardim():
    conn = sqlite3.connect('database.db')
    plantas = conn.cursor().execute(
        "SELECT id, tipo_planta FROM jardim WHERE usuario_id = ? ORDER BY posicao ASC",
        (current_user.id,)
    ).fetchall()
    conn.close()
    return render_template('jardim.html', plantas=plantas)
```

### Depois
```python
from database import db

@app.route('/jardim')
@login_required
def jardim():
    plantas = db.buscar(
        "SELECT id, tipo_planta FROM jardim WHERE usuario_id = ? ORDER BY posicao ASC",
        (current_user.id,)
    )
    return render_template('jardim.html', plantas=plantas)
```

A rota não abre nem fecha conexão — só delega a consulta para o Proxy.

---

## Como o fluxo funciona

```
Rota chama db.buscar(...)
        ↓
DatabaseProxy intercepta e registra o log
        ↓
delega para Database (objeto real)
        ↓
retorna o resultado para a rota
```

A rota não sabe se está falando com o `Database` real ou com o `DatabaseProxy` — para ela, a interface é idêntica.

---

## Exceção: `init_db()`

A função `init_db()`, que cria as tabelas na inicialização do app, continua usando `sqlite3.connect` diretamente. Ela roda uma única vez, antes do `db` (Proxy) ser necessário, então não foi migrada.

---

## Como estender no futuro

Como toda a lógica de log já está centralizada no `DatabaseProxy`, adicionar uma nova camada de comportamento — como medir tempo de execução de cada query, ou bloquear certas operações — exige alterar apenas essa classe, sem tocar em nenhuma rota:

```python
class DatabaseProxy:
    def buscar(self, query, params=()):
        inicio = time.time()
        resultado = self._db.buscar(query, params)
        print(f"[LOG] SELECT levou {time.time() - inicio:.4f}s")
        return resultado
```