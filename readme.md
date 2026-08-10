# Sistema de Gestão do PAC UFPI

Plataforma web para cadastrar, validar, consolidar e acompanhar as demandas do Plano Anual de Contratações da UFPI.

O projeto utiliza:

* **Django** e **Django REST Framework** no back-end;
* **React** com **Vite** no front-end;
* **Bootstrap** para a interface;
* **PostgreSQL** como banco de dados;
* **Docker** para execução e implantação.

## Como instalar e rodar o projeto

### Pré-requisitos

Antes de iniciar, instale:

* Python 3.11 ou superior;
* Node.js 20 ou superior;
* npm;
* Git;
* PostgreSQL.

### 1. Clone o repositório

Clone o repositório e entre na pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd PAC-UFPI-Final
```

Substitua `<URL_DO_REPOSITORIO>` pela URL do repositório.

### 2. Crie e ative o ambiente virtual

No Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

No Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências do back-end

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

No Windows:

```bash
copy .env.example .env
```

No Linux/macOS:

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme as configurações do ambiente.

### 5. Configure o PostgreSQL

Certifique-se de que o servidor PostgreSQL esteja instalado e em execução.

O projeto utiliza as configurações definidas no arquivo `.env` para estabelecer a conexão com o banco de dados.

Antes de executar as migrações, confirme que o PostgreSQL está disponível e que as credenciais configuradas no `.env` estão corretas.

### 6. Execute as migrações

Entre na pasta do back-end:

```bash
cd pac
```

Execute as migrações:

```bash
python manage.py migrate
```

Para criar um usuário administrador:

```bash
python manage.py createsuperuser
```

### 7. Inicie o back-end

```bash
python manage.py runserver
```

Por padrão, a API ficará disponível em:

```text
http://localhost:8000
```

### 8. Execute o front-end

Em outro terminal, entre na pasta do projeto:

```bash
cd PAC-UFPI-Final\frontend
```

Instale as dependências:

```bash
npm install
```

Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

Por padrão, o front-end ficará disponível em:

```text
http://localhost:5173
```

## Testes

### Back-end

Na pasta `pac`:

```bash
python manage.py test
```

### Front-end

Na pasta `frontend`:

```bash
npm test
```

## Verificação de código

O projeto utiliza ferramentas de lint para manter a qualidade e padronização do código.

### Python — Ruff

Na raiz do projeto:

```bash
ruff check pac
```

Para corrigir automaticamente os problemas que podem ser corrigidos pelo Ruff:

```bash
ruff check pac --fix
```

Caso o Ruff ainda não esteja instalado no ambiente virtual:

```bash
python -m pip install ruff
```

### React — ESLint

Na pasta `frontend`:

```bash
npm run lint
```

## Como usar o projeto

Depois de iniciar o back-end e o front-end, acesse:

```text
http://localhost:5173
```

Após realizar o login, o sistema permite utilizar os principais módulos para:

* cadastrar demandas;
* consultar e gerenciar itens do catálogo;
* validar ou devolver solicitações;
* acompanhar o fluxo das demandas;
* consultar indicadores no dashboard.

## Como contribuir

1. Faça um fork do projeto.
2. Crie uma branch para sua alteração.
3. Implemente a mudança.
4. Execute os testes.
5. Execute as verificações de lint.
6. Abra uma Pull Request descrevendo as alterações realizadas.

Para alterações maiores, recomenda-se abrir uma issue antes de iniciar o desenvolvimento para alinhar o escopo.

## Estrutura do projeto

```text
PAC-UFPI-Final/
├── pac/                    # Back-end Django
│   ├── apps/               # Aplicações do sistema
│   ├── config/             # Configurações do projeto
│   └── manage.py            # Gerenciador do Django
├── frontend/                # Aplicação React/Vite
├── docs/                    # Documentação do projeto
├── requirements.txt         # Dependências Python
├── ruff.toml                # Configuração do Ruff
├── Dockerfile               # Configuração da imagem Docker
└── .env.example             # Exemplo das variáveis de ambiente
```

## CI/CD

O projeto possui verificações automatizadas por meio do GitHub Actions.

As verificações incluem:

* testes do back-end com Python 3.11;
* testes do back-end com Python 3.12;
* lint do código Python utilizando Ruff;
* lint, testes e build do front-end React.

Antes de abrir uma Pull Request, recomenda-se executar localmente os testes e as verificações de lint para garantir que o código esteja em conformidade com o CI.

## Docker

O projeto possui configuração para execução utilizando Docker.

A configuração de Docker pode ser utilizada para facilitar a implantação da aplicação em ambientes que suportem containers.

Consulte os arquivos de configuração do projeto para verificar os serviços e parâmetros disponíveis para o ambiente de execução.
