#!/usr/bin/env python3
# coding: utf-8
# File: sentence_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-3-10

import os
from ltp import LTP
import torch
from pyltp import SementicRoleLabeller

workspace = os.path.dirname(__file__)
print(workspace)

class LtpParser:
    def __init__(self, if_cuda=True):
        if if_cuda == True:
            device = torch.device('cuda:0') if torch.cuda.is_available() else 'cpu'
        else:
            device = 'cpu'
        LTP_DIR = "./EventTriplesExtraction/ltp_models"
        # todo 该模型依然运行在CPU上，新的ltp输出srl内容有变，不好修改
        self.labeller = SementicRoleLabeller(os.path.join(LTP_DIR, "pisrl_win.model"))
        self.ltp = LTP(os.path.join(workspace, '..', 'data', 'small')).to(device)

    def __release__(self):
        self.labeller.release()
        self.ltp.release()

    '''语义角色标注'''
    def format_labelrole(self, words, postags, arcs):
        roles = self.labeller.label(words, postags, arcs)
        roles_dict = {}
        for role in roles:
            roles_dict[role[0]] = {arg[0]:[arg[0],arg[1][0], arg[1][1]] for arg in role[1]}
        return roles_dict

    '''句法分析---为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
    def build_parse_child_dict(self, words, postags, arcs):
        child_dict_list = []
        format_parse_list = []
        for index in range(len(words)):
            child_dict = dict()
            for arc_index in range(len(arcs)):
                if arcs[arc_index][0] == index+1:   #arcs的索引从1开始
                    if arcs[arc_index][1] in child_dict:
                        child_dict[arcs[arc_index][1]].append(arc_index)
                    else:
                        child_dict[arcs[arc_index][1]] = []
                        child_dict[arcs[arc_index][1]].append(arc_index)
            child_dict_list.append(child_dict)
        rely_id = [arc[0] for arc in arcs]  # 提取依存父节点id
        relation = [arc[1] for arc in arcs]  # 提取依存关系
        heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语
        for i in range(len(words)):
            # ['ATT', '李克强', 0, 'nh', '总理', 1, 'n']
            a = [relation[i], words[i], i, postags[i], heads[i], rely_id[i]-1, postags[rely_id[i]-1]]
            format_parse_list.append(a)

        return child_dict_list, format_parse_list

    '''parser主函数'''
    def parser_main(self, sentence):
        words, postags, dependency = self.ltp.pipeline(sentence, tasks=['cws', 'pos', 'dep']).values()
        arcs = list(zip(dependency['head'], dependency['label']))
        child_dict_list, format_parse_list = self.build_parse_child_dict(words, postags, arcs)
        roles_dict = self.format_labelrole(words, postags, arcs)
        return words, postags, child_dict_list, roles_dict, format_parse_list


if __name__ == '__main__':
    parse = LtpParser()
    sentence = '李克强总理今天来我家了,我感到非常荣幸'
    words, postags, child_dict_list, roles_dict, format_parse_list = parse.parser_main(sentence)
    # print(words, len(words))
    # print(postags, len(postags))
    # print(child_dict_list, len(child_dict_list))
    # print(roles_dict)
    # print(format_parse_list, len(format_parse_list))