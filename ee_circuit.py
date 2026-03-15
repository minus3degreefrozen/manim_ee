from manim import *
import numpy as np


class Circuit(VGroup):
    """
    面向电路绘图的容器类，负责“游标驱动”的元件布置与连线。

    设计要点：
        - Circuit 自身是一个 ``VGroup``，内部可以包含多个电阻、连线、节点等；
        - 维护一个“游标位置”和“当前朝向”，用于增量式地放置元件；
        - 支持按角度布置元件、按坐标或方向指定锚点、控制游标是否前进；
        - 通过 ``elements_dict`` 提供按名称访问元件的能力（如 ``circuit.R12``）。
    """
    def __init__(self, start_pos=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        # 当前“游标坐标”：下一次放置元件或绘制导线的起点
        self.cursor_coord = np.array(start_pos, dtype=float)
        # 当前“游标方向角”：以度为单位，0° 向右，90° 向上等
        self.current_angle = 0.0
        # 命名元件字典：支持通过属性或下标访问特定元件
        self.elements_dict = {}
        # 控制是否在下一次放置元件后保持游标不动（适用于从中心辐射放置多元件的场景）
        self._hold_cursor_once = False
    
    def __getattr__(self, name):
        """
        支持使用点号语法访问命名元件，例如 ``circuit.R12``。
        """
        elements = super().__getattribute__("elements_dict")
        if name in elements:
            return elements[name]
        raise AttributeError(f"'{type(self).__name__}' 对象没有属性或元件 '{name}'")
    
    def __getitem__(self, key):
        """
        通过下标访问命名元件，例如 ``circuit['R12']``。
        """
        return self.elements_dict.get(key)

    def move_cursor_to(self, coord: np.ndarray):
        """
        将“游标位置”移动到指定坐标。

        常用于：
            - 从某个节点重新开始绘制导线；
            - 在不同子电路之间跳转起点。
        """
        self.cursor_coord = np.array(coord, dtype=float)
        return self
    
    def hold(self):
        """
        让“下一次” add_elements 调用在放置元件后不更新游标位置。
        适用于从同一锚点向四周辐射绘制多个元件的场景。
        
        典型用法：
            center = ...
            circuit.move_cursor_to(center)
            circuit.hold().add_elements(R1, angle_degree=0)
            circuit.hold().add_elements(R2, angle_degree=120)
            circuit.hold().add_elements(R3, angle_degree=240)
        以上三次放置后，游标仍保持在 center，不会被移动到各个元件的右端。
        """
        self._hold_cursor_once = True
        return self

    def theta(self, angle_degree):
        """
        设置当前游标的绘图角度（单位：度）。

        约定：
            - 0° 表示向右；
            - 90° 表示向上；
            - 180° 表示向左；
            - 270° 表示向下。
        """
        self.current_angle = angle_degree * DEGREES
        return self

    # 0.1 常用方向快捷函数
    def right(self):
        """
        将当前绘图方向设置为 0°（向右）。
        等价于 self.theta(0)。
        """
        return self.theta(0)

    def up(self):
        """
        将当前绘图方向设置为 90°（向上）。
        等价于 self.theta(90)。
        """
        return self.theta(90)

    def left(self):
        """
        将当前绘图方向设置为 180°（向左）。
        等价于 self.theta(180)。
        """
        return self.theta(180)

    def down(self):
        """
        将当前绘图方向设置为 270°（向下）。
        等价于 self.theta(270)。
        """
        return self.theta(270)

    # 1.增量添加元件（集成锚点与角度设置）
    def add_elements(
        self,
        mobject: VGroup,
        name: str | None = None,
        anchor: np.ndarray | None = None,
        angle_degree: float | None = None,
    ):
        """
        在电路中添加一个元件，并可选地同时指定：
            - 元件放置的锚点坐标（anchor）
            - 元件放置的方向角度（angle_degree，单位：度）

        参数说明：
            mobject: 要添加的元件（如 Resistor 实例）
            name: 可选的元件名称，会记录到 elements_dict 中
            anchor: 
                - 若为坐标 (np.ndarray)，则元件左端会对齐到该坐标；
                - 若为方向常量 RIGHT / UP / LEFT / DOWN，则会被解释为
                  0° / 90° / 180° / 270° 的放置方向（此时不移动游标）。
            angle_degree: 可选角度；若提供，则在放置前将当前绘图角度设置为该值

        行为等价于按顺序执行：
            1. 如果 anchor 是 RIGHT / UP / LEFT / DOWN 之一，则根据其设置
               对应的角度（0/90/180/270 度），并清空锚点坐标；
            2. 如果给定 angle_degree，则调用 self.theta(angle_degree)
            3. 如果给定 anchor（且为坐标），则调用 self.move_cursor_to(anchor)
            4. 使用当前游标坐标和当前角度执行原有的添加逻辑

        示例：
            # 1）保持现有状态，只按当前游标与角度放置：
            circuit.add_elements(R1, name="R1")

            # 2）指定角度，但使用当前游标位置：
            circuit.add_elements(R2, name="R2", angle_degree=120)

            # 3）指定锚点和角度，一次性完成：
            circuit.add_elements(R3, name="R3",
                                 anchor=R1.left_terminal,
                                 angle_degree=240)

            # 4）使用方向常量代替特殊角度（0°/90°/180°/270°）：
            circuit.add_elements(R4, name="R4", anchor=RIGHT)  # 等价于 angle_degree=0
            circuit.add_elements(R5, name="R5", anchor=UP)     # 等价于 angle_degree=90
        """
        # 0. 如果 anchor 是方向常量，则将其转换为角度信息
        if anchor is not None:
            if np.allclose(anchor, RIGHT):
                if angle_degree is None:
                    angle_degree = 0
                anchor = None  # 不移动游标，只用作方向
            elif np.allclose(anchor, UP):
                if angle_degree is None:
                    angle_degree = 90
                anchor = None
            elif np.allclose(anchor, LEFT):
                if angle_degree is None:
                    angle_degree = 180
                anchor = None
            elif np.allclose(anchor, DOWN):
                if angle_degree is None:
                    angle_degree = 270
                anchor = None

        # 1. 可选：设置角度
        if angle_degree is not None:
            self.theta(angle_degree)

        # 2. 可选：设置锚点（游标位置）
        if anchor is not None:
            self.move_cursor_to(anchor)

        # 3. 按当前角度与游标执行原有放置逻辑
        if self.current_angle != 0.0:
            mobject.rotate_about_origin(self.current_angle)

        # 将元件的左终端移动到当前游标位置
        shift_vector = self.cursor_coord - mobject.left_terminal
        mobject.shift(shift_vector)

        if hasattr(mobject, "update_label_for_angle"):
            mobject.update_label_for_angle(self.current_angle)

        # 更新游标到元件右端（若未开启 hold）
        if self._hold_cursor_once:
            # 本次放置后保持游标不动，并重置开关
            self._hold_cursor_once = False
        else:
            self.cursor_coord = np.array(mobject.right_terminal)

        # 添加到 Circuit 容器并可选记录名称
        self.add(mobject)
        if name:
            self.elements_dict[name] = mobject

        return self

    # 🚀 新增节点功能
    def add_node(self, coord: np.ndarray,
                 label_text: str | None = None,
                 node_radius: float = 0.08,
                 node_color: ManimColor = WHITE,
                 label_position: np.ndarray = UP,
                 label_color: ManimColor = WHITE,
                 label_scale: float = 0.5,
                 label_buff: float = 0.2,
                 name: str | None = None) -> Dot:
        """
        在指定坐标添加一个节点（Dot）和可选的标签。
        
        Args:
            coord: 节点中心坐标。
            label_text: 节点标签文本（可选）。
            node_radius: 节点半径。
            ... (其他样式参数)
        
        Returns:
            Dot: 创建的节点 Mobject。
        """
        
        node = Dot(coord, radius=node_radius, color=node_color).set_z_index(1) # 确保节点在前景
        self.add(node)
        
        if label_text:
            # 标签创建
            # 标签创建
            if label_text.startswith('$') and label_text.endswith('$'):
                label = MathTex(label_text[1:-1], color=label_color)
            else:
                label = Tex(label_text, color=label_color)
                
            label.scale(label_scale)
            # 定位
            label.next_to(node, label_position, buff=label_buff)
            
            # 将标签添加到 Circuit，使其成为 Circuit 的一部分
            self.add(label)
            # 为了方便外部引用，可以将标签也作为 node 的一个属性
            node.label = label
            
        if name:
            self.elements_dict[name] = node
        return node

    # 2.绘制到指定坐标
    def draw_line_to(self, target_coord: np.ndarray, **kwargs):
        """
        从当前游标位置画线到 target_coord，并更新游标。
        """
        line = Line(self.cursor_coord, target_coord, **kwargs)
        self.add(line)
        
        # 更新游标位置
        self.cursor_coord = target_coord
        
        # 返回 self实现链式调用
        return self
    
    # --- 3. 【新增】绘制相对矢量直线 (支持正交分解) ---
    def draw_line(self, vector: np.ndarray, **kwargs):
        """
        从当前游标出发，根据输入向量绘制直线。
        如果向量同时包含水平和垂直分量（如 UP + RIGHT），
        则会自动分解为“先水平、后垂直”的两段线（L形走线）。
        
        Args:
            vector: Manim 向量 (例如 3*RIGHT, 2*UP + LEFT)
        """
        # 1. 提取分量
        dx = vector[0] # X轴分量
        dy = vector[1] # Y轴分量
        
        # 设置默认样式
        default_kwargs = {'color': WHITE, 'stroke_width': 3}
        line_config = {**default_kwargs, **kwargs}

        # 2. 处理水平分量 (Horizontal)
        # 使用 abs > 1e-6 防止浮点数误差
        if abs(dx) > 1e-6:
            target_x = self.cursor_coord + RIGHT * dx
            line_h = Line(self.cursor_coord, target_x, **line_config)
            self.add(line_h)
            self.cursor_coord = target_x # 更新游标到中间点

        # 3. 处理垂直分量 (Vertical)
        if abs(dy) > 1e-6:
            target_y = self.cursor_coord + UP * dy
            line_v = Line(self.cursor_coord, target_y, **line_config)
            self.add(line_v)
            self.cursor_coord = target_y # 更新游标到终点

        # 4. 返回 self 实现链式调用
        return self

    def connect_components(self,
                           mobject1: VGroup,
                           mobject2: VGroup,
                           mobject1_terminal: str='R',
                           mobject2_terminal: str='L',
                           **kwargs) -> VGroup:
        # 1.定义端口代号到属性名称的映射
        # 这是为了确保代码知道 'R' 对应的是 'right_terminal' 这个属性名
        terminal_map = {'L': 'left_terminal', 'R': 'right_terminal'}

        # 2.检查输入并确定属性名称 (使用 upper()确保大小写不敏感)
        m1_key = mobject1_terminal.upper()
        m2_key = mobject2_terminal.upper()

        if m1_key not in terminal_map or m2_key not in terminal_map:
            raise ValueError(f"Terminal代号必须是 'L' 或 'R'。收到的值: {mobject1_terminal}, {mobject2_terminal}")
        
        m1_attr_name = terminal_map[m1_key]
        m2_attr_name = terminal_map[m2_key]

        # 3.核心逻辑：使用 getattr()动态获取坐标值
        # getattr(对象, 属性名字符串)等价于对象.属性名
        start_coord = getattr(mobject1, m1_attr_name)
        end_coord = getattr(mobject2, m2_attr_name)

        # 4.创建连接线(默认使用白色，stroke_width=3)
        default_kwargs = {'color': WHITE, 'stroke_width': 3}
        connection_line = Line(start_coord, end_coord, **{**default_kwargs, **kwargs})
        self.add(mobject1, mobject2, connection_line)
        
        return self
