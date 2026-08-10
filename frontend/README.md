# PAC UFPI — Frontend

Aplicação web em React + Vite para o Sistema de Gestão do Plano Anual de Contratações da UFPI.

## Stack

- React
- Vite
- React Router
- Bootstrap 5 + Bootstrap Icons
- Vitest + Testing Library
- ESLint

## Estrutura

`src/api` centraliza o acesso à API Django; `src/auth` controla a sessão; `src/pages` contém as telas do fluxo do PAC; `src/components` concentra componentes compartilhados.

## Executar

Com o backend Django rodando em `http://localhost:8000`:

```bash
npm ci
npm run dev
```

O frontend fica normalmente em `http://localhost:5173`.

Se a API estiver em outro endereço, crie `.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
```

## Verificação antes de entregar

```bash
npm run lint
npm test
npm run build
```

O frontend usa a sessão do Django por cookies e envia o token CSRF nas operações que alteram dados.

## Fluxo implementado

Login → Dashboard → Demandas → Itens → Envio para validação → Validação administrativa → DFD → Consolidação.

As telas administrativas ficam protegidas pela permissão `is_staff` retornada pela API.
