# Refatoração com Strategy

## O que foi feito

O padrão **Strategy** foi aplicado na lógica de escolha de planta ao finalizar uma sessão no timer. A lógica que estava hardcoded diretamente na rota foi extraída para classes independentes no arquivo `strategies.py`.

---

## O que mudou

### Antes — lógica hardcoded na rota
```python
@app.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    if request.method == 'POST':
        duracao = int(request.form.get('duracao', 0))
        planta = random.choice(["Carvalho", "Cerejeira", "Cacto"])  # ← hardcoded
        ...
```

### Depois — rota delega para a estratégia
```python
from strategies import EstrategiaPorTempo

@app.route('/timer', methods=['GET', 'POST'])
@login_required
def timer():
    if request.method == 'POST':
        duracao = int(request.form.get('duracao', 0))
        estrategia = EstrategiaPorTempo()
        planta = estrategia.escolher(duracao)  # ← delegado
        ...
```

---

## O arquivo `strategies.py`

```python
import random
from abc import ABC, abstractmethod

class EstrategiaPlanta(ABC):
    @abstractmethod
    def escolher(self, duracao):
        pass

class EstrategiaAleatoria(EstrategiaPlanta):
    def escolher(self, duracao):
        return random.choice(["Carvalho", "Cerejeira", "Cacto"])

class EstrategiaPorTempo(EstrategiaPlanta):
    def escolher(self, duracao):
        if duracao >= 3600:
            return "Carvalho"   # 1h ou mais
        elif duracao >= 1800:
            return "Cerejeira"  # 30min ou mais
        else:
            return "Cacto"      # menos de 30min
```

---

## As estratégias disponíveis

| Classe | Comportamento |
|---|---|
| `EstrategiaAleatoria` | Escolhe uma planta aleatória independente do tempo |
| `EstrategiaPorTempo` | Escolhe a planta com base na duração da sessão estudada |

---

## Como o padrão funciona

A rota sempre chama `.escolher(duracao)` da mesma forma, sem saber qual algoritmo está sendo executado internamente:

```
timer POST
  │
  ├── EstrategiaAleatoria.escolher(duracao)  →  random.choice(...)
  │
  └── EstrategiaPorTempo.escolher(duracao)   →  if duracao >= 3600...
```

Trocar a estratégia é uma mudança de uma linha na rota — o resto do código não toca em nada.

---

## Por que `duracao` está em todas as assinaturas

A classe base define o contrato com `duracao` como parâmetro. Todas as subclasses precisam respeitar essa assinatura, mesmo que não usem o parâmetro internamente — como é o caso de `EstrategiaAleatoria`.

Isso é o polimorfismo em ação: a rota sempre chama `.escolher(duracao)` da mesma forma independente de qual estratégia está instanciada.

---

## Como estender no futuro

Para adicionar uma nova lógica de escolha, basta criar uma nova classe herdando de `EstrategiaPlanta`:

```python
class EstrategiaPorDiaSemana(EstrategiaPlanta):
    def escolher(self, duracao):
        from datetime import datetime
        dia = datetime.now().weekday()
        if dia == 0:  # segunda-feira
            return "Carvalho"
        elif dia == 4:  # sexta-feira
            return "Cerejeira"
        else:
            return "Cacto"
```

E trocar na rota:

```python
estrategia = EstrategiaPorDiaSemana()
planta = estrategia.escolher(duracao)
```

A rota, a superclasse e as outras estratégias **não precisam de nenhuma modificação**.