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
                    "label": "Compras",
                    "icon": "🛒",
                    "url": "/compras/",
                },
                {
                    "label": "Estoque",
                    "icon": "📦",
                    "url": "/estoque/",
                },
                {
                    "label": "Fornecedores",
                    "icon": "🚚",
                    "url": "/fornecedores/",
                },
            ],
        },
        {
            "section": "Produtos",
            "items": [
                {
                    "label": "Produtos",
                    "icon": "📦",
                    "url": "/produtos/",
                }
            ],
        },
        {
            "section": "Calculos e Análises",
            "items": [
                {
                    "label": "Custos fixos",
                    "icon": "💰",
                    "url": "/admin/calculations/fixedcost/",
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
    ]
