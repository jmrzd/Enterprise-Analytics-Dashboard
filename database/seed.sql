INSERT INTO departamentos (id,nome) VALUES (1,'Vendas'),(2,'Financeiro'),(3,'Recursos Humanos'),(4,'Tecnologia') ON CONFLICT (id) DO NOTHING;
INSERT INTO funcionarios (id,nome,departamento_id,salario,admissao,desligamento) VALUES
 (1,'Ana Silva',1,4500,'2024-02-01',NULL),
 (2,'Bruno Costa',2,5200,'2023-05-10',NULL),
 (3,'Carla Lima',3,4800,'2025-01-15',NULL),
 (4,'Diego Rocha',4,6500,'2024-08-20',NULL),
 (5,'Eva Martins',1,3900,'2024-04-10','2025-11-30') ON CONFLICT (id) DO NOTHING;
INSERT INTO clientes (id,nome,cidade) VALUES (1,'Mercado Sol','Rio de Janeiro'),(2,'Loja Horizonte','Niterói'),(3,'Comercial Azul','Duque de Caxias') ON CONFLICT (id) DO NOTHING;
INSERT INTO produtos (id,nome,categoria,custo_unitario,preco_unitario) VALUES
 (1,'Notebook','Tecnologia',2200,3400),(2,'Monitor','Tecnologia',600,950),
 (3,'Cadeira','Escritório',420,750),(4,'Teclado','Acessórios',80,160) ON CONFLICT (id) DO NOTHING;
INSERT INTO pedidos (id,cliente_id,data_pedido,status) VALUES
 (1,1,'2026-01-12','concluido'),(2,2,'2026-02-18','concluido'),
 (3,3,'2026-03-05','concluido'),(4,1,'2026-04-22','cancelado'),
 (5,2,'2026-05-14','concluido'),(6,3,'2026-06-09','pendente') ON CONFLICT (id) DO NOTHING;
INSERT INTO itens_pedido (id,pedido_id,produto_id,quantidade,preco_venda,custo_unitario) VALUES
 (1,1,1,2,3400,2200),(2,1,4,4,160,80),
 (3,2,2,3,950,600),(4,3,3,5,750,420),
 (5,4,1,1,3400,2200),(6,5,1,1,3400,2200),
 (7,5,2,2,950,600),(8,6,4,10,160,80) ON CONFLICT (id) DO NOTHING;
INSERT INTO lancamentos_financeiros (id,descricao,categoria,tipo,valor,data_vencimento,data_pagamento) VALUES
 (1,'Capital inicial','Aporte','receita',15000,'2026-01-05','2026-01-05'),
 (2,'Aluguel janeiro','Infraestrutura','despesa',2200,'2026-01-10','2026-01-10'),
 (3,'Serviços fevereiro','Serviços','receita',4100,'2026-02-15','2026-02-15'),
 (4,'Energia março','Infraestrutura','despesa',780,'2026-03-12','2026-03-12'),
 (5,'Marketing abril','Marketing','despesa',1200,'2026-04-20','2026-04-20'),
 (6,'Serviços maio','Serviços','receita',5200,'2026-05-15','2026-05-15'),
 (7,'Aluguel junho','Infraestrutura','despesa',2200,'2026-06-10',NULL) ON CONFLICT (id) DO NOTHING;
