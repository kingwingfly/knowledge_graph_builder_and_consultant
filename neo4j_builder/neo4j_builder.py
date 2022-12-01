from py2neo import Node, Graph, Relationship, NodeMatcher
from data_parser import load_data


class NeoGraph:
    def __init__(self, init: bool) -> None:
        self.graph = Graph("http://localhost:7474/", auth=("neo4j", "123"))
        if init:
            self.graph.delete_all()

    # 查询节点
    def match_node(self, label, attrs):
        # n = "_.name=" + "\"" + attrs["name"] + "\""
        # n = f'_.name="{attrs["name"]}"'
        matcher = NodeMatcher(self.graph)
        return matcher.match(label).where(**attrs).first()

    # 建立一个节点
    def create_node(self, label: str, attrs: dict):
        # 查询是否已经存在，若存在则返回节点，否则返回None
        value = self.match_node(label, attrs)
        # 如果要创建的节点不存在则创建
        if value is None:
            node = Node(label, **attrs)
            self.graph.create(node)
            print(f"Node created: label: {label} name: {attrs['name']}")
            return
        print(f"Node has existed: label: {label} name: {attrs['name']}")
        # return

    # 建立两个节点之间的关系
    def create_relation(
        self,
        label1: str,
        attrs1: dict,
        label2: str,
        attrs2: dict,
        r_name: str,
        attrs: dict,
    ):
        value1 = self.match_node(label1, attrs1)
        value2 = self.match_node(label2, attrs2)
        if value1 is None or value2 is None:
            print(
                f'Nodes don\'t all exist: {label1}: {attrs1["name"]})->[{r_name}: {attrs["name"]}]->({label2}: {attrs2["name"]})'
            )
            return
        r = Relationship(value1, r_name, value2, **attrs)
        print(
            f'Relation created: ({label1}: {attrs1["name"]})->[{r_name}: {attrs["name"]}]->({label2}: {attrs2["name"]})'
        )
        self.graph.create(r)


def create_nodes(neo_graph: NeoGraph, label: str, nodes: dict):
    for node, properties in nodes.items():
        neo_graph.create_node(label, {'name': node} | properties)


def create_author_relations(
    neo_graph: NeoGraph, cooperation: dict[str, list[list[str | list[str]]]]
):
    for author, infos in cooperation.items():
        # print(author, '\n', infos)
        for info in infos:
            # info: [title, [cooperators]]
            for cooperator in info[1]:
                neo_graph.create_relation(
                    'Author',
                    {'name': author},
                    'Author',
                    {'name': cooperator},
                    'Cooperation',
                    {'name': 'CooperateBetweenAuthors', 'Cooperatedon': info[0]},
                )


def create_when_str(
    neo_graph: NeoGraph,
    article: str,
    target: str,
    relation_label1: str,
    relation_label2: str,
    target_label: str,
):
    neo_graph.create_relation(
        'Article',
        {'name': article},
        target_label,
        {'name': target},
        relation_label1,
        {'name': relation_label1},
    )
    neo_graph.create_relation(
        target_label,
        {'name': target},
        'Article',
        {'name': article},
        relation_label2,
        {'name': relation_label2},
    )


def create_when_list(
    neo_graph: NeoGraph,
    article: str,
    targets: str,
    relation_label1: str,
    relation_label2: str,
    target_label
):
    for target in targets:
        create_when_str(neo_graph, article, target, relation_label1, relation_label2, target_label)


def create_article_relations(
    neo_graph: NeoGraph, articles: dict[str, dict[str, str | list[str]]]
):
    relation_label_dic = {
        'Author-作者': ('WittenBy', 'Wrote', 'Author'),
        'Organ-单位': ('Belongto', 'Contains', 'Organ'),
        'Source-文献来源': ('PublishedOn', 'Published', 'Source'),
        'Keyword-关键词': ('Quoted', 'QuotedBy', 'Keyword'),
        'Keyword_of_abstract': ('QuoteinAbstract', 'QuotedinAbstractBy', 'KeywordinAbstract'),
    }
    # article: str; infos: {str: str|lst}
    for article, infos in articles.items():
        for relation, target in infos.items():
            if not target or relation in [
                'SrcDatabase-来源库',
                'Title-题名',
                'Summary-摘要',
                'PubTime-发表时间',
                'DOI-DOI',
                'Year-年',
            ]:
                continue
            # relation in [Author-作者, Organ-单位, Source-文献来源, Keyword-关键词, Keyword_of_abstract,]
            if type(target) == str:
                create_when_str(
                    neo_graph, article, target, *relation_label_dic[relation]
                )
            elif type(target) == list:
                create_when_list(
                    neo_graph, article, target, *relation_label_dic[relation]
                )


def main():
    neo_graph = NeoGraph(init=True)
    '''Create nodes'''
    create_nodes(neo_graph, 'Article', load_data('./data/cnki.json'))
    create_nodes(neo_graph, 'Author', load_data('./data/Author-作者.json'))
    create_nodes(neo_graph, 'Keyword', load_data('./data/Keyword-关键词.json'))
    create_nodes(neo_graph, 'Sourse', load_data('./data/Source-文献来源.json'))
    create_nodes(neo_graph, 'Organ', load_data('./data/Organ-单位.json'))
    create_nodes(neo_graph, 'KeywordinAbstract', load_data('./data/Keyword_of_abstract.json'))
    create_nodes(neo_graph, 'BaikeWord', load_data('./data/baike.json'))
    '''Create relations'''
    create_author_relations(neo_graph, load_data('./data/cooperation.json'))
    create_article_relations(neo_graph, load_data('./data/cnki.json'))


if __name__ == '__main__':
    main()
