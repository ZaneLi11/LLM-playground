import pygame
import random
import sys # 用于sys.exit()

# --- 游戏常量定义 ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20  # 蛇身和食物的单元格大小
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SNAKE_SPEED = 10  # 游戏帧率，决定蛇的移动速度

# --- 颜色定义 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # 蛇的颜色
RED = (255, 0, 0)    # 食物的颜色
BLUE = (0, 0, 255)   # 分数和文字的颜色

# --- 方向定义 (dx, dy) ---
UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

# --- Pygame 初始化 ---
pygame.init()
pygame.display.set_caption("贪吃蛇")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # 默认字体，大小36

# --- Snake类 ---
class Snake:
    def __init__(self):
        # 蛇的身体坐标列表，每个元素是一个(x, y)元组
        # 初始长度为3，从屏幕左侧中间开始向右移动
        self.body = [(GRID_WIDTH // 4 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE),
                     ((GRID_WIDTH // 4 - 1) * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE),
                     ((GRID_WIDTH // 4 - 2) * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)]
        self.direction = RIGHT  # 初始移动方向
        self.growing = False    # 标记蛇是否在当前帧增长

    def move(self):
        """
        根据当前方向移动蛇的身体。
        如果处于增长状态，则不移除尾部。
        """
        # 计算新蛇头的位置
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 将新蛇头添加到身体的最前端
        self.body.insert(0, new_head)

        # 如果蛇没有增长，则移除身体的最后一个部分（尾巴）
        if not self.growing:
            self.body.pop()
        else:
            # 增长后重置growing标志，确保只增长一次
            self.growing = False

    def change_direction(self, new_direction):
        """
        改变蛇的移动方向。
        关键逻辑：禁止蛇立即180度反向移动（例如，从左直接转向右）。
        """
        # 检查新方向是否与当前方向相反
        # 如果(new_direction[0] + self.direction[0] == 0) 并且 (new_direction[1] + self.direction[1] == 0)
        # 则表示方向相反（如 (20,0) + (-20,0) = (0,0)）
        if (new_direction[0] + self.direction[0] == 0 and 
            new_direction[1] + self.direction[1] == 0):
            return  # 忽略反向操作
        
        self.direction = new_direction

    def check_collision(self):
        """
        检查蛇是否发生碰撞（撞墙或撞到自身）。
        返回 True 表示发生碰撞，False 表示未碰撞。
        """
        head_x, head_y = self.body[0]

        # 1. 边界碰撞检测：检查蛇头是否超出屏幕范围
        # 常见错误：未考虑窗口坐标系的起始点(0,0)
        if not (0 <= head_x < SCREEN_WIDTH and 0 <= head_y < SCREEN_HEIGHT):
            return True  # 撞墙

        # 2. 自身碰撞检测：检查蛇头是否撞到身体的任何一部分
        # 常见错误：直接检查蛇头是否在身体列表中，这会包含蛇头自身
        # 正确做法是检查蛇头是否在身体的除头部以外的部分
        if self.body[0] in self.body[1:]:
            return True  # 撞到自身

        return False

    def grow(self):
        """设置标志，指示蛇在下一次移动时增长身体。"""
        self.growing = True

    def draw(self, surface):
        """在给定的 surface 上绘制蛇的身体。"""
        for segment in self.body:
            pygame.draw.rect(surface, GREEN, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))

# --- Food类 ---
class Food:
    def __init__(self, snake_body):
        self.position = None
        self.randomize_position(snake_body) # 初始化时随机生成食物位置

    def randomize_position(self, snake_body):
        """
        随机生成新的食物位置，确保不与蛇的身体重叠。
        常见错误：未检查新位置是否有效。
        """
        while True:
            # 在网格范围内随机生成 x, y 坐标
            x = random.randrange(GRID_WIDTH) * GRID_SIZE
            y = random.randrange(GRID_HEIGHT) * GRID_SIZE
            new_pos = (x, y)

            # 检查新位置是否与蛇的身体重叠
            if new_pos not in snake_body:
                self.position = new_pos
                break # 找到有效位置，跳出循环

    def draw(self, surface):
        """在给定的 surface 上绘制食物。"""
        pygame.draw.rect(surface, RED, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))

# --- Game类 ---
class Game:
    def __init__(self):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.game_over = False  # 游戏状态标志
        self.score = 0          # 玩家分数
        self.snake = Snake()    # 蛇的实例
        self.food = Food(self.snake.body) # 食物的实例，初始化时传入蛇的身体以避免重叠

    def _draw_elements(self):
        """绘制所有游戏元素：背景、蛇、食物、分数。"""
        self.screen.fill(BLACK) # 填充黑色背景
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        self._display_score()

    def _display_score(self):
        """在屏幕左上角显示当前分数。"""
        score_text = self.font.render(f"分数: {self.score}", True, BLUE)
        self.screen.blit(score_text, (5, 5)) # 放置在 (5, 5) 坐标

    def _handle_input(self):
        """处理用户输入事件，如退出游戏和方向控制。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() # 退出程序

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    # 如果游戏结束，只处理 'R' 键重新开始
                    if event.key == pygame.K_r:
                        self._restart_game()
                else:
                    # 游戏进行中，处理方向键
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)

    def _check_game_logic(self):
        """检查游戏逻辑，包括碰撞检测和食物消耗。"""
        # 1. 碰撞检测
        if self.snake.check_collision():
            self.game_over = True

        # 2. 食物消耗检测：如果蛇头位置与食物位置相同
        if self.snake.body[0] == self.food.position:
            self.score += 1         # 增加分数
            self.snake.grow()       # 通知蛇增长身体
            self.food.randomize_position(self.snake.body) # 重新生成食物位置

    def _display_game_over_screen(self):
        """显示游戏结束画面和重新开始的提示。"""
        # 创建一个半透明的图层，覆盖在屏幕上，使背景变暗
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128)) # 黑色，透明度128 (0-255)
        self.screen.blit(s, (0, 0))

        # 渲染游戏结束文字
        game_over_text = self.font.render("GAME OVER!", True, WHITE)
        score_final_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        restart_text = self.font.render("按 'R' 键重新开始", True, WHITE)

        # 获取文本矩形并居中显示
        go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        score_rect = score_final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        self.screen.blit(game_over_text, go_rect)
        self.screen.blit(score_final_text, score_rect)
        self.screen.blit(restart_text, restart_rect)

    def _restart_game(self):
        """重置游戏到初始状态。"""
        self.game_over = False
        self.score = 0
        self.snake = Snake() # 创建新的蛇实例
        self.food = Food(self.snake.body) # 创建新的食物实例

    def run(self):
        """游戏主循环。"""
        running = True
        while running:
            self._handle_input() # 处理用户输入

            if not self.game_over:
                # 游戏进行中时，移动蛇并检查游戏逻辑
                self.snake.move()
                self._check_game_logic()
            
            self._draw_elements() # 无论游戏是否结束，都绘制元素

            if self.game_over:
                # 如果游戏结束，显示游戏结束画面
                self._display_game_over_screen()

            pygame.display.flip() # 更新整个屏幕显示
            self.clock.tick(SNAKE_SPEED) # 控制游戏帧率

# --- 游戏入口点 ---
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit() # 确保在程序结束时正确退出 Pygame