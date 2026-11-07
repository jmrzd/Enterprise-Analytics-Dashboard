# Enterprise Analytics — versão Vercel

Interface web futurista para portfólio, com **FastAPI (Python)**, HTML/CSS/JavaScript e visualizações SVG sem bibliotecas externas de gráficos.

> **Atenção:** este deploy usa **dados 100% sintéticos**. Não há conexão com dados reais, nem login. A aplicação original Streamlit + PostgreSQL + Pandas e os scripts Power BI continuam na raiz do repositório.

## Executar localmente

```bash
cd vercel-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Acesse http://127.0.0.1:8000.

## Endpoints

- `GET /` — interface responsiva.
- `GET /api/dashboard?period=30d|90d|180d|365d` — indicadores gerados em Python, em JSON.
- `GET /api/health` — status do serviço.
- `GET /api/docs` — documentação OpenAPI do FastAPI.

O endpoint gera dados sintéticos determinísticos por dia, com consistência entre vendas, produtos e clientes. Financeiro e RH são conjuntos separados e não devem ser interpretados como lucro líquido contábil.

## Publicação na Vercel

Configure o projeto da Vercel com:

- **Git Repository:** `jmrzd/Enterprise-Analytics-Dashboard`
- **Root Directory:** `vercel-app`
- **Framework Preset:** `FastAPI`
- **Production Branch:** `main`
- **Environment variables:** nenhuma para o modo demo.

A Vercel instala `vercel-app/requirements.txt` e expõe a aplicação FastAPI em `app.py`. Não aponte a Vercel para o Streamlit da raiz. Os arquivos HTML/CSS/JS ficam em `templates/` (NÃO em `public/`) para evitar que a CDN sirva `index.html` sem passar pelo FastAPI. A resposta `/` inclui CSS, JavaScript e dados iniciais inline. Cabeçalho de diagnóstico: `X-Dashboard-Render: fastapi-inline-v3`.

## Testes

```bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
```

## Próximos passos

- Implementar API autenticada e conexão segura com PostgreSQL para dados reais.
- Adicionar controle de acesso por função antes de disponibilizar RH.
- Construir o arquivo Power BI `.pbix` e publicar relatórios.
- Adicionar testes de ponta a ponta no navegador.

## Assistente de IA (OpenAI e Gemini)

O dashboard inclui um assistente flutuante **✦ Assistente IA** e uma tela **Configurações IA**. O visitante escolhe um provedor e usa sua própria chave de API para perguntas livres. Estão disponíveis também respostas locais e exatas sem chave (faturamento, lucro bruto, margem, ticket médio, ranking de produtos, caixa, RH e suporte à navegação).

- O navegador guarda a chave **somente na memória desta aba** até fechar/recarregar. Não usa cookies, \`localStorage\`, \`sessionStorage\` ou banco de dados.
- Para perguntas livres, o navegador envia a chave por **HTTPS** à rota \`POST /api/chat\`. O FastAPI encaminha-a somente ao endereço fixo do provedor escolhido; a chave não aparece na URL nem é salva, retornada ou escrita em logs pelo código da aplicação.
- **Importante:** o operador do site controla o backend e pode tecnicamente interceptar requisições. Não peça que visitantes usem chaves de alto privilégio. Recomende criar chave com gastos limitados e uso restrito, usando apenas sites confiáveis.
- O OpenAI Responses API usa \`gpt-5.4-mini\` com \`store: false\`. O Gemini API usa \`gemini-3.5-flash-lite\` com \`x-goog-api-key\`. O acesso depende da conta do visitante, disponibilidade de modelos e possíveis cobranças.
- Os provedores externos recebem apenas a pergunta, um trecho recente da conversa e os **indicadores sintéticos do dashboard**; não recebem dados pessoais reais nem acesso ao PostgreSQL.
- O endpoint aceita perguntas de até 900 caracteres, histórico de no máximo seis mensagens, tempo limite de requisição, e não permite URLs de destino fornecidas pelo visitante. Erros do provedor são filtrados para não vazar credenciais.
- Ainda não há autenticação, rate limiting distribuído ou suporte a dados empresariais reais. **Não utilize chaves de produção ou dados privados.**

## Gráficos ampliados e interativos

A página ganhou opção de detalhamento **automático / semanal / mensal**, visões maiores, valores exatos sob o cursor ou via teclado, e botão **⛶** para ampliar gráficos. O cálculo das séries semanais é feito no Python a partir das mesmas vendas e lançamentos que alimentam os KPIs. Todos os resultados permanecem fictícios.

## Testes da integração

\`\`\`bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
\`\`\`

Os testes de IA são simulados, **sem usar chaves de terceiros nem realizar cobranças reais**. É necessário fazer uma pergunta com uma chave válida para validar ao vivo o acesso do provedor escolhido.


## Enterprise Analytics 2.0 — produto interativo

A versão Vercel agora inclui funcionalidades reais de exploração:

- **Visão Geral:** quatro insights executivos derivados de fórmulas transparentes, alertas demonstrativos e atalhos por módulo.
- **Vendas:** subabas Resumo, Produtos, Clientes e Performance; rankings, receitas e participação de clientes; clique em produtos/categorias para drill-down.
- **Financeiro:** subabas Fluxo de caixa, Despesas, Pendências e Simulador, com cálculos de cenários sem modificar dados originais.
- **RH:** subabas Equipe, Departamentos, Movimentações e Custos. A folha representa um snapshot mensal, não custo anual.
- **Power BI Studio:** seis endpoints reais de CSV, prévia tabular, medidas DAX, guia de importação, modelo de dados ilustrativo e ZIP completo.
- **Gráficos:** melhor escala visual, tooltips, ocultar/exibir séries clicando na legenda, opção de ampliar e explorar itens.
- **Assistente IA:** OpenAI / Gemini com chave temporária BYOK, e respostas locais para cálculos simples sem chave.

### APIs de análise e exportação

- \`GET /api/insights?period=90d\`: insights, alertas e fórmulas.
- \`POST /api/scenario\`: simulação matemática com \`price_pct\`, \`volume_pct\`, \`cost_pct\`, \`hires\`, \`expense_reduction_pct\`.
- \`GET /api/powerbi/kit?period=90d\`: ZIP com seis CSVs, \`medidas.dax\` e instruções.
- \`GET /api/powerbi/dax\`: biblioteca de medidas DAX.
- \`GET /api/powerbi/{dataset}?period=90d\`: CSV de \`vendas\`, \`financeiro\`, \`rh\`, \`produtos\`, \`clientes\` ou \`categorias\`.
- \`GET /api/dashboard?period=90d\`: dados do dashboard.
- \`POST /api/chat\`: perguntas via API com chave de uso temporário do próprio visitante.

### Como o simulador calcula

**Receita de cenário = receita de referência × (1 + ajuste de preço) × (1 + ajuste de volume)**.

**COGS de cenário = (receita − lucro bruto) × (1 + ajuste de custo) × (1 + ajuste de volume)**.

**Lucro bruto de cenário = receita de cenário − COGS de cenário**.

**Folha mensal ajustada = folha atual + contratações × custo salarial médio**.

A redução de despesas é aplicada à fonte independente de lançamentos financeiros; **não é somada ao lucro bruto**. As hipóteses são simplificadas. Não é uma previsão ou aconselhamento financeiro.

### Power BI — limites importantes

Os seis CSVs são **agregados sintéticos**. \`vendas\` e \`financeiro\` têm coluna \`mes_inicio\` que permite criar uma dimensão calendário. \`rh\` é uma fotografia da folha atual. O projeto ainda não fornece um relatório \`.pbix\` ou conexão Power BI Service publicada. O kit é um **ponto de partida funcional para criar seu próprio relatório no Power BI Desktop**.

### Verificação de qualidade

\`\`\`bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
node --check templates/upgrade.js
\`\`\`

Não forneça dados reais de clientes ou funcionários nem chaves de APIs sem restrições para a vitrine pública.


## Enterprise Analytics — Interface 3.0 (NOVA UI)

Uma camada visual e funcional adicional, sem alterar os dados nem a integração de IA:

- **Nova identidade futurista:** navegação glassmorphism com iluminação suave, indicadores com pequenos sparklines reais e destaque de aba ativa.
- **Gráficos de alta resolução:** curvas SVG suaves e dados reais do modo demo; alternância clicável entre **Linha / Área / Barras**, liga/desliga de séries, crosshair e tooltip com valores exatos. Zoom/ampliação original preservados.
- **Comparação verificável:** botão **Comparar períodos** mostra os dados do intervalo imediatamente anterior de igual duração (30/90/180 dias). O Python calcula os eventos com datas exatas, não subtrai meses incompletos. Na visão 365 dias, a comparação fica indisponível por falta de histórico.
- **Busca de comandos:** **Ctrl+K** abre pesquisa de módulos, produtos, clientes, cenários, Power BI e configurações IA com suporte a teclado.
- **Centro de alertas:** ícone no topo lista alertas já calculados sobre dados sintéticos com navegação direta para o módulo.
- **Subabas mais visíveis:** atalhos em formato de pílulas com estado ativo neon e fixação durante rolagem.
- **Reinício de navegação:** mudar de módulo retorna ao topo, em vez de manter a posição profunda de rolagem.

Os arquivos \`studio.css\` e \`studio.js\` são incorporados pelo FastAPI na resposta HTML, assim como os demais estilos e scripts. **Não** mova os arquivos para \`public/\`, pois isso pode reintroduzir a entrega de HTML sem CSS.

### Testes

\`\`\`bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/studio.js
\`\`\`

Dados do dashboard e alertas continuam 100% sintéticos. O centro de alertas não produz notificações reais e os cenários não são previsão financeira.


## Integrações self-service (etapa de testes, sem armazenar credenciais)

O menu **Integrações** do dashboard oferece um fluxo de três etapas:

1. **Origem:** PostgreSQL, MySQL, CSV, Excel (.xlsx) ou conexão de demonstração.
2. **Teste:** no exemplo fictício, resultado instantâneo sem senha; em CSV/Excel, upload de até 1,5 MB e visualização de até 12 linhas; em PostgreSQL/MySQL, teste HTTPS com senha temporária e TLS verificado, caso o administrador tenha ativado o recurso.
3. **Mapeamento:** escolher colunas de data, valor e categoria. Para planilhas, o sistema calcula totais **somente da amostra exibida**. Para bancos remotos, lista tabelas/colunas sem copiar registros.

### Ativar teste real de PostgreSQL/MySQL

**Importante:** no site público, testes SQL são desabilitados por padrão para impedir acesso indevido a hosts externos/internos. O proprietário pode habilitar de forma segura em **Vercel → Project → Settings → Environment Variables**, sem modificar código:

- \`INTEGRATION_ADMIN_TOKEN\`: segredo aleatório de **pelo menos 24 caracteres**, compartilhado apenas com administradores autorizados. Gere localmente: \`python -c "import secrets; print(secrets.token_urlsafe(32))"\`.
- \`INTEGRATION_ALLOWED_HOSTS\`: lista de hostnames **exatos** aprovada pelo administrador, separados por vírgula. Exemplo: \`db1.suaempresa.com,db2.suaempresa.com\`. Não inclui portas nem URLs. Endereços privados, loopback e reservados são bloqueados.
- Faça um **Redeploy** depois de salvar as variáveis na Vercel.

O responsável informa no formulário o host aprovado, a porta (5432/3306), nome do banco, usuário **somente leitura**, senha e token do administrador. A aplicação valida primeiro a autorização e o destino, exige TLS verificado, roda somente \`SELECT 1\` e consulta o catálogo \`information_schema.columns\` (máximo de 350 entradas). O teste não executa SQL fornecido pelo usuário, nem grava credenciais ou dados.

Para PostgreSQL, usa \`sslmode="verify-full"\`, que valida certificado e hostname. MySQL usa \`ssl.create_default_context()\`, verificando certificado e hostname. Bancos com certificados autoassinados exigem configuração de certificado e **não devem desabilitar a verificação TLS**.

**Vercel não se conecta automaticamente a um banco local** (\`localhost\`/rede privada). Para bancos corporativos, prefira uma implantação privada, gateway seguro ou VPN/autorização de rede aprovada, com autenticação e controle por empresa. **Nunca exponha diretamente um banco interno só para testar esta demonstração pública.**

### Privacidade e o que ainda não é feito

- Nada de senhas, tokens ou CSV/Excel no \`localStorage\`, repositório, banco de dados ou logs da aplicação.
- A senha é enviada apenas na requisição de teste via HTTPS e depois descartada. O operador do backend ainda controla o servidor; use apenas instalações de confiança.
- Arquivos são processados temporariamente em memória no servidor. **Não envie planilhas com dados pessoais/confidenciais para a vitrine pública.**
- As integrações **ainda não ficam salvas** nem alimentam automaticamente os painéis, porque isso exigiria autenticação empresarial, criptografia persistente de segredos, isolamento entre organizações, gestão de permissões e sincronização agendada.
- Suporte a SQL Server, OAuth e um conector persistente multiempresa são evoluções futuras.

**Endpoints:** \`GET /api/integrations/status\`, \`POST /api/integrations/test\` (autorizado), \`POST /api/integrations/file-preview\` (amostra de CSV/XLSX).


## Sincronização segura de bancos — piloto

A aba Integrações agora permite **sincronizar sob demanda totais mensais de uma tabela** de PostgreSQL ou MySQL. O resultado aparece **dentro de Integrações**, não substitui automaticamente os painéis fictícios de Vendas, Financeiro e RH.

### Configuração do administrador na Vercel

1. Abra Enterprise Analytics em Vercel → Settings → Environment Variables.
2. Crie **INTEGRATION_ADMIN_TOKEN** como segredo protegido de pelo menos 24 caracteres. Gere localmente com Python secrets.token_urlsafe(32); não compartilhe no chat nem no GitHub.
3. Crie **INTEGRATION_ALLOWED_HOSTS** com hostnames exatos e autorizados, separados por vírgula, por exemplo db1.suaempresa.com,db2.suaempresa.com (domínios meramente ilustrativos). Não inclua URLs, localhost ou endereços internos.
4. Aplique em Production e execute um Redeploy. Sem ambos os valores, o teste e a sincronização seguem desativados.
5. Crie um usuário SQL somente leitura e disponibilize uma conexão com certificado TLS válido, sem expor um banco interno apenas para usar o piloto.
6. Em Integrações escolha PostgreSQL/MySQL, informe host, porta, banco, usuário, senha e autorização do proprietário. Teste, selecione uma tabela e mapeie data, valor numérico e opcionalmente categoria.
7. Clique em **Sincronizar totais agora** para ler agregados mensais e até oito categorias. É possível ativar atualização a cada cinco minutos enquanto a aba estiver aberta.

O servidor não salva senhas, registros individuais ou snapshots. As credenciais são mantidas apenas em memória na aba por até dez minutos, removidas ao mudar de módulo. Essa expiração do navegador **não revoga** o token do administrador, que deve ser rotacionado periodicamente.

### O que ainda NÃO faz

- Não oferece autenticação empresarial ou isolamento de dados por organização.
- Não mantém conexão persistente, tarefas cron ou um banco central.
- Não atualiza automaticamente os outros módulos com os dados da empresa.
- Não envia métricas empresariais para o chatbot.

Para transformar o piloto em um SaaS corporativo é preciso login seguro, controle de acesso por empresa, cofre de credenciais, armazenamento privado, auditoria e uma rotina de sincronização agendada. Não conecte dados confidenciais ou pessoais à vitrine pública antes dessas etapas.

### Segurança adicionada

- Content Security Policy para JavaScript com nonce por página.
- Headers HSTS, X-Frame-Options DENY, nosniff, Referrer-Policy no-referrer e Permissions-Policy.
- Limites de tamanho para requisições, bloqueio de requisições de origem cruzada e Cache-Control no-store.
- TLS certificado e validado, host allowlist, bloqueio de IP privado/reservado e conexão de PostgreSQL fixada ao IP verificado.
- SQL somente leitura, identificadores validados no catálogo do banco, parâmetros SQL seguros, timeout e respostas agregadas.

Também recomendamos habilitar limitação de requisições e proteção contra abuso no Vercel Firewall/WAF, se disponível no plano. Consulte SECURITY.md.

**API:** POST /api/integrations/sync aceita uma tabela, colunas validadas e um período de 30/90/180/365 dias, exigindo autorização administrativa e host aprovado. A interface utiliza 90 dias no piloto.


## Layout adaptativo — smartphone, iPhone, Android, tablet e desktop

Esta versão mantém o visual neon futurista e adiciona dois assets finais em templates/responsive.css e templates/responsive.js, incorporados pelo FastAPI com o nonce da Content Security Policy.

**Mudanças de interface:**

- Mobile-first para até 960px (incluindo iPhone em modo paisagem e iPads compactos): menu lateral como gaveta com rolagem própria e bloqueio do fundo; botão de fechar acessível; navegação inferior rápida com Início, Vendas, Finanças, Integrações e Menu.
- Suporte a área segura de dispositivos Apple: viewport-fit=cover, safe-area-inset-top/bottom/left/right e unidades de viewport dinâmicas.
- Chatbot, menu de configurações, detalhes e busca de comandos ajustáveis à altura da viewport visual quando o teclado aparece; campos com fonte de 16px para evitar zoom automático do Safari.
- Gráficos neon com séries que podem ser roladas horizontalmente na própria área, sem alargar a página; valores exatos por toque; controles de tipo de gráfico e subabas acessíveis ao arrastar.
- Cards, tabelas, Power BI, cenários, formulário de integrações e ações responsivos; menos transições em dispositivos com preferência por redução de movimento.
- A experiência continua desktop-first em telas grandes, mantendo a barra lateral e o espaço de análise.

**Verificação automatizada:** o workflow Vercel Demo Quality inclui testes com Chromium e WebKit (engine usado pelo Safari) em 11 tamanhos: 320×690, 375×667, 390×844, 430×932, 932×430, 768×1024, 834×1194, 1024×768, 1280×800, 1440×900 e 1920×1080. Os testes verificam ausência de rolagem horizontal da página, navegação, subabas, fluxo demonstrativo de Integrações, visualização de chatbot e configurações e exceções JavaScript.

Em ambiente local, após instalar Playwright e um navegador, inicie FastAPI na porta 8765 e execute:

    python vercel-app/scripts/check_viewports.py --browser chromium
    python vercel-app/scripts/check_viewports.py --browser webkit

**Nota:** testes automatizados em Chromium/WebKit de desktop emulam tamanhos e toques; não substituem validação física de Safari no iPhone, Android e navegadores com recursos de acessibilidade variados.
