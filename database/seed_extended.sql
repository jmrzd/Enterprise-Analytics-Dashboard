-- Extensão idempotente e EXCLUSIVAMENTE FICTÍCIA do dataset.
-- Pode ser executada em bancos existentes sem apagar os dados iniciais.
BEGIN;
INSERT INTO clientes(id,nome,cidade) VALUES
 (10,'Alfa Distribuição','Rio de Janeiro'),(11,'Norte Comércio','Petrópolis'),
 (12,'Central Office','Nova Iguaçu'),(13,'Ponto Digital','Niterói'),
 (14,'Loja Aurora','Duque de Caxias'),(15,'Casa Nova','Rio de Janeiro')
 ON CONFLICT (id) DO NOTHING;
INSERT INTO produtos(id,nome,categoria,custo_unitario,preco_unitario) VALUES
 (10,'Mouse sem fio','Acessórios',38,99),(11,'Webcam HD','Tecnologia',125,249),
 (12,'Mesa Office','Escritório',310,589),(13,'Headset Pro','Acessórios',120,269),
 (14,'Hub USB-C','Acessórios',65,149),(15,'Impressora Wi-Fi','Tecnologia',520,899)
 ON CONFLICT (id) DO NOTHING;
INSERT INTO funcionarios(id,nome,departamento_id,salario,admissao,desligamento) VALUES
 (100,'Luiza Ferreira',1,4200,'2025-04-03',NULL),
 (101,'Marcos Ribeiro',1,4700,'2025-08-19',NULL),
 (102,'Isabela Gomes',1,5100,'2026-02-03',NULL),
 (103,'Pedro Almeida',2,5400,'2025-11-05',NULL),
 (104,'Rafaela Santos',2,4900,'2026-04-16',NULL),
 (105,'Tiago Castro',3,5100,'2026-01-12',NULL),
 (106,'Bianca Mendes',3,4400,'2025-12-01',NULL),
 (107,'Felipe Barros',4,7200,'2025-06-17',NULL),
 (108,'Fernanda Oliveira',4,6900,'2026-03-23',NULL),
 (109,'Gabriel Vieira',4,6200,'2025-09-09',NULL),
 (110,'Júlia Marques',1,3600,'2025-01-10','2026-04-30'),
 (111,'Rodrigo Pinto',2,5300,'2025-03-02','2026-07-31')
 ON CONFLICT (id) DO NOTHING;

INSERT INTO pedidos(id,cliente_id,data_pedido,status)
SELECT 1000+n,
       (ARRAY[1,2,3,10,11,12,13,14,15])[(n % 9)+1],
       DATE '2025-11-01' + n*2,
       CASE WHEN n%19=0 THEN 'cancelado' WHEN n%13=0 THEN 'pendente' ELSE 'concluido' END
FROM generate_series(0,180) AS n
ON CONFLICT (id) DO NOTHING;

INSERT INTO itens_pedido(id,pedido_id,produto_id,quantidade,preco_venda,custo_unitario)
SELECT 4000+n*2, 1000+n,
       (ARRAY[1,2,3,4,10,11,12,13,14,15])[(n % 10)+1],
       1 + (n%4), pr.preco_unitario, pr.custo_unitario
FROM generate_series(0,180) AS n
JOIN produtos pr ON pr.id=(ARRAY[1,2,3,4,10,11,12,13,14,15])[(n%10)+1]
ON CONFLICT (id) DO NOTHING;

INSERT INTO itens_pedido(id,pedido_id,produto_id,quantidade,preco_venda,custo_unitario)
SELECT 4001+n*2, 1000+n,
       (ARRAY[1,2,3,4,10,11,12,13,14,15])[((n+3)%10)+1],
       1 + (n%3), pr.preco_unitario, pr.custo_unitario
FROM generate_series(0,180) AS n
JOIN produtos pr ON pr.id=(ARRAY[1,2,3,4,10,11,12,13,14,15])[((n+3)%10)+1]
ON CONFLICT (id) DO NOTHING;

INSERT INTO lancamentos_financeiros(id,descricao,categoria,tipo,valor,data_vencimento,data_pagamento)
SELECT 1000+n,
  CASE WHEN n%3=0 THEN 'Serviço contratado - demo ' ELSE 'Despesa operacional - demo ' END || n,
  CASE WHEN n%3=0 THEN 'Serviços' WHEN n%4=0 THEN 'Marketing' WHEN n%4=1 THEN 'Infraestrutura' ELSE 'Operacional' END,
  CASE WHEN n%3=0 THEN 'receita' ELSE 'despesa' END,
  CASE WHEN n%3=0 THEN (3600+n%12*380)::numeric
       ELSE (450+n%9*190)::numeric END,
  DATE '2025-11-01' + n*3,
  CASE WHEN n%17=0 THEN NULL ELSE DATE '2025-11-01' + n*3 END
FROM generate_series(0,119) AS n
ON CONFLICT (id) DO NOTHING;
COMMIT;
