from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Iterator


class Node(ABC):
    """Componente base da árvore de decisão.

    Implementa parte do padrão Composite: cada nó pode ter filhos
    (exceto LeafNode, que bloqueia essa operação)
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._children: List["Node"] = []

    def add_child(self, child: "Node") -> None:
        print(f"[Composite] Adicionando filho '{child.name}' a '{self.name}'")
        self._children.append(child)

    def remove_child(self, child: "Node") -> None:
        print(f"[Composite] Removendo filho '{child.name}' de '{self.name}'")
        self._children.remove(child)

    def get_children(self) -> List["Node"]:
        # devolvemos uma cópia para evitar modificações externas diretas
        return list(self._children)


    def __iter__(self) -> "PreOrderIterator":
        """Permite iterar sobre a árvore usando: for node in root:"""
        return PreOrderIterator(self)

    @abstractmethod
    def accept(self, visitor: "Visitor") -> None:
        """Ponto de entrada do Visitor."""
        raise NotImplementedError


class DecisionNode(Node):
    """Nó interno da árvore (possui filhos)."""

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_decision_node(self)


class LeafNode(Node):
    """Nó folha da árvore (não possui filhos)."""

    def __init__(self, name: str, label: str) -> None:
        super().__init__(name)
        self.label = label

    # bloqueia a adição de filhos para manter a semântica de folha
    def add_child(self, child: "Node") -> None:  # type: ignore[override]
        raise RuntimeError("LeafNode não pode receber filhos.")

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_leaf_node(self)


class PreOrderIterator(Iterator[Node]):
    """
    Iterador em pré-ordem sobre a árvore.
    """

    def __init__(self, root: Node) -> None:
        self._stack: List[Node] = [root]

    def __next__(self) -> Node:
        if not self._stack:
            raise StopIteration

        node = self._stack.pop()
        print(f"[Iterator] Visitando nó: {node.name}")
        # adiciona filhos em ordem reversa para que o primeiro filho seja processado primeiro (LIFO)
        for child in reversed(node.get_children()):
            self._stack.append(child)
        return node


class Visitor(ABC):
    """Interface base para visitantes."""

    @abstractmethod
    def visit_decision_node(self, node: DecisionNode) -> None:
        raise NotImplementedError

    @abstractmethod
    def visit_leaf_node(self, node: LeafNode) -> None:
        raise NotImplementedError


class DepthVisitor(Visitor):
    """Versão mockada"""

    def __init__(self) -> None:
        self.description = "Visitor que simularia o cálculo da profundidade."

    def visit_decision_node(self, node: DecisionNode) -> None:
        print(
            f"[DepthVisitor] (mock) Entrando em DecisionNode '{node.name}'. "
            "Aqui eu desceria para os filhos para calcular a profundidade máxima."
        )
        for child in node.get_children():
            child.accept(self)

    def visit_leaf_node(self, node: LeafNode) -> None:
        print(
            f"[DepthVisitor] (mock) Cheguei em LeafNode '{node.name}' "
            f"(rótulo='{node.label}'). "
            "Aqui eu atualizaria a profundidade máxima"
        )



class CountLeavesVisitor(Visitor):
    """Versão mockada"""

    def __init__(self) -> None:
        self.description = "Visitor que simularia a contagem de folhas."

    def visit_decision_node(self, node: DecisionNode) -> None:
        print(
            f"[CountLeavesVisitor] Explorando DecisionNode '{node.name}'. "
            "Aqui eu percorreria os filhos para contar as folhas."
        )
        for child in node.get_children():
            child.accept(self)

    def visit_leaf_node(self, node: LeafNode) -> None:
        print(
            f"[CountLeavesVisitor] Encontrei LeafNode '{node.name}' "
            f"(rótulo='{node.label}'). "
            "Aqui eu incrementaria o contador de folhas"
        )


class TreeBuilderState(ABC):
    """Interface base para os estados do TreeBuilder."""

    def __init__(self, builder: "TreeBuilder") -> None:
        self.builder = builder

    @abstractmethod
    def handle(self, node: DecisionNode) -> None:
        """Executa uma etapa de construção/pruning da árvore."""
        raise NotImplementedError


class SplittingState(TreeBuilderState):
    """Estado responsável por 'dividir' um nó em filhos."""

    def handle(self, node: DecisionNode) -> None:
        print(f"[SplittingState] Preparando divisão do nó '{node.name}'...")
        # adiciona dois filhos mockados
        yes_child = LeafNode(name=f"{node.name}_YES", label="Sim")
        no_child = LeafNode(name=f"{node.name}_NO", label="Não")
        node.add_child(yes_child)
        node.add_child(no_child)
        print(
            f"[SplittingState] Nó '{node.name}' dividido em "
            f"'{yes_child.name}' e '{no_child.name}'."
        )
        # após dividir, muda para o estado de parada
        self.builder.change_to_stopping()


class StoppingState(TreeBuilderState):
    """Estado que representa a decisão de não dividir mais o nó."""

    def handle(self, node: DecisionNode) -> None:
        print(
            f"[StoppingState] Decidindo não dividir mais o nó '{node.name}'. "
            "Nenhuma modificação real é feita."
        )
        # demonstramos o comportamento e passamos para um possível estado de pruning
        self.builder.change_to_pruning()


class PruningState(TreeBuilderState):
    """Estado que representa a 'poda' de parte da árvore."""

    def handle(self, node: DecisionNode) -> None:
        children = node.get_children()
        if children:
            pruned = children[-1]
            node.remove_child(pruned)
            print(
                f"[PruningState] Podando o filho '{pruned.name}' "
                f"do nó '{node.name}'."
            )
        else:
            print(
                f"[PruningState] Nó '{node.name}' não possui filhos para poda."
            )
        # Após a poda, voltamos para o estado de splitting para um novo ciclo
        self.builder.change_to_splitting()


class TreeBuilder:
    """Contexto do padrão State. Orquestra o processo de construção/poda da árvore mudando de estado."""

    def __init__(self) -> None:
        self._splitting_state = SplittingState(self)
        self._stopping_state = StoppingState(self)
        self._pruning_state = PruningState(self)
        self._state: TreeBuilderState = self._splitting_state


    def change_to_splitting(self) -> None:
        print("[TreeBuilder] Mudando estado para SplittingState.")
        self._state = self._splitting_state

    def change_to_stopping(self) -> None:
        print("[TreeBuilder] Mudando estado para StoppingState.")
        self._state = self._stopping_state

    def change_to_pruning(self) -> None:
        print("[TreeBuilder] Mudando estado para PruningState.")
        self._state = self._pruning_state

    def build_step(self, node: DecisionNode) -> None:
        """Executa uma etapa de construção/pruning de acordo com o estado atual."""
        print(f"[TreeBuilder] Estado atual: {self._state.__class__.__name__}")
        self._state.handle(node)
