import pandas as pd
import re
import argparse

# Mapeamento de termos para categorias. Ajuste conforme suas necessidades.
MAPPINGS = {
    'mercado': 'Supermercado',
    'posto': 'Combustível',
    'uber': 'Transporte',
    'ifood': 'Alimentação',
    # Adicione aqui suas próprias regras de mapeamento
}


def load_csv(path: str) -> pd.DataFrame:
    """
    Carrega um CSV de transações, tentando separador ',' e ';'.
    """
    try:
        df = pd.read_csv(path)
    except Exception:
        df = pd.read_csv(path, sep=';')
    return df


def parse_parcelas(title: str):
    """
    Extrai parcela atual e total de parcelas a partir do título.
    Formatos suportados: '2/12', '2 de 12', etc.
    Retorna (parcela_atual, parcelas_totais) ou (None, None).
    """
    pattern = r"(\d+)[/| ](\d+)"
    match = re.search(pattern, title)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def categorize(title: str) -> str:
    """
    Classifica um título em uma categoria baseada em termos-chave.
    Itens não mapeados vão para 'Outros'.
    """
    lower = title.lower()
    for termo, cat in MAPPINGS.items():
        if termo in lower:
            return cat
    return 'Outros'


def main(input_csv: str, output_excel: str):
    # 1. Carregar dados
    df = load_csv(input_csv)

    # 2. Conversão de tipos
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)

    # 3. Detectar parcelados
    df[['parcela_atual', 'parcelas_totais']] = df['title'].apply(
        lambda x: pd.Series(parse_parcelas(x))
    )
    df['is_parcelado'] = df['parcela_atual'].notnull()

    # 4. Classificação em categorias
    df['categoria'] = df['title'].apply(categorize)

    # 5. Resumo por categoria
    resumo = df.groupby('categoria')['amount'].sum().reset_index()
    resumo = resumo.sort_values(by='amount', ascending=False)

    # 6. Detalhe de parcelados
    parcelados = df[df['is_parcelado']].copy()
    if not parcelados.empty:
        parcelados['valor_parcela'] = parcelados['amount']
        parcelados['parcelas_restantes'] = (
            parcelados['parcelas_totais'] - parcelados['parcela_atual']
        )
        parcelados['total_comprometido'] = (
            parcelados['valor_parcela'] * parcelados['parcelas_totais']
        )

    # 7. Identificação de recorrentes
    contagem = df['title'].value_counts()
    recorrentes = contagem[contagem > 1].reset_index()
    recorrentes.columns = ['title', 'frequencia']
    recorrentes = recorrentes.merge(df, on='title')[
        ['date', 'title', 'amount', 'frequencia']
    ]

    # 8. Exportação para Excel
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transações', index=False)
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
        if not parcelados.empty:
            parcelados.to_excel(writer, sheet_name='Parcelados', index=False)
        if not recorrentes.empty:
            recorrentes.to_excel(writer, sheet_name='Recorrentes', index=False)

    print(
        f"Planilha gerada em {output_excel} com abas: Transações, Resumo, Parcelados, Recorrentes")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Controle mensal de despesas a partir de CSV'
    )
    parser.add_argument(
        '-i', '--input_csv',
        default='./docs/exemplo.csv',
        help='(opcional) CSV de entrada — padrão: ../docs/exemplo.csv'
    )
    parser.add_argument(
        '-o', '--output_excel',
        default='./out/arquivoDeSaida.xlsx',
        help='(opcional) Excel de saída — padrão: ../out/arquivoDeSaida.xlsx'
    )
    args = parser.parse_args()
    main(args.input_csv, args.output_excel)
