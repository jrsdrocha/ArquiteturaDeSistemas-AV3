# Banco

API para cadastro de cliente com conta, transferencia entre contas e consulta de extrato.

## Rodar o servidor

Na raiz do projeto:

```bash
./venv/bin/uvicorn app.main:app --reload
```

URL base:

```text
http://127.0.0.1:8000
```

Documentacao interativa:

```text
http://127.0.0.1:8000/docs
```

## 1. Cadastro completo de pessoa fisica

Cria login, cliente individual e conta em uma unica chamada.

```http
POST http://127.0.0.1:8000/accounts/individual/register
```

```json
{
  "username": "maria3",
  "password": "123456",
  "full_name": "Maria Silva",
  "cpf": "12345678903",
  "account_number": "0003",
  "balance": 100.00
}
```

## 2. Cadastro completo de empresa

Cria login, cliente corporativo e conta em uma unica chamada.

```http
POST http://127.0.0.1:8000/accounts/corporate/register
```

```json
{
  "username": "empresa4",
  "password": "123456",
  "company_name": "Empresa LTDA",
  "cnpj": "12345678000194",
  "account_number": "0004",
  "balance": 50.00
}
```

## 3. Transferencia entre contas

Transfere dinheiro usando o numero da conta.

```http
POST http://127.0.0.1:8000/transactions/transfer/by-account-number
```

```json
{
  "source_account_number": "0003",
  "destination_account_number": "0004",
  "amount": 25.00
}
```

## 4. Extrato da conta

Consulta saldo e historico de transferencias da conta.

```http
GET http://127.0.0.1:8000/transactions/statement/0003
```

Exemplo de resposta:

```json
{
  "account_number": "0003",
  "balance": "75.00",
  "transactions": [
    {
      "transaction_id": 1,
      "direction": "SENT",
      "amount": "25.00",
      "source_account_number": "0003",
      "destination_account_number": "0004",
      "transaction_type": "TRANSFER"
    }
  ]
}
```

Para consultar a conta que recebeu:

```http
GET http://127.0.0.1:8000/transactions/statement/0004
```

Nesse caso, a transacao aparece com:

```json
{
  "direction": "RECEIVED"
}
```

## Observacoes

- `username`, `cpf`, `cnpj` e `account_number` nao podem repetir.
- Use novos numeros de conta se `0001`, `0002`, `0003` ou `0004` ja existirem no banco.
- O saldo inicial pode ser `0.00` ou maior.
