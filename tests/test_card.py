# -*- coding: utf-8 -*-
"""
卡牌单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card, CardRarity, CardClass, parse_card_name


class CardTestCase(unittest.TestCase):
    """卡牌测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.test_card = Card(
            name="德莱文",
            cost=4,
            classes=["挑战者", "帝国"],
            confidence=0.95
        )
    
    def test_card_creation(self):
        """测试卡牌创建"""
        card = Card(name="测试卡牌", cost=3)
        self.assertEqual(card.name, "测试卡牌")
        self.assertEqual(card.cost, 3)
        self.assertEqual(card.rarity, CardRarity.THREE_COST)
    
    def test_card_rarity_from_cost(self):
        """测试稀有度从费用获取"""
        self.assertEqual(CardRarity.from_cost(1), CardRarity.ONE_COST)
        self.assertEqual(CardRarity.from_cost(2), CardRarity.TWO_COST)
        self.assertEqual(CardRarity.from_cost(3), CardRarity.THREE_COST)
        self.assertEqual(CardRarity.from_cost(4), CardRarity.FOUR_COST)
        self.assertEqual(CardRarity.from_cost(5), CardRarity.FIVE_COST)
        self.assertEqual(CardRarity.from_cost(99), CardRarity.UNKNOWN)
    
    def test_card_cost_property(self):
        """测试费用属性"""
        self.assertEqual(CardRarity.ONE_COST.cost, 1)
        self.assertEqual(CardRarity.TWO_COST.cost, 2)
        self.assertEqual(CardRarity.FIVE_COST.cost, 5)
    
    def test_card_str_representation(self):
        """测试卡牌字符串表示"""
        card = Card(name="烬", cost=4)
        self.assertIn("烬", str(card))
        self.assertIn("4费", str(card))
    
    def test_card_position(self):
        """测试卡牌位置设置"""
        self.test_card.set_position(100, 200)
        self.assertEqual(self.test_card.position, (100, 200))
    
    def test_card_selection(self):
        """测试卡牌选择状态"""
        self.assertFalse(self.test_card.is_selected)
        self.test_card.select()
        self.assertTrue(self.test_card.is_selected)
        self.test_card.deselect()
        self.assertFalse(self.test_card.is_selected)
    
    def test_card_matches_priority(self):
        """测试优先级匹配"""
        priority_list = ["德莱文", "亚索", "凯尔"]
        self.assertTrue(self.test_card.matches_priority(priority_list))
        
        priority_list2 = ["亚索", "凯尔"]
        self.assertFalse(self.test_card.matches_priority(priority_list2))
    
    def test_card_to_dict(self):
        """测试卡牌转字典"""
        card = Card(name="测试", cost=2)
        card_dict = card.to_dict()
        
        self.assertEqual(card_dict['name'], "测试")
        self.assertEqual(card_dict['cost'], 2)
        self.assertIn('rarity', card_dict)
    
    def test_card_class(self):
        """测试卡牌职业类"""
        cls = CardClass("挑战者")
        self.assertEqual(str(cls), "挑战者")
        
        cls2 = CardClass("  挑战者  ")
        self.assertEqual(cls, cls2)
    
    def test_parse_card_name(self):
        """测试卡牌名称解析"""
        self.assertEqual(parse_card_name("德莱文"), "德莱文")
        self.assertEqual(parse_card_name("  德莱文  "), "德莱文")
    
    def test_card_full_name(self):
        """测试完整名称属性"""
        card = Card(name="烬", cost=4)
        self.assertIn("烬", card.full_name)
        self.assertIn("4费", card.full_name)


if __name__ == '__main__':
    unittest.main()
