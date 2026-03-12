from manim import *
import numpy as np

class Resistor(VGroup):
    """
    电阻元件的基础可视化类。

    特点：
        - 使用折线锯齿近似表示电阻符号；
        - 内建左右端点坐标，便于电路连接；
        - 支持在电阻附近自动放置文本 / LaTeX 标签；
        - 提供统一的创建动画，方便在电路场景中复用。
    """

    def __init__(
        self,
        length: float = 2.0,
        zigzag_count: int = 4,
        show_terminals: bool = True,
        terminal_radius: float = 0.08,
        terminal_color: ManimColor = WHITE,
        terminal_opacity: float = 1.0,
        terminal_extension: float = 0.5,
        label_text: str | None = None,
        label_position: np.ndarray = UP,
        label_color: ManimColor = WHITE,
        label_scale: float = 0.5,
        label_buff: float = 0.3,
        **kwargs,
    ):
        """
        创建一个电阻符号。

        参数说明：
            length:
                电阻整体长度（包括两端接线段），单位为 Manim 坐标单位。
            zigzag_count:
                锯齿“折叠次数”，控制电阻主体的锯齿密度。
            show_terminals:
                是否在左右两端绘制端点圆点。
            terminal_radius / terminal_color / terminal_opacity:
                端点圆点的半径、颜色和不透明度。
            terminal_extension:
                从电阻主体到端点圆点之间的额外接线长度。
            label_text:
                电阻标签文本；支持普通字符串和形如 ``"$R_1$"`` 的 LaTeX 文本。
            label_position:
                标签相对于电阻主体的方向（如 ``UP``、``DOWN`` 等）。
            label_color / label_scale / label_buff:
                标签颜色、缩放比例以及与主体之间的间距。
            **kwargs:
                传递给内部 ``VMobject`` 的其他绘制配置（如颜色、线宽等）。
        """
        super().__init__(**kwargs)
        self.length = length
        self.zigzag_count = zigzag_count
        self.terminal_extension = terminal_extension
        self.label_position = label_position
        self.label_buff = label_buff

        # 1. 计算左右端点在局部坐标系中的位置（用于路径与端点绘制）
        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        # 2. 计算电阻主体锯齿段的起止点
        start_point = LEFT * (length / 2 - self.terminal_extension)
        end_point = RIGHT * (length / 2 - self.terminal_extension)
        step = (length - self.terminal_extension * 2) / (zigzag_count * 2 + 2)
        points = [initial_left_coord, start_point]
        # 3. 累积生成锯齿折线上的顶点
        current_x = start_point[0] + step
        for i in range(zigzag_count * 2 + 1):
            y_offset = 0.3 if i % 2 == 0 else -0.3
            points.append(np.array([current_x, y_offset, 0]))
            current_x += step
        points.append(end_point)
        points.append(initial_right_coord)

        # 4. 使用计算出的顶点创建电阻主体路径
        self.resistor_path = VMobject(**kwargs).set_points_as_corners(points)

        self.body = VGroup(self.resistor_path)

        # 5. 根据配置添加端点圆点
        dots = self._add_terminals(
            show_terminals,
            terminal_radius,
            terminal_color,
            terminal_opacity,
            initial_left_coord,
            initial_right_coord,
        )
        self.body.add(*dots)
        self.add(self.body)

        if label_text:
            self._add_label(label_text, label_position, label_color, label_scale, label_buff)

    def _add_terminals(self, show_terminals, terminal_radius, terminal_color, terminal_opacity, initial_left_coord, initial_right_coord):
        terminal_opacity = terminal_opacity if show_terminals else 0.0
        dot_left = Dot(initial_left_coord, radius=terminal_radius, color=terminal_color, fill_opacity=terminal_opacity)
        dot_right = Dot(initial_right_coord, radius=terminal_radius, color=terminal_color, fill_opacity=terminal_opacity)
        return [dot_left, dot_right]
    
    @property
    def left_terminal(self):
        """
        返回电阻左端（连接点）的坐标。
        """
        return self.resistor_path.get_start()

    @property
    def right_terminal(self):
        """
        返回电阻右端（连接点）的坐标。
        """
        return self.resistor_path.get_end()
    
    def _add_label(self, text, position, color, scale, buff):
        """
        内部工具：在电阻附近创建并附加标签。

        注意：
            - 标签被包裹在 ``self.label`` 这个 ``VGroup`` 中；
            - 标签会随电阻整体变换（平移 / 旋转 / 缩放）。
        """
        # 1. 根据文本内容选择 MathTex / Tex
        if isinstance(text, str) and text.startswith('$') and text.endswith('$'):
            label = MathTex(text[1:-1], color=color)
        else:
            label = Tex(text, color=color)
        
        # 2. 基本样式与相对位置
        label.scale(scale)
        label.next_to(self, position, buff=buff)

        # 3. 包裹成 VGroup，保证后续整体几何变换时一起参与
        self.label = VGroup()
        self.label.add(label)
        self.add(self.label)

    def get_creation_animation(self, run_time=2, **kwargs):
        """
        返回一个用于“从无到有”绘制电阻的创建动画。

        特点：
            - 电阻主体与端点会同时被 Create；
            - 适合作为电路搭建过程中的基础动画单元。
        """
        if not self.submobjects:
            # 极端情况下（没有任何子对象）返回空动画，避免崩溃。
            return AnimationGroup()

        # 默认情况下，电阻主体与端点并行绘制。
        return AnimationGroup(
            *[Create(m, **kwargs) for m in self.submobjects],
            lag_ratio=0,
            run_time=run_time,
            **kwargs,
        )


class Inductor(VGroup):
    """
    电感元件的基础可视化类。

    特点：
        - 使用一串圆弧近似表示电感线圈符号；
        - 与 ``Resistor`` 保持相同的接口风格（端点、标签、创建动画等）；
        - 内建左右端点坐标，便于与 ``Circuit`` 配合进行游标放置。
    """

    def __init__(
        self,
        length: float = 2.0,
        turns: int = 3,
        show_terminals: bool = True,
        terminal_radius: float = 0.08,
        terminal_color: ManimColor = WHITE,
        terminal_opacity: float = 1.0,
        terminal_extension: float = 0.5,
        label_text: str | None = None,
        label_position: np.ndarray = UP,
        label_color: ManimColor = WHITE,
        label_scale: float = 0.5,
        label_buff: float = 0.3,
        **kwargs,
    ):
        """
        创建一个电感符号。

        参数说明：
            length:
                电感整体长度（包括两端接线段），单位为 Manim 坐标单位。
            turns:
                线圈“圈数”，决定弧形线圈的数量。
            show_terminals:
                是否在左右两端绘制端点圆点。
            terminal_radius / terminal_color / terminal_opacity:
                端点圆点的半径、颜色和不透明度。
            terminal_extension:
                从线圈主体到端点圆点之间的额外接线长度。
            label_text:
                电感标签文本；支持普通字符串和形如 ``"$L_1$"`` 的 LaTeX 文本。
            label_position:
                标签相对于电感主体的方向（如 ``UP``、``DOWN`` 等）。
            label_color / label_scale / label_buff:
                标签颜色、缩放比例以及与主体之间的间距。
            **kwargs:
                传递给内部弧线 / 线段的其他绘制配置（如颜色、线宽等）。
        """
        super().__init__(**kwargs)
        self.length = length
        self.turns = max(1, int(turns))
        self.terminal_extension = terminal_extension
        self.label_position = label_position
        self.label_buff = label_buff

        # 1. 计算左右端点位置（用于接线与端点绘制）
        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        # 2. 计算线圈主体所在的区间与每一圈的水平跨度
        coil_length = length - 2 * self.terminal_extension
        coil_length = max(coil_length, 0.1)  # 防止极端参数导致为负
        turn_span = coil_length / self.turns

        components: list[Mobject] = []

        # 3. 左右直线接线段（与 Resistor 保持一致的端点几何）
        left_start = initial_left_coord
        left_end = left_start + RIGHT * self.terminal_extension
        right_end = initial_right_coord
        right_start = right_end + LEFT * self.terminal_extension

        left_lead = Line(left_start, left_end, **kwargs)
        right_lead = Line(right_start, right_end, **kwargs)
        components.extend([left_lead, right_lead])

        # 4. 在线圈区间内依次放置若干个“向上凸起”的半圆弧
        #    使用 ArcBetweenPoints 保证弧线沿水平方向连续排列，形似标准电感符号。
        coil_start = left_end
        for i in range(self.turns):
            p_start = coil_start + RIGHT * (i * turn_span)
            p_end = coil_start + RIGHT * ((i + 1) * turn_span)
            # angle=-PI 生成位于上方的半圆（凸起朝上）
            arc = ArcBetweenPoints(p_start, p_end, angle=-PI, **kwargs)
            components.append(arc)

        self.body = VGroup(*components)
        self.add(self.body)

        # 5. 根据配置添加端点圆点
        if show_terminals:
            terminal_opacity = terminal_opacity
        else:
            terminal_opacity = 0.0
        dot_left = Dot(
            initial_left_coord,
            radius=terminal_radius,
            color=terminal_color,
            fill_opacity=terminal_opacity,
        )
        dot_right = Dot(
            initial_right_coord,
            radius=terminal_radius,
            color=terminal_color,
            fill_opacity=terminal_opacity,
        )
        self.add(dot_left, dot_right)

        # 6. 为了复用与 Resistor 相同的接口，定义一条隐含“主路径”用于端点坐标获取
        self.coil_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.coil_path)

        if label_text:
            self._add_label(label_text, label_position, label_color, label_scale, label_buff)

    @property
    def left_terminal(self):
        """
        返回电感左端（连接点）的坐标。
        """
        return self.coil_path.get_start()

    @property
    def right_terminal(self):
        """
        返回电感右端（连接点）的坐标。
        """
        return self.coil_path.get_end()

    def _add_label(self, text, position, color, scale, buff):
        """
        内部工具：在电感附近创建并附加标签。

        行为与 ``Resistor._add_label`` 保持一致，便于在 Circuit 中统一处理。
        """
        if isinstance(text, str) and text.startswith('$') and text.endswith('$'):
            label = MathTex(text[1:-1], color=color)
        else:
            label = Tex(text, color=color)

        label.scale(scale)
        label.next_to(self, position, buff=buff)

        self.label = VGroup()
        self.label.add(label)
        self.add(self.label)

    def get_creation_animation(self, run_time=2, **kwargs):
        """
        返回一个用于“从无到有”绘制电感的创建动画。

        线圈主体与端点会同时被 Create，适合作为电路搭建过程中的基础动画单元。
        """
        if not self.submobjects:
            return AnimationGroup()

        return AnimationGroup(
            *[Create(m, **kwargs) for m in self.submobjects],
            lag_ratio=0,
            run_time=run_time,
            **kwargs,
        )


class Capacitor(VGroup):
    """
    电容元件的基础可视化类。

    特点：
        - 使用两条平行线段表示电容极板；
        - 与 ``Resistor``、``Inductor`` 保持相同的接口风格（端点、标签、创建动画等）；
        - 支持设置正极极板（显示“+”号），并将该符号归入标签组中。
    """

    def __init__(
        self,
        length: float = 2.0,
        plate_spacing: float = 0.3,
        plate_length: float = 0.8,
        show_terminals: bool = True,
        terminal_radius: float = 0.08,
        terminal_color: ManimColor = WHITE,
        terminal_opacity: float = 1.0,
        terminal_extension: float = 0.5,
        label_text: str | None = None,
        label_position: np.ndarray = UP,
        label_color: ManimColor = WHITE,
        label_scale: float = 0.5,
        label_buff: float = 0.3,
        positive_plate: int | None = None,  # 1 为左极板，2 为右极板
        **kwargs,
    ):
        """
        创建一个电容符号。

        参数说明：
            length:
                电容整体长度（包括两端接线段）。
            plate_spacing:
                两个极板之间的间距。
            plate_length:
                极板线段的长度。
            show_terminals:
                是否在左右两端绘制端点圆点。
            terminal_radius / terminal_color / terminal_opacity:
                端点样式参数。
            terminal_extension:
                接线段长度。
            label_text:
                电容标签文本。
            label_position:
                标签位置。
            positive_plate:
                指定哪个极板为正极（1:左, 2:右）。若为 None 则不显示正号。
            **kwargs:
                传递给内部 VMobject 的绘图配置。
        """
        super().__init__(**kwargs)
        self.length = length
        self.plate_spacing = plate_spacing
        self.plate_length = plate_length
        self.terminal_extension = terminal_extension
        self.label_position = label_position
        self.label_buff = label_buff
        self.positive_plate = positive_plate

        # 1. 计算左右端点位置
        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        # 2. 计算极板位置
        left_plate_x = -plate_spacing / 2
        right_plate_x = plate_spacing / 2

        # 3. 创建接线与极板
        left_lead = Line(initial_left_coord, np.array([left_plate_x, 0, 0]), **kwargs)
        right_lead = Line(np.array([right_plate_x, 0, 0]), initial_right_coord, **kwargs)
        
        left_plate = Line(
            np.array([left_plate_x, plate_length / 2, 0]),
            np.array([left_plate_x, -plate_length / 2, 0]),
            **kwargs
        )
        right_plate = Line(
            np.array([right_plate_x, plate_length / 2, 0]),
            np.array([right_plate_x, -plate_length / 2, 0]),
            **kwargs
        )

        self.body = VGroup(left_lead, right_lead, left_plate, right_plate)
        self.add(self.body)

        # 4. 添加端点
        if show_terminals:
            terminal_opacity = terminal_opacity
        else:
            terminal_opacity = 0.0
        dot_left = Dot(
            initial_left_coord,
            radius=terminal_radius,
            color=terminal_color,
            fill_opacity=terminal_opacity,
        )
        dot_right = Dot(
            initial_right_coord,
            radius=terminal_radius,
            color=terminal_color,
            fill_opacity=terminal_opacity,
        )
        self.add(dot_left, dot_right)

        # 5. 定义主路径
        self.cap_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.cap_path)

        # 6. 添加标签（含极性符号）
        self._add_label(label_text, label_position, label_color, label_scale, label_buff)

    @property
    def left_terminal(self):
        return self.cap_path.get_start()

    @property
    def right_terminal(self):
        return self.cap_path.get_end()

    def _add_label(self, text, position, color, scale, buff):
        """
        创建并附加标签，同时处理正号。
        """
        self.label = VGroup()

        # 1. 主文本标签
        if text:
            if isinstance(text, str) and text.startswith('$') and text.endswith('$'):
                label_obj = MathTex(text[1:-1], color=color)
            else:
                label_obj = Tex(text, color=color)
            label_obj.scale(scale)
            label_obj.next_to(self, position, buff=buff)
            self.label.add(label_obj)

        # 2. 正号符号
        if self.positive_plate in [1, 2]:
            plus_sign = MathTex("+", color=color).scale(scale * 0.8)
            plate_x = -self.plate_spacing / 2 - 0.15 if self.positive_plate == 1 else self.plate_spacing / 2 + 0.15
            # 放在极板上方一点点
            plus_sign.move_to(np.array([plate_x, self.plate_length / 2, 0]))
            self.label.add(plus_sign)

        if self.label.submobjects:
            self.add(self.label)

    def get_creation_animation(self, run_time=2, **kwargs):
        if not self.submobjects:
            return AnimationGroup()
        return AnimationGroup(
            *[Create(m, **kwargs) for m in self.submobjects],
            lag_ratio=0,
            run_time=run_time,
            **kwargs,
        )


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

        # 标签方向与位置校正
        if self.current_angle != 0.0 and hasattr(mobject, 'label'):
            original_direction = np.array(mobject.label_position)
            rotate_proxy = Dot(point=original_direction)
            rotated_direction_proxy = rotate_proxy.rotate_about_origin(self.current_angle)
            new_direction = rotated_direction_proxy.get_center()
            mobject.label.rotate(-self.current_angle)
            mobject.label.next_to(mobject.get_center(), new_direction, buff=mobject.label_buff)

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

# --- 测试场景 ---
class CircuitDemo(Scene):
    """
    演示单个电阻元件的基础渲染效果：
        - 不带端点的电阻；
        - 自定义端点样式（颜色、大小）；
        - 端点继承主体颜色的情况。
    """

    def construct(self):
        # 1. 默认设置（无端点，颜色为默认白色）
        R1 = Resistor(length=2, show_terminals=False)
        R1.shift(UP * 2)

        # 2. 显示端点，并单独设置端点样式
        R2 = Resistor(
            length=4,
            color=RED,
            stroke_width=6,
            show_terminals=True,
            terminal_radius=0.15,
            terminal_color=YELLOW,
        )
        R2.shift(ORIGIN)

        # 3. 显示端点，但不指定端点颜色（端点继承主体颜色 BLUE）
        R3 = Resistor(
            length=2,
            color=BLUE,
            show_terminals=True,
        )
        R3.shift(DOWN * 2)

        # 并行播放三个电阻的创建动画
        self.play(
            R1.get_creation_animation(),
            R2.get_creation_animation(run_time=4),
            R3.get_creation_animation(),
        )
        self.wait(2)


class ChainableCircuitDemo(Scene):
    """
    演示基于游标的链式电路绘制：
        - 从左侧起点依次放置电阻；
        - 使用 ``draw_line`` 通过向量分解绘制 L 形连线；
        - 展示 Circuit 作为一个整体被 Create 的效果。
    """

    def construct(self):
        # 初始化 Circuit，设置起点在屏幕左侧
        circuit = Circuit(start_pos=LEFT * 5)

        # 从起点开始：电阻 + 水平线 + 电阻 + 竖直线 + 电阻 + 闭合回路
        circuit.add_elements(Resistor(length=2, color=BLUE)) \
            .draw_line(RIGHT * 1.5) \
            .add_elements(Resistor(length=2, color=RED)) \
            .draw_line(UP * 3) \
            .add_elements(Resistor(length=2, color=YELLOW)) \
            .draw_line(LEFT * 5.5 + DOWN * 3)

        # 整体创建电路图
        self.play(Create(circuit))
        self.wait(1)


class ThetaCircuitDemo(Scene):
    """
    使用 ``theta`` 控制电阻朝向，构造一个等边三角形电路。
    """

    def construct(self):
        circuit = Circuit(start_pos=LEFT * 2 + DOWN * 1)
        L = 3  # 电阻长度

        # 依次设置 0° / 120° / 240° 的朝向，形成闭合三角形
        circuit.theta(0).add_elements(
            Resistor(
                length=L,
                color=BLUE,
                terminal_extension=0.1,
                label_text=r"$R_1=10\Omega$",
                label_scale=0.6,
                label_position=DOWN,
                label_color=YELLOW,
            )
        ).theta(120).add_elements(
            Resistor(
                length=L,
                color=RED,
                terminal_extension=1.0,
                label_text=r"$R_1=6\Omega$",
                label_scale=0.6,
                label_position=DOWN,
                label_color=GREEN,
            )
        ).theta(240).add_elements(
            Resistor(
                length=L,
                color=YELLOW,
                terminal_extension=1.0,
                label_text=r"$R_1=8\Omega$",
                label_scale=0.6,
                label_position=LEFT,
                label_color=GREEN,
            )
        )

        self.play(Create(circuit))
        self.wait()


class ScaledCircuitDemo(Scene):
    """
    演示在电路中混合使用“正常尺寸”和缩放后的元件：
        - 比较同一电阻符号在缩放前后的视觉差异；
        - 说明对 VGroup 直接 ``scale`` 后，Circuit 仍可正常处理其端点。
    """

    def construct(self):
        circuit = Circuit(start_pos=LEFT * 4)

        L = 3  # 基础长度

        # 正常尺寸的电阻
        R_norm = Resistor(
            length=L,
            label_text=r"$R_{\text{norm}}$",
            label_position=UP,
            label_buff=0.3,
            color=BLUE,
        )

        # 放大 1.5 倍的电阻，用于对比
        R_scaled = Resistor(
            length=L,
            label_text=r"$R_{\text{scaled}}$",
            label_position=DOWN,
            label_buff=0.5,
            color=RED,
        )
        R_scaled.scale(1.5)

        # 在 0° 和 120° 方向依次放入两个电阻，并用一条粗黄色连线闭合
        self.play(
            Create(
                circuit.theta(0)
                .add_elements(R_norm)
                .theta(120)
                .add_elements(R_scaled)
                .draw_line_to(
                    circuit.components[0].left_terminal,
                    color=YELLOW,
                    stroke_width=10,
                )
            )
        )

        self.wait(2)


class StarDeltaTransform(Scene):
    """
    △–Y（Delta–Star）变换的可视化示例场景。

    演示内容：
        - 使用 ``Circuit`` 和 ``Resistor`` 构建 Delta（三角形）和 Star（星形）等效电路；
        - 通过 ``ReplacementTransform`` 将 Delta 中的电阻与 Star 中的电阻建立视觉对应；
        - 辅以节点高亮与公式推导动画，展示等效电阻的计算过程。
    """

    def construct(self):
        # --- 0. 场景装饰：标题与版权 ---

        # 顶部标题：△-Y 变换
        title = Text("△-Y变换", font="Sans", font_size=44, color=YELLOW)
        title.to_edge(UP, buff=0.5)

        # 右下角版权：Made By 零下三度极寒
        # 使用支持中文的字体（如 "SimHei" / "Microsoft YaHei"）
        copyright_info = Text(
            "Made By 零下三度极寒",
            font="SimHei",
            font_size=20,
            fill_opacity=0.6,
            color=GRAY,
        )
        copyright_info.to_edge(DR, buff=0.3)

        # 标题与版权信息淡入
        self.play(Write(title), FadeIn(copyright_info, shift=LEFT))

        # 0. 配置基本元件参数
        R_length = 2.5
        R_buff = 0.4
        
        # --- 1. 创建 Delta (三角形) 电路 (源 Mobject)---
        R12 = Resistor(show_terminals=False, length=R_length, label_text=r'$R_{12}$', label_position=UP, color=BLUE, label_buff=R_buff, label_color=BLUE)
        R23 = Resistor(show_terminals=False, length=R_length, label_text=r'$R_{23}$', label_position=UP, color=GREEN, label_buff=R_buff, label_color=GREEN)
        R31 = Resistor(show_terminals=False, length=R_length, label_text=r'$R_{31}$', label_position=UP, color=RED, label_buff=R_buff, label_color=RED)
        
        delta_circuit = Circuit(start_pos=UP*1.5 + LEFT*1.5)
        # 使用集成版 add_elements：直接指定放置角度
        delta_circuit.add_elements(R12, name="R12", angle_degree=0)
        delta_circuit.add_elements(R23, name="R23", angle_degree=-120)
        delta_circuit.add_elements(R31, name="R31", angle_degree=120)

        node1_coord = R12.left_terminal
        node2_coord = R12.right_terminal
        node3_coord = R31.left_terminal
        
        # 添加 Delta 的节点
        node1_delta = delta_circuit.add_node(node1_coord, label_text="1", label_position=UP+LEFT, label_buff=0.2, name="node1_delta")
        node2_delta = delta_circuit.add_node(node2_coord, label_text="2", label_position=UP+RIGHT, label_buff=0.2, name="node2_delta")
        node3_delta = delta_circuit.add_node(node3_coord, label_text="3", label_position=DOWN, label_buff=0.2, name="node3_delta")

        self.play(Create(delta_circuit), run_time=2)
        self.wait(0.5)

        # --- 2. 创建 Star (星形) 电路 (目标 Mobject) ---
        center_node_coord = delta_circuit.get_center()
        star_circuit = Circuit(start_pos=center_node_coord)
        
        # 2.1 定义星形电阻
        R1 = Resistor(show_terminals=False, length=R_length, label_text=r"$R_1$", label_position=UP, color=BLUE, label_buff=R_buff, label_color=BLUE)
        R2 = Resistor(show_terminals=False, length=R_length, label_text=r"$R_2$", label_position=UP, color=GREEN, label_buff=R_buff, label_color=GREEN)
        R3 = Resistor(show_terminals=False, length=R_length, label_text=r"$R_3$", label_position=UP, color=RED, label_buff=R_buff, label_color=RED)

        # 计算放置角度
        angle1 = angle_of_vector(node1_coord - center_node_coord) / DEGREES
        angle2 = angle_of_vector(node2_coord - center_node_coord) / DEGREES
        angle3 = angle_of_vector(node3_coord - center_node_coord) / DEGREES
        # print(f"Angle A: {angle_A}, B: {angle_B}, C: {angle_C}")

        # 2.2 🚀 利用集成版 add_elements / add_node 构建完整的 Star 电路（含端点）
        #      使用 hold() 保持游标在中心点，实现“从中心向四周辐射”放置多个元件
        
        # 确保游标位于中心节点
        star_circuit.move_cursor_to(center_node_coord)
        
        # --- R1 分支 ---
        # 使用 hold()，让放置 R1 后游标仍停留在中心
        star_circuit.hold().add_elements(R1, name="R1", angle_degree=angle1)
        # 补全星形电路的点1 (使用 R1 的右端作为坐标)
        node1_star = star_circuit.add_node(R1.right_terminal, label_text="1", label_position=UP+LEFT, label_buff=0.2)
        
        # --- R2 分支 ---
        star_circuit.hold().add_elements(R2, name="R2", angle_degree=angle2)
        # 补全星形电路的点2 (使用 R2 的右端作为坐标)
        node2_star = star_circuit.add_node(R2.right_terminal, label_text="2", label_position=UP+RIGHT, label_buff=0.2)
        
        # --- R3 分支 ---
        star_circuit.hold().add_elements(R3, name="R3", angle_degree=angle3)
        # 补全星形电路的点3 (使用 R3 的右端作为坐标)
        node3_star = star_circuit.add_node(R3.right_terminal, label_text="3", label_position=DOWN, label_buff=0.2)

        # 添加中心节点 N
        node_N = star_circuit.add_node(center_node_coord, label_text="N", label_position=UP, label_buff=0.2)
        
        # 此时 star_circuit 包含了 R*, node_star, node_N 及其标签
        # 我们暂时不显示它，只用它作为 Transform 的目标属性来源
        
        # 1. 移除原始 Delta 电阻
        # 原始电阻会迅速消失，让位给正在变形的副本
        self.remove(delta_circuit)
        
        # --- 3. 执行核心变换动画 ---
        # 3.1 变换动画
        self.play(
            # 1. 电阻形变 (R1+R3 -> R12)
            ReplacementTransform(R12.body.copy(), R2.body),
            ReplacementTransform(R23.body.copy(), R3.body),
            ReplacementTransform(R31.body.copy(), R1.body),
            ReplacementTransform(R12.body.copy().reverse_points(), R1.body),
            ReplacementTransform(R23.body.copy().reverse_points(), R2.body),
            ReplacementTransform(R31.body.copy().reverse_points(), R3.body),

            # 2. 标签融合变换 (R1, R3 标签 -> R12 标签)
            # R12.label.animate.become(R1.label),
            # R31.label.animate.become(R1.label.copy()),
            # R23.label.animate.become(R2.label),
            # R12.label.copy().animate.become(R2.label.copy()),
            # R31.label.copy().animate.become(R3.label),
            # R23.label.copy().animate.become(R3.label.copy()),
            ReplacementTransform(R12.label.copy(), R1.label),
            ReplacementTransform(R31.label.copy(), R1.label),
            ReplacementTransform(R23.label.copy(), R2.label),
            ReplacementTransform(R12.label.copy(), R2.label),
            ReplacementTransform(R31.label.copy(), R3.label),
            ReplacementTransform(R23.label.copy(), R3.label),

            # 3. 显现星形电路特有的节点 N和新的端点 1, 2, 3
            # 注意：Transform 只处理了电阻，我们需要 FadeIn 星形电路的节点
            FadeIn(node_N, node_N.label),
            ReplacementTransform(node1_delta.copy(), node1_star),
            ReplacementTransform(node2_delta.copy(), node2_star),
            ReplacementTransform(node3_delta.copy(), node3_star),
            ReplacementTransform(node1_delta.label.copy(), node1_star.label),
            ReplacementTransform(node2_delta.label.copy(), node2_star.label),
            ReplacementTransform(node3_delta.label.copy(), node3_star.label),
            run_time=3.5,
            rate_func=smooth
        )
        
        self.wait(0.5)
        
        # --- 4. 最终布局动画 (分离视图) ---
        # 4.1 定义公式
        formula_R1 = MathTex(r"R_1 = \frac{R_{12} R_{31}}{R_{12} + R_{23} + R_{31}}", font_size=36, color=BLUE)
        formula_R2 = MathTex(r"R_2 = \frac{R_{12} R_{23}}{R_{12} + R_{23} + R_{31}}", font_size=36, color=GREEN)
        formula_R3 = MathTex(r"R_3 = \frac{R_{23} R_{31}}{R_{12} + R_{23} + R_{31}}", font_size=36, color=RED)

        formula_group = VGroup(formula_R1, formula_R2, formula_R3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        formula_group.to_edge(DOWN)

        # --- 4.2 最终布局动画：两步走方案 ---

        # 准备左侧的“分身”
        # 将副本初始位置设在星形电路当前的中心，实现“钻出来”的效果
        # delta_emerge = delta_circuit.copy().move_to(star_circuit.get_center())
        # # 第一步：星形向右，三角形从星形身上“钻”出来向左
        # self.play(
        #     # 星形平移至右侧
        #     star_circuit.animate.to_edge(RIGHT, buff=1.5),
        #     # 🚀 直接让 Delta 从中心点“长”出来，不需要 FadeIn 和 scale
        #     GrowFromPoint(delta_emerge.to_edge(LEFT, buff=1.5), center_node_coord),
        #     run_time=2,
        #     rate_func=smooth
        # )

        delta_target = delta_circuit.copy().to_edge(LEFT, buff=1.5)
        self.play(
            star_circuit.animate.to_edge(RIGHT, buff=1.5),
            
            # 🚀 关键：带位移的淡入，shift 方向指向左侧
            # 这会产生一种被“推”出来的感觉
            FadeIn(delta_target, target_position=node_N, scale=0.1),
            
            # 可选：加一个高光脉冲，强调“钻出来”那一刻的能量
            Flash(delta_target.get_center(), line_length=1.0, color=YELLOW, flash_radius=1.0),
            
            run_time=3,
            rate_func=smooth
        )
        
        self.wait(0.2) # 微小的停顿，增加节奏感

        # 第二步：书写公式
        # self.play(
        #     Write(formula_group),
        #     run_time=1.5
        # )

        # --- 5. 公式细粒化推导 (以 R1 为例) ---

        # 5.1 准备公式各部分（带颜色匹配）
        # 注意：这里先不写完整公式，而是拆解开，方便做 Transform
        
        # 5.2 第一步：突出 R1 元件并提取符号
        # self.add(index_labels(formula_R1[0]))
        self.play(
            # 突出显示 R1 及其标签
            Indicate(star_circuit.R1, color=BLUE),
            TransformFromCopy(star_circuit.R1.label.copy(), formula_R1[0][:2].set_color(BLUE)),
            run_time=1.5
        )
        self.play(Write(formula_R1[0][2]), Write(formula_R1[0][9]), run_time=0.5)
        self.play(
            Indicate(delta_target.R12, color=BLUE),
            Indicate(delta_target.R31, color=RED),
            TransformFromCopy(delta_target.R12.label.copy(), formula_R1[0][3:6].set_color(BLUE)),
            TransformFromCopy(delta_target.R31.label.copy(), formula_R1[0][6:9].set_color(RED)),
            run_time=2
        )
        self.play(
            Indicate(delta_target.R12, color=BLUE),
            Indicate(delta_target.R23, color=GREEN),
            Indicate(delta_target.R31, color=RED),
            TransformFromCopy(delta_target.R12.label.copy(), formula_R1[0][10:13].set_color(BLUE)),
            TransformFromCopy(delta_target.R23.label.copy(), formula_R1[0][14:17].set_color(GREEN)),
            TransformFromCopy(delta_target.R31.label.copy(), formula_R1[0][18:].set_color(RED)),
            Write(formula_R1[0][13]), Write(formula_R1[0][17]),
            run_time=2
        )
     
        self.wait(1)

        # --- 5.3 推导 R2 公式 ---
        # R2 = (R12 * R23) / (R12 + R23 + R31)
        self.play(
            # 突出显示 R2 及其标签
            Indicate(star_circuit.R2, color=GREEN),
            TransformFromCopy(star_circuit.R2.label.copy(), formula_R2[0][:2].set_color(GREEN)),
            run_time=1.5
        )
        # 写等号和分式线
        self.play(Write(formula_R2[0][2]), Write(formula_R2[0][9]), run_time=0.5)

        # 提取分子：R12 和 R23 (夹着 R2 的两个电阻)
        self.play(
            Indicate(delta_target.R12, color=BLUE),
            Indicate(delta_target.R23, color=GREEN),
            TransformFromCopy(delta_target.R12.label.copy(), formula_R2[0][3:6].set_color(BLUE)),
            TransformFromCopy(delta_target.R23.label.copy(), formula_R2[0][6:9].set_color(GREEN)),
            run_time=2
        )

        # 提取分母：R12 + R23 + R31
        self.play(
            Indicate(delta_target.R12, color=BLUE),
            Indicate(delta_target.R23, color=GREEN),
            Indicate(delta_target.R31, color=RED),
            TransformFromCopy(delta_target.R12.label.copy(), formula_R2[0][10:13].set_color(BLUE)),
            TransformFromCopy(delta_target.R23.label.copy(), formula_R2[0][14:17].set_color(GREEN)),
            TransformFromCopy(delta_target.R31.label.copy(), formula_R2[0][18:].set_color(RED)),
            Write(formula_R2[0][13]), Write(formula_R2[0][17]), # 写加号
            run_time=2
        )
        self.wait(1)

        # --- 5.4 推导 R3 公式 ---
        # R3 = (R23 * R31) / (R12 + R23 + R31)
        self.play(
            # 突出显示 R3 及其标签
            Indicate(star_circuit.R3, color=RED),
            TransformFromCopy(star_circuit.R3.label.copy(), formula_R3[0][:2].set_color(RED)),
            run_time=1.5
        )
        # 写等号和分式线
        self.play(Write(formula_R3[0][2]), Write(formula_R3[0][9]), run_time=0.5)

        # 提取分子：R23 和 R31 (夹着 R3 的两个电阻)
        self.play(
            Indicate(delta_target.R23, color=GREEN),
            Indicate(delta_target.R31, color=RED),
            TransformFromCopy(delta_target.R23.label.copy(), formula_R3[0][3:6].set_color(GREEN)),
            TransformFromCopy(delta_target.R31.label.copy(), formula_R3[0][6:9].set_color(RED)),
            run_time=2
        )

        # 提取分母：R12 + R23 + R31
        self.play(
            Indicate(delta_target.R12, color=BLUE),
            Indicate(delta_target.R23, color=GREEN),
            Indicate(delta_target.R31, color=RED),
            TransformFromCopy(delta_target.R12.label.copy(), formula_R3[0][10:13].set_color(BLUE)),
            TransformFromCopy(delta_target.R23.label.copy(), formula_R3[0][14:17].set_color(GREEN)),
            TransformFromCopy(delta_target.R31.label.copy(), formula_R3[0][18:].set_color(RED)),
            Write(formula_R3[0][13]), Write(formula_R3[0][17]), # 写加号
            run_time=2
        )
        self.wait(1)


class InductorDemo(Scene):
    """
    演示电感元件 ``Inductor`` 的基础渲染与参数效果：
        - 调整线圈圈数 ``turns``；
        - 控制端点是否显示以及端点样式；
        - 展示标签在不同方向上的放置方式。
    """

    def construct(self):
        # 电感 1：默认参数，位于上方
        L1 = Inductor(
            length=2.5,
            turns=3,
            show_terminals=True,
            label_text=r"$L_1$",
            label_position=UP,
            label_color=YELLOW,
        ).shift(UP * 2.0)

        # 电感 2：圈数更多，端点变大，位于中间
        L2 = Inductor(
            length=3.0,
            turns=5,
            show_terminals=True,
            terminal_radius=0.12,
            terminal_color=GREEN,
            label_text=r"$L_2$",
            label_position=DOWN,
            label_color=GREEN,
        )

        # 电感 3：不显示端点，仅作为符号展示，位于下方
        L3 = Inductor(
            length=2.5,
            turns=4,
            show_terminals=False,
            label_text=r"$L_3$",
            label_position=UP,
            label_color=RED,
        ).shift(DOWN * 2.0)

        # 并行播放三个电感的创建动画，便于比较外观差异
        self.play(
            L1.get_creation_animation(run_time=2),
            L2.get_creation_animation(run_time=2),
            L3.get_creation_animation(run_time=2),
        )
        self.wait(2)


class CapacitorDemo(Scene):
    """
    演示电容元件 ``Capacitor`` 的基础渲染与参数效果：
        - 基础电容符号；
        - 设置正极极板与极性符号；
        - 在 Circuit 中使用电容。
    """

    def construct(self):
        # 1. 基础电容，不带极性
        C1 = Capacitor(
            length=2,
            label_text=r"$C_1$",
            label_position=UP,
            color=BLUE
        ).shift(UP * 2 + LEFT * 3)

        # 2. 带正极的电容（左极板为正）
        C2 = Capacitor(
            length=2,
            positive_plate=1,
            label_text=r"$C_2$",
            label_position=UP,
            color=RED
        ).shift(UP * 2 + RIGHT * 3)

        # 3. 带正极的电容（右极板为正）
        C3 = Capacitor(
            length=2,
            positive_plate=2,
            label_text=r"$C_3$",
            label_position=DOWN,
            color=GREEN
        ).shift(DOWN * 2 + LEFT * 3)

        # 4. 在 Circuit 中链式添加电容
        circuit = Circuit(start_pos=DOWN * 2 + RIGHT * 1)
        circuit.add_elements(
            Capacitor(length=2, label_text=r"$C_4$", color=YELLOW),
            name="C4",
            angle_degree=90
        ).draw_line(RIGHT * 2).add_elements(
            Capacitor(length=2, positive_plate=1, label_text=r"$C_5$", color=PURPLE),
            name="C5",
            angle_degree=0
        )

        self.play(
            C1.get_creation_animation(),
            C2.get_creation_animation(),
            C3.get_creation_animation(),
            Create(circuit),
            run_time=3
        )
        self.wait(2)
