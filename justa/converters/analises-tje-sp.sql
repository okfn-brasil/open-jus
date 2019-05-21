SELECT "Total de registros:";
SELECT COUNT(*) FROM ore_tje_pr;
SELECT "Total de homens:";
SELECT COUNT(*) FROM ore_tje_pr WHERE genero = "M";
SELECT "Total de mulheres:";
SELECT COUNT(*) FROM ore_tje_pr WHERE genero = "F";

SELECT "Total de registros sem gênero:";
SELECT COUNT(*) FROM ore_tje_pr WHERE genero = "";
SELECT "Quantidade de nomes com gênero em branco:";
SELECT COUNT(nome) FROM ore_tje_pr WHERE genero = "";

SELECT "Rendimento bruto médio por gênero:";
SELECT genero, AVG(rendimento_bruto) FROM ore_tje_pr GROUP BY genero;
