# -*- coding: utf-8 -*-
"""
游戏状态单元测试
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_state import GameState, GamePhase


class GameStateTestCase(unittest.TestCase):
    """游戏状态测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.game_state = GameState()
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.game_state.phase, GamePhase.UNKNOWN)
        self.assertEqual(len(self.game_state.available_cards), 0)
        self.assertEqual(self.game_state.gold, 0)
        self.assertEqual(self.game_state.level, 1)
        self.assertFalse(self.game_state.is_active)
    
    def test_update_phase(self):
        """测试阶段更新"""
        self.game_state.update_phase(GamePhase.SHOPPING)
        self.assertEqual(self.game_state.phase, GamePhase.SHOPPING)
        
        self.game_state.update_phase(GamePhase.LOBBY)
        self.assertEqual(self.game_state.phase, GamePhase.LOBBY)
    
    def test_set_shop_phase(self):
        """测试设置商店阶段"""
        self.game_state.set_shop_phase()
        self.assertEqual(self.game_state.phase, GamePhase.SHOPPING)
        self.assertTrue(self.game_state.is_active)
    
    def test_set_lobby_phase(self):
        """测试设置大厅阶段"""
        self.game_state.set_shop_phase()
        self.game_state.set_lobby_phase()
        self.assertEqual(self.game_state.phase, GamePhase.LOBBY)
        self.assertFalse(self.game_state.is_active)
    
    def test_set_battle_phase(self):
        """测试设置战斗阶段"""
        self.game_state.set_shop_phase()
        self.game_state.set_battle_phase()
        self.assertEqual(self.game_state.phase, GamePhase.BATTLING)
        self.assertFalse(self.game_state.is_active)
    
    def test_reset(self):
        """测试重置状态"""
        self.game_state.set_shop_phase()
        self.game_state.gold = 50
        self.game_state.level = 5
        
        self.game_state.reset()
        
        self.assertEqual(self.game_state.phase, GamePhase.UNKNOWN)
        self.assertEqual(self.game_state.gold, 0)
        self.assertEqual(self.game_state.level, 1)
    
    def test_to_dict(self):
        """测试转换为字典"""
        self.game_state.set_shop_phase()
        self.game_state.gold = 40
        
        state_dict = self.game_state.to_dict()
        
        self.assertIn('phase', state_dict)
        self.assertIn('gold', state_dict)
        self.assertIn('is_active', state_dict)
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.game_state.set_shop_phase()
        str_repr = str(self.game_state)
        
        self.assertIn('SHOPPING', str_repr)


if __name__ == '__main__':
    unittest.main()
