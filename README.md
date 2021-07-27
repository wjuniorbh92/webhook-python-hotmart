# webhook-python-hotmart
## Webhook Hotmart

Esse é um projeto criado com proposito de consumir o **webhook** da API da **hotmart** usando o Flask.

O intuito do projeto é recebe um POST do **hotmart** em um caminho "www.seudominio.com/**webhook**"

Ele verifica o campo de hottok(key unica enviada pelo hotmart)

Se o hottok == ao que você configurou no **config.json.**

- Envia todos os dados que você escolheu no array **keyDatabase** para banco de dados SQL que foi configurado no **config.json.**
- Dependendo do status envia um email para o cliente usando o **Flask Mail** e da um update num Field no seu banco de dados, por exemplo **cliente_pago = true/false.**

Se o hottok ≠  ao que você configurou no **config.json.**

- Retorna um erro para o hotmart

O projeto ja esta pronto para deploy em um server como o Heroku,DigitalOcean,AWS.