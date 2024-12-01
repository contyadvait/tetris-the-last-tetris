import unittest
from unittest.mock import patch, MagicMock
from tetris import play_replay, Tetris

# FILE: test_tetris.py


class TestPlayReplay(unittest.TestCase):

    @patch('tetris.pygame')
    def test_play_replay(self, mock_pygame):
        # Mock necessary pygame functions and objects
        mock_pygame.time.Clock.return_value = MagicMock()
        mock_pygame.display.set_mode.return_value = MagicMock()
        mock_pygame.display.set_caption.return_value = MagicMock()
        mock_pygame.image.load.return_value = MagicMock()
        mock_pygame.font.Font.return_value = MagicMock()
        mock_pygame.event.get.return_value = [MagicMock(type=mock_pygame.QUIT)]

        # Sample replay data
        replay_data = {
            'piece_sequence': [{'shape': [[1, 1, 1, 1]], 'key': 'I'}],
            'moves': [{'type': 'move', 'time': 0, 'data': {'dx': 0, 'dy': 1}}],
            'final_score': 100
        }

        # Call the play_replay function with the sample replay data
        play_replay(replay_data)

        # Assertions to verify expected behavior
        self.assertTrue(mock_pygame.display.set_mode.called)
        self.assertTrue(mock_pygame.display.set_caption.called)
        self.assertTrue(mock_pygame.image.load.called)
        self.assertTrue(mock_pygame.font.Font.called)
        self.assertTrue(mock_pygame.event.get.called)

if __name__ == '__main__':
    unittest.main()