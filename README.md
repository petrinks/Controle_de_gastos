# Controle Mensal de Despesas

**Versão:** v1  
**Suporte:** Apenas o modelo de CSV exportado pelo Nubank  

---

## Descrição

Este projeto fornece um script em Python para controlar suas despesas mensais a partir de um arquivo CSV (no formato padrão do Nubank) e gerar um relatório em planilha Excel com múltiplas abas:

1. **Transações** – todas as entradas do mês  
2. **Resumo** – total gasto por categoria  
3. **Parcelados** – detalhes de compras em parcelas  
4. **Recorrentes** – despesas que aparecem mais de uma vez no mês  

---

## Requisitos

- Python 3.8 ou superior  
- [pandas](https://pandas.pydata.org/)  
- [openpyxl](https://openpyxl.readthedocs.io/)  

Instale as dependências com:

```bash
pip install pandas openpyxl
