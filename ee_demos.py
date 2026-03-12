from manim import *

from ee_circuit import Circuit
from ee_elements import Capacitor, Inductor, Resistor


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
