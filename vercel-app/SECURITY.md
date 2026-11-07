# Segurança — Integrações (piloto público)

## Ativação
O site permanece público e usa dados fictícios. Por padrão, operações remotas de banco estão desativadas. O proprietário habilita o serviço apenas quando configurar os segredos INTEGRATION_ADMIN_TOKEN e INTEGRATION_ALLOWED_HOSTS nas Environment Variables da Vercel, escopo Production, e executar Redeploy.

## Limitações
A autorização usa um token de operador, **não** é um login multiusuário ou multiempresa. Não distribua esse token a visitantes nem conecte dados pessoais de empresas à vitrine. Para produção corporativa é obrigatório autenticação OIDC/SSO, MFA, isolamento por tenant, autorização, auditoria, quotas, segredos criptografados, retenção definida e armazenamento durável.

As senhas e o token ficam somente na memória temporária da aba, nunca no localStorage ou repositório. O backend recebe a credencial durante requisições autorizadas sobre HTTPS, mas o operador do servidor e extensões maliciosas do navegador continuam sendo fatores de confiança. A janela de dez minutos é controle da interface e não revoga o token administrativo no servidor.

## Proteções técnicas
A aplicação valida origem do navegador, tamanho de requisições, hostnames aprovados, IPs públicos e certificado TLS. PostgreSQL tem IP público fixado em hostaddr preservando validação TLS do nome. MySQL tem TLS com verificação de hostname. O usuário SQL deve ter permissão somente SELECT. O SQL usa identificadores do catálogo, limita tipos de colunas e executa somente agregações com limites e timeout. Os dados da empresa não são armazenados.

O HTML utiliza CSP com nonces para scripts, proteção contra frames, HSTS, controle de cache e cabeçalhos de privacidade. O CSS exige a exceção unsafe-inline para estilos gerados pelo frontend legado. Não há rate limiting distribuído implementado pelo backend: habilite Vercel Firewall/WAF quando disponível.

## Operação
Use um banco autorizado e roteável publicamente com certificado confiável; não exponha um banco em VPN/rede privada só para usar esta demonstração. Se um segredo vazar, revogue e rotacione imediatamente. Revise logs da Vercel sem registrar payloads sensíveis.

Os testes automatizados validam negações de acesso, consistência dos agregados e headers. Isso não substitui pentest profissional ou aprovação corporativa.
