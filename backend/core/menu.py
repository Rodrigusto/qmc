def get_menu():
    return [
        {
            "section": None,
            "items": [
                {
                    "label": "Dashboard",
                    "icon": "⊞",
                    "url": "/",
                },
            ],
        },
        {
            "section": "Estoque",
            "items": [
                {
                    "label": "Ingredientes",
                    "icon": "🥬",
                    "url": "/ingredientes/",
                },
                {
                    "label": "Fornecedores",
                    "icon": "🚚",
                    "url": "/fornecedores/",
                },
                {
                    "label": "Compras",
                    "icon": "🛒",
                    "url": "/compras/",
                },
                {
                    "label": "Estoque",
                    "icon": "📦",
                    "url": "/estoque/",
                },
            ],
        },
        {
            "section": "Produtos",
            "items": [
                {
                    "label": "Produtos",
                    "icon": "🍔",
                    "url": "/produtos/",
                },
            ],
        },
        {
            "section": "Vendas",
            "items": [
                {
                    "label": "Vendas",
                    "icon": "📦",
                    "url": "/vendas/",
                },
                {
                    "label": "Clientes",
                    "icon": "👥",
                    "url": "/clientes/",
                },
                {
                    "label": "Canais de venda",
                    "icon": "📱",
                    "url": "/canais/",
                },
                {
                    "label": "Bairros",
                    "icon": "🏘️",
                    "url": "/bairros/",
                },
            ],
        },
        {
            "section": "Calculos e Análises",
            "items": [
                {
                    "label": "Custos fixos",
                    "icon": "💰",
                    "url": "/custos-fixos/",
                },
                {
                    "label": "Despesas",
                    "icon": "💸",
                    "url": "/despesas/",
                },
                {
                    "label": "GGF",
                    "icon": "📊",
                    "url": "/ggf/",
                },
                {
                    "label": "Cálculos de custo",
                    "icon": "⚙️",
                    "url": "/calculos/",
                },
                {
                    "label": "Previsão de vendas",
                    "icon": "🔮",
                    "url": "/previsao/",
                },
            ],
        },
    ]
