# Publicação da demonstração no Streamlit Community Cloud

Este repositório tem **dois modos separados**:

- **Produção local de desenvolvimento:** `DEMO_MODE` ausente ou desabilitado → consulta o PostgreSQL usando `DATABASE_URL`, via SQLAlchemy/Pandas. Requer Docker ou banco configurado.
- **Demonstração pública:** `DEMO_MODE=true` → gera dados totalmente fictícios e determinísticos em memória. **Não conecta a banco de dados**, não utiliza credenciais e não publica informações reais.

O modo demo tem o mesmo layout e indicadores do modo PostgreSQL, porém sua fonte é sintética. É uma vitrine visual, não uma implantação de dados empresariais reais.

## Testar modo demo sem Docker

No Linux/CachyOS (terminal Fish), dentro do repositório:

```fish
git pull origin main
source .venv/bin/activate.fish
python -m pip install -r requirements.txt
env DEMO_MODE=true python -m streamlit run app.py
```

Abra http://localhost:8501.

Para voltar ao PostgreSQL, encerre o Streamlit (Ctrl+C) e execute sem a variável:

```fish
docker compose up -d
python -m streamlit run app.py
```

## Publicar

1. Acesse https://share.streamlit.io/ e entre com GitHub.
2. Selecione **Create app**, depois **Yup, I have an app**.
3. Selecione o repositório `jmrzd/Enterprise-Analytics-Dashboard`.
4. Branch: `main`. Arquivo principal (entrypoint): `app.py`.
5. Em **Advanced settings → Secrets**, adicione SOMENTE a configuração abaixo (não insira credenciais de bancos nesta versão pública):

   ```toml
   DEMO_MODE = "true"
   ```

6. Clique em **Deploy**. Depois de publicado, copie a URL gerada na plataforma (terminada em `.streamlit.app`) e adicione ao GitHub e ao currículo.

Não há link público até que a implantação seja concluída na conta Streamlit do proprietário.

## Segurança

- Mantenha `DATABASE_URL`, `.env` e credenciais fora do GitHub. `.streamlit/secrets.toml` está no `.gitignore`.
- Não utilize dados de clientes ou colaboradores reais em uma aplicação pública sem autenticação, controle de acesso, autorização e aprovação adequada.
- A aplicação informa na barra lateral se está em **modo demo** ou **PostgreSQL**. As visualizações são demonstrativas, não indicadores de uma empresa real.
- O repositório contém SQL e um banco local funcional; a demonstração pública não substitui o trabalho de integração SQL e Power BI.

## Integração Power BI

O módulo Power BI permite baixar dados agregados em CSV para importar no Power BI Desktop. Não foi criado arquivo `.pbix`, nem publicado relatório no Power BI Service.
