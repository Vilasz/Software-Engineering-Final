from tree_design import (
    DecisionNode,
    LeafNode,
    TreeBuilder,
    PreOrderIterator,
    DepthVisitor,
    CountLeavesVisitor,
)


def build_manual_tree() -> DecisionNode:
    """Cria uma árvore de decisão mockada para demonstração.
    """
    root = DecisionNode("Root")

    income = DecisionNode("Renda")
    age = DecisionNode("Idade")

    root.add_child(income)
    root.add_child(age)

    low_income = LeafNode("RendaBaixa", label="Negar crédito")
    high_income = LeafNode("RendaAlta", label="Aprovar crédito")
    income.add_child(low_income)
    income.add_child(high_income)

    young = LeafNode("Jovem", label="Analisar manualmente")
    history = DecisionNode("Historico")
    age.add_child(young)
    age.add_child(history)

    good_history = LeafNode("BomHist", label="Aprovar")
    bad_history = LeafNode("MauHist", label="Negar")
    history.add_child(good_history)
    history.add_child(bad_history)

    return root


def demo_state_pattern(root: DecisionNode) -> None:
    print("\n Demonstração do padrão State (TreeBuilder)")
    builder = TreeBuilder()

    # aplicamos algumas etapas de construção/poda no nó raiz
    builder.build_step(root)   
    builder.build_step(root)  
    builder.build_step(root)  
    builder.build_step(root)


def demo_iterator(root: DecisionNode) -> None:
    print("\n Demonstração do padrão Iterator (PreOrderIterator)")
    for node in PreOrderIterator(root):
        # apenas para mostrar o tipo do nó durante a iteração
        node_type = type(node).__name__
        print(f"[Demo Iterator] Nó visitado: {node.name} ({node_type})")


def demo_visitors(root: DecisionNode) -> None:
    print("\n Demonstração do padrão Visitor")

    depth_visitor = DepthVisitor()
    print("[Demo Visitor] Iniciando Visitor de profundidade.")
    root.accept(depth_visitor)
    print("[Demo Visitor] Profundidade não é realmente calculada")

    leaves_visitor = CountLeavesVisitor()
    print("\n[Demo Visitor] Iniciando Visitor de contagem de folhas.")
    root.accept(leaves_visitor)
    print("[Demo Visitor] Quantidade de folhas não é realmente calculada")



if __name__ == "__main__":
    print("### Demo da Árvore de Decisão (Mockada) ###")

    root_node = build_manual_tree()

    demo_state_pattern(root_node)
    demo_iterator(root_node)
    demo_visitors(root_node)
