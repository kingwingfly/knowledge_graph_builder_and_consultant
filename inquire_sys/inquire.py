import py2neo
from py2neo import Graph, NodeMatcher, RelationshipMatcher
from queue import Queue
from jieba import analyse
import ahocorasick
import os
import json


class Consultant:
    def __init__(self, json_path='./data') -> None:
        with open('./dictionary/label_dict.json', 'r', encoding='utf-8') as f:
            self.label_dict = json.load(f)
        with open('./dictionary/extra_names.json', 'r', encoding='utf-8') as f:
            self.extra_attr_names = json.load(f)
        with open('./dictionary/relation_translate.json', 'r', encoding='utf-8') as f:
            self.relation_translate = json.load(f)
        with open('./dictionary/attribute_translate.json', 'r', encoding='utf-8') as f:
            self.attribute_translate = json.load(f)
        self.ac_trees = self.tree_builder(json_path)
        # ac_trees: {label: ac_tree}
        self.graph = Graph("http://localhost:7474/", auth=("neo4j", "123"))
        self.qwds_ac_trees = self.qwds_ac_tree_builder()
        self.matcher = NodeMatcher(self.graph)
        self.r_matcher = RelationshipMatcher(self.graph)

    def tree_builder(self, json_path):
        ac_trees = {}
        for dirpath, _, filenames in os.walk(json_path):
            for filename in filenames:
                if not filename.endswith('.json'):
                    continue
                ac_tree = ahocorasick.Automaton()
                f = open(os.path.join(dirpath, filename), 'r', encoding='utf-8')
                label, words = (
                    self.label_dict[''.join(filename.split('.')[:-1:])],
                    json.load(f).keys(),
                )
                f.close()
                for word in words:
                    # word as index, word as return when inquiring
                    ac_tree.add_word(word, word)
                ac_tree.make_automaton()
                ac_trees[label] = ac_tree
        return ac_trees

    def qwds_ac_tree_builder(self):
        ac_trees = {}
        for json_name in [
            'Author-作者',
            'cnki',
            'Keyword_of_abstract',
            'Keyword-关键词',
            'Organ-单位',
            'Source-文献来源',
            'baike',
        ]:
            ac_tree = ahocorasick.Automaton()
            with open(f'./data/{json_name}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            attr_names = set(
                [attr_name for attr in data.values() for attr_name in attr.keys()]
            )
            label = self.label_dict[json_name]
            for qwd in attr_names | set(self.extra_attr_names[label]):
                # qwd as index, (label, qwd) as return when inquiring
                ac_tree.add_word(qwd, (label, qwd))
            ac_tree.make_automaton()
            ac_trees[label] = ac_tree
        return ac_trees

    def node_label_getter(self, sentence):
        nodes_mentioned = []
        for label, ac_tree in self.ac_trees.items():
            for _, word in ac_tree.iter(sentence):
                nodes_mentioned.append((label, word))
        return nodes_mentioned

    def question_classfy(self, sentence, labels):
        inquired_relation = []
        for label in labels:
            for _, (label, attr) in self.qwds_ac_trees[label].iter(sentence):
                inquired_relation.append((label, attr))
        return inquired_relation

    @staticmethod
    def deduplication(nodes, keep_diffrent_label=False):
        new_nodes = []
        for i in range(len(nodes)):
            others = nodes[::]
            others.pop(i)
            flag = True
            if keep_diffrent_label:
                for label, word in others:
                    if (
                        nodes[i][1] in word
                        and nodes[i][1] != word
                        and nodes[i][0] == label
                    ):
                        flag = False
                        continue
            else:
                for label, word in others:
                    if nodes[i][1] in word and nodes[i][1] != word:
                        flag = False
                        continue
            if flag:
                new_nodes.append(i)
        return [nodes[i] for i in new_nodes]

    def inquire(self, sentence, queue):
        # [(position, label, name)]
        nodes_mentioned = self.node_label_getter(sentence)
        nodes_mentioned = self.deduplication(nodes_mentioned, keep_diffrent_label=False)
        labels = set([label for label, _ in nodes_mentioned])
        nodes_mentioned = dict(nodes_mentioned)
        # [types]
        question_types = self.question_classfy(sentence, labels)
        question_types = dict(
            self.deduplication(question_types, keep_diffrent_label=True)
        )
        print(nodes_mentioned)
        print(question_types)
        result = []
        for label in labels:
            n = nodes_mentioned.get(label, None)
            r = question_types.get(label, None)
            if not n or not r:
                continue
            relationship = self.relation_translate.get(r, r)
            attribute = self.attribute_translate.get(r, r)
            nodes = self.matcher.match(label).where(name=n).all()
            if attribute == "全部信息":
                for node in nodes:
                    for attr_name, attr in node.items():
                        if attr_name == 'name' or not attr:
                            continue
                        result.append(f'{n} 的 {attr_name} 为 {attr}')
                for node in nodes:
                    relations = self.r_matcher.match(
                        nodes=(node, None), r_type=None
                    ).all()
                    for relation in relations:
                        gen = py2neo.data.walk(relation)
                        start = next(gen)
                        relation = next(gen)
                        end = next(gen)
                        if len(relation) > 1:
                            result.append(
                                f'{start["name"]} and {end["name"]} '
                                + ' & '.join(
                                    [
                                        k + ': ' + v
                                        for k, v in relation.items()
                                        if k != 'name'
                                    ]
                                )
                            )
                        else:
                            result.append(f'{start["name"]}  {relation["name"]} {end["name"]}')
                continue
            for node in nodes:
                if node[attribute]:
                    result.append(f'{n} 的 {r} 为 {node[attribute]}')
            for node in nodes:
                relations = self.r_matcher.match(
                    nodes=(node, None), r_type=relationship
                ).all()
                for relation in relations:
                    gen = py2neo.data.walk(relation)
                    start = next(gen)
                    relation = next(gen)
                    end = next(gen)
                    if len(relation) > 1:
                        result.append(
                            f'{start["name"]} and {end["name"]} '
                            + ' & '.join(
                                [
                                    k + ': ' + v
                                    for k, v in relation.items()
                                    if k != 'name'
                                ]
                            )
                        )
                    else:
                        result.append(f'{start["name"]} 的 {r} 为 {end["name"]}')
        # print(result)
        queue.put(result)


if __name__ == '__main__':
    queue = Queue()
    consultant = Consultant()
    sentence = '基于数据大脑的船岸一体机舱智能运维系统研究设计发表时间'
    consultant.inquire(sentence, queue)
    print(queue.get())
