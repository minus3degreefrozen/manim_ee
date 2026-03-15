from manim import *
import numpy as np


class TwoTerminalElement(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.body = VGroup()
        self.add(self.body)

    def get_label_text(self, index: int = 0) -> Mobject | None:
        if hasattr(self, "label_text_group") and len(self.label_text_group) > index:
            return self.label_text_group[index]
        return None

    def _set_main_path(self, path: VMobject):
        self._main_path = path

    @property
    def left_terminal(self):
        return self._main_path.get_start()

    @property
    def right_terminal(self):
        return self._main_path.get_end()

    def _add_terminals(
        self,
        show_terminals: bool,
        terminal_radius: float,
        terminal_color: ManimColor,
        terminal_opacity: float,
        initial_left_coord: np.ndarray,
        initial_right_coord: np.ndarray,
    ):
        opacity = terminal_opacity if show_terminals else 0.0
        dot_left = Dot(initial_left_coord, radius=terminal_radius, color=terminal_color, fill_opacity=opacity)
        dot_right = Dot(initial_right_coord, radius=terminal_radius, color=terminal_color, fill_opacity=opacity)
        self.body.add(dot_left, dot_right)
        return dot_left, dot_right

    def _ensure_label_groups(self):
        if not hasattr(self, "label"):
            self.label = VGroup()
            self.label_text_group = VGroup()
            self.label_mark_group = VGroup()
            self.label.add(self.label_text_group, self.label_mark_group)
            self.add(self.label)
        return self.label, self.label_text_group, self.label_mark_group

    def _add_text_label(self, text: str | None, position: np.ndarray, color: ManimColor, scale: float, buff: float):
        if not text:
            return None

        if isinstance(text, str) and text.startswith("$") and text.endswith("$"):
            label_obj = MathTex(text[1:-1], color=color)
        else:
            label_obj = Tex(text, color=color)

        label_obj.scale(scale)
        label_obj.next_to(self, position, buff=buff)

        _, label_text_group, _ = self._ensure_label_groups()
        label_text_group.add(label_obj)
        return label_obj

    def update_label_for_angle(self, angle: float):
        if not hasattr(self, "label"):
            return self

        original_direction = np.array(getattr(self, "label_position", UP))
        rotate_proxy = Dot(point=original_direction)
        rotated_direction_proxy = rotate_proxy.rotate_about_origin(angle)
        new_direction = rotated_direction_proxy.get_center()

        buff = getattr(self, "label_buff", 0.3)

        if hasattr(self, "label_text_group"):
            self.label_text_group.rotate(-angle)
            self.label_text_group.next_to(self.get_center(), new_direction, buff=buff)
            if hasattr(self, "label_mark_group"):
                self.label_mark_group.rotate(-angle)
        else:
            self.label.rotate(-angle)
            self.label.next_to(self.get_center(), new_direction, buff=buff)

        return self

    def get_creation_animation(self, run_time=2, **kwargs):
        if not self.submobjects:
            return AnimationGroup()

        return AnimationGroup(
            *[Create(m, **kwargs) for m in self.submobjects],
            lag_ratio=0,
            run_time=run_time,
            **kwargs,
        )


class Resistor(TwoTerminalElement):
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
        left_terminal_coord: np.ndarray | None = None,
        right_terminal_coord: np.ndarray | None = None,
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

        if left_terminal_coord is not None and right_terminal_coord is not None:
            left_terminal_coord = np.array(left_terminal_coord, dtype=float)
            right_terminal_coord = np.array(right_terminal_coord, dtype=float)
            length = float(np.linalg.norm(right_terminal_coord - left_terminal_coord))

        self.length = length
        self.zigzag_count = zigzag_count
        max_terminal_extension = max(self.length / 2 - 0.1, 0.0)
        self.terminal_extension = min(terminal_extension, max_terminal_extension)
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
        self.body.add(self.resistor_path)
        self._set_main_path(self.resistor_path)

        self._add_terminals(
            show_terminals,
            terminal_radius,
            terminal_color,
            terminal_opacity,
            initial_left_coord,
            initial_right_coord,
        )

        if label_text:
            self._add_text_label(label_text, label_position, label_color, label_scale, label_buff)

        if left_terminal_coord is not None and right_terminal_coord is not None:
            desired_vec = np.array(right_terminal_coord, dtype=float) - np.array(left_terminal_coord, dtype=float)
            if np.allclose(desired_vec, 0):
                raise ValueError("left_terminal_coord 与 right_terminal_coord 重合，无法确定元件方向与长度。")
            desired_angle = angle_of_vector(desired_vec)
            self.rotate(desired_angle, about_point=ORIGIN)
            self.shift(np.array(left_terminal_coord, dtype=float) - np.array(self.left_terminal, dtype=float))
            self.update_label_for_angle(desired_angle)
 

class Inductor(TwoTerminalElement):
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
        left_terminal_coord: np.ndarray | None = None,
        right_terminal_coord: np.ndarray | None = None,
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

        if left_terminal_coord is not None and right_terminal_coord is not None:
            left_terminal_coord = np.array(left_terminal_coord, dtype=float)
            right_terminal_coord = np.array(right_terminal_coord, dtype=float)
            length = float(np.linalg.norm(right_terminal_coord - left_terminal_coord))

        self.length = length
        self.turns = max(1, int(turns))
        max_terminal_extension = max(self.length / 2 - 0.05, 0.0)
        self.terminal_extension = min(terminal_extension, max_terminal_extension)
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

        self.body.add(*components)

        self._add_terminals(
            show_terminals,
            terminal_radius,
            terminal_color,
            terminal_opacity,
            initial_left_coord,
            initial_right_coord,
        )

        self.coil_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.coil_path)
        self._set_main_path(self.coil_path)

        if label_text:
            self._add_text_label(label_text, label_position, label_color, label_scale, label_buff)

        if left_terminal_coord is not None and right_terminal_coord is not None:
            desired_vec = np.array(right_terminal_coord, dtype=float) - np.array(left_terminal_coord, dtype=float)
            if np.allclose(desired_vec, 0):
                raise ValueError("left_terminal_coord 与 right_terminal_coord 重合，无法确定元件方向与长度。")
            desired_angle = angle_of_vector(desired_vec)
            self.rotate(desired_angle, about_point=ORIGIN)
            self.shift(np.array(left_terminal_coord, dtype=float) - np.array(self.left_terminal, dtype=float))
            self.update_label_for_angle(desired_angle)


class Capacitor(TwoTerminalElement):
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
        left_terminal_coord: np.ndarray | None = None,
        right_terminal_coord: np.ndarray | None = None,
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

        if left_terminal_coord is not None and right_terminal_coord is not None:
            left_terminal_coord = np.array(left_terminal_coord, dtype=float)
            right_terminal_coord = np.array(right_terminal_coord, dtype=float)
            length = float(np.linalg.norm(right_terminal_coord - left_terminal_coord))

        if length < plate_spacing:
            raise ValueError(f"length({length}) 小于 plate_spacing({plate_spacing})，无法绘制电容。")

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

        self.body.add(left_lead, right_lead, left_plate, right_plate)

        self._add_terminals(
            show_terminals,
            terminal_radius,
            terminal_color,
            terminal_opacity,
            initial_left_coord,
            initial_right_coord,
        )

        self.cap_path = Line(initial_left_coord, initial_right_coord).set_stroke(opacity=0)
        self.body.add(self.cap_path)
        self._set_main_path(self.cap_path)

        self._add_text_label(label_text, label_position, label_color, label_scale, label_buff)

        if self.positive_plate in [1, 2]:
            _, _, label_mark_group = self._ensure_label_groups()
            plus_sign = MathTex("+", color=label_color).scale(label_scale * 0.8)
            plate_x = -self.plate_spacing / 2 - 0.15 if self.positive_plate == 1 else self.plate_spacing / 2 + 0.15
            plus_sign.move_to(np.array([plate_x, self.plate_length / 2, 0]))
            label_mark_group.add(plus_sign)

        if left_terminal_coord is not None and right_terminal_coord is not None:
            desired_vec = np.array(right_terminal_coord, dtype=float) - np.array(left_terminal_coord, dtype=float)
            if np.allclose(desired_vec, 0):
                raise ValueError("left_terminal_coord 与 right_terminal_coord 重合，无法确定元件方向与长度。")
            desired_angle = angle_of_vector(desired_vec)
            self.rotate(desired_angle, about_point=ORIGIN)
            self.shift(np.array(left_terminal_coord, dtype=float) - np.array(self.left_terminal, dtype=float))
            self.update_label_for_angle(desired_angle)
