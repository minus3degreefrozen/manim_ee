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

        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        start_point = LEFT * (length / 2 - self.terminal_extension)
        end_point = RIGHT * (length / 2 - self.terminal_extension)
        step = (length - self.terminal_extension * 2) / (zigzag_count * 2 + 2)
        points = [initial_left_coord, start_point]
        current_x = start_point[0] + step
        for i in range(zigzag_count * 2 + 1):
            y_offset = 0.3 if i % 2 == 0 else -0.3
            points.append(np.array([current_x, y_offset, 0]))
            current_x += step
        points.append(end_point)
        points.append(initial_right_coord)

        self.resistor_path = VMobject(**kwargs).set_points_as_corners(points)
        self.body = VGroup(self.resistor_path)

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
        return self.resistor_path.get_start()

    @property
    def right_terminal(self):
        return self.resistor_path.get_end()
    
    def _add_label(self, text, position, color, scale, buff):
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
        if not self.submobjects:
            return AnimationGroup()

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
        """
        super().__init__(**kwargs)
        self.length = length
        self.turns = max(1, int(turns))
        self.terminal_extension = terminal_extension
        self.label_position = label_position
        self.label_buff = label_buff

        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        coil_length = length - 2 * self.terminal_extension
        coil_length = max(coil_length, 0.1)
        turn_span = coil_length / self.turns

        components: list[Mobject] = []

        left_start = initial_left_coord
        left_end = left_start + RIGHT * self.terminal_extension
        right_end = initial_right_coord
        right_start = right_end + LEFT * self.terminal_extension

        left_lead = Line(left_start, left_end, **kwargs)
        right_lead = Line(right_start, right_end, **kwargs)
        components.extend([left_lead, right_lead])

        coil_start = left_end
        for i in range(self.turns):
            p_start = coil_start + RIGHT * (i * turn_span)
            p_end = coil_start + RIGHT * ((i + 1) * turn_span)
            arc = ArcBetweenPoints(p_start, p_end, angle=-PI, **kwargs)
            components.append(arc)

        self.body = VGroup(*components)
        self.add(self.body)

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

        self.coil_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.coil_path)

        if label_text:
            self._add_label(label_text, label_position, label_color, label_scale, label_buff)

    @property
    def left_terminal(self):
        return self.coil_path.get_start()

    @property
    def right_terminal(self):
        return self.coil_path.get_end()

    def _add_label(self, text, position, color, scale, buff):
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
        positive_plate: int | None = None,
        **kwargs,
    ):
        """
        创建一个电容符号。
        """
        super().__init__(**kwargs)
        self.length = length
        self.plate_spacing = plate_spacing
        self.plate_length = plate_length
        self.terminal_extension = terminal_extension
        self.label_position = label_position
        self.label_buff = label_buff
        self.positive_plate = positive_plate

        initial_left_coord = LEFT * (length / 2)
        initial_right_coord = RIGHT * (length / 2)

        left_plate_x = -plate_spacing / 2
        right_plate_x = plate_spacing / 2

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

        self.cap_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.cap_path)

        self._add_label(label_text, label_position, label_color, label_scale, label_buff)

    @property
    def left_terminal(self):
        return self.cap_path.get_start()

    @property
    def right_terminal(self):
        return self.cap_path.get_end()

    def _add_label(self, text, position, color, scale, buff):
        self.label = VGroup()

        if text:
            if isinstance(text, str) and text.startswith('$') and text.endswith('$'):
                label_obj = MathTex(text[1:-1], color=color)
            else:
                label_obj = Tex(text, color=color)
            label_obj.scale(scale)
            label_obj.next_to(self, position, buff=buff)
            self.label.add(label_obj)

        if self.positive_plate in [1, 2]:
            plus_sign = MathTex("+", color=color).scale(scale * 0.8)
            plate_x = -self.plate_spacing / 2 - 0.15 if self.positive_plate == 1 else self.plate_spacing / 2 + 0.15
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
