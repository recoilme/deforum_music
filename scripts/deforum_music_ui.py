import modules.scripts as scripts
import gradio as gr
import os

from modules import script_callbacks, ui
import scripts.deforum_music as deforum_music



def reset_values():
    # Сброс к начальным значениям для каждого поля
    return "extensions/deforum_music/_deforum_music.txt", "deforum_music.txt", "extensions/deforum_music/example.mp3", \
            -1.4, 1.4, 3, -1.4, 1.4, 3, -0.5, 5, 3, \
            -0.4, 0.4, 6, -0.4, 0.4, 6, -0.4, 0.4, 6, \
            0.45, 0.65, 1, 5, 15, 1, "Autumn,  golden hour. Maple leaves are swirling in the wind. thunderstorm, swirling motion, wind's playful touch. White, snowy mountain range, majestic peaks, scattered across the sky. Warm hues of orange and red.  Keywords: Autumn, storm, apple tree, snow.\nWinter, evening. Snowflakes are swirling in the wind. A serene lake reflects the vibrant colors of the scene. In the foreground, a quaint wooden bridge arches gracefully over the water. The bridge's steel frame is weathered by time and use, yet maintains an elegant allure. A lantern with a warm glow hangs nearby, casting dancing shadows on the water.\nSpring, bloom. Rose petals swirl in a dance, xtial Spring emerges, xtial Summer emerges,  pure summer afterset. Vibrant colors burst, summer flowers bloom, summer's warm hues take center stage. Spring's sweet fragrance wafts through the air,  A clear, tranquil scene unfolds as the first light of summer envelops the garden. A gentle breeze rustles the leaves, carrying the sweet scent of blossoms. "

# TODO: add more UI components (cf. https://gradio.app/docs/#components)
def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as tab:
        with gr.Row():  
            dm_base_settings = gr.Textbox(label="deforum base settings path", placeholder="base settigs", value="extensions/deforum_music/_deforum_music.txt")
            dm_result_settings = gr.Textbox(label="deforum resulting settings path", placeholder="result settigs", value="deforum_music.txt")
        with gr.Row():
            dm_audio = gr.Textbox(label="soundtrack path", placeholder="mp3",value="extensions/deforum_music/example.mp3")
        with gr.Row():
            with gr.Column():
                with gr.Row(): 
                    gr.Markdown("#### X", min_width=50)
                    dm_x_min = gr.Number(label="x_Min", value=-1.4, step=0.1, min_width=100)
                    dm_x_max = gr.Number(label="x_Max", value=1.4, step=0.1, min_width=100)
                    dm_x_cad = gr.Number(label="SmoothX", value=3, step=1, min_width=100)
                with gr.Row():   
                    gr.Markdown("#### Y", min_width=50)
                    dm_y_min = gr.Number(label="y_Min", value=-1.4, step=0.1, min_width=100)
                    dm_y_max = gr.Number(label="y_Max", value=1.4, step=0.1, min_width=100)
                    dm_y_cad = gr.Number(label="SmoothY", value=3, step=1, min_width=100)
                with gr.Row():
                    gr.Markdown("#### Z", min_width=50)
                    dm_z_min = gr.Number(label="z_Min", value=-0.5, step=0.1, min_width=100)
                    dm_z_max = gr.Number(label="z_Max", value=5, step=0.1, min_width=100)
                    dm_z_cad = gr.Number(label="SmoothZ", value=3, step=1, min_width=100)
            with gr.Column():
                with gr.Row(): 
                    gr.Markdown("#### 3dX", min_width=50)
                    dm_3dX_min = gr.Number(label="3dX_Min", value=-0.4, step=0.1, min_width=100)
                    dm_3dX_max = gr.Number(label="3dX_Max", value=0.4, step=0.1, min_width=100)
                    dm_3dX_cad = gr.Number(label="Smooth3dX", value=6, step=1, min_width=100)
                with gr.Row():   
                    gr.Markdown("#### 3dY", min_width=50)
                    dm_3dY_min = gr.Number(label="3dY_Min", value=-0.4, step=0.1, min_width=100)
                    dm_3dY_max = gr.Number(label="3dY_Max", value=0.4, step=0.1, min_width=100)
                    dm_3dY_cad = gr.Number(label="Smooth3dY", value=6, step=1, min_width=100)
                with gr.Row():
                    gr.Markdown("#### 3dZ", min_width=50)
                    dm_3dZ_min = gr.Number(label="3dZ_Min", value=-0.4, step=0.1, min_width=100)
                    dm_3dZ_max = gr.Number(label="3dZ_Max", value=0.4, step=0.1, min_width=100)
                    dm_3dZ_cad = gr.Number(label="Smooth3dZ", value=6, step=1, min_width=100)
        with gr.Row():
            with gr.Column():
                with gr.Row(): 
                    gr.Markdown("#### Str", min_width=50)
                    dm_str_min = gr.Number(label="str_Min", value=0.45, step=0.01, min_width=100)
                    dm_str_max = gr.Number(label="str_Max", value=0.65, step=0.01, min_width=100)
                    dm_str_cad = gr.Number(label="SmoothStr", value=1, step=1, min_width=100)
            with gr.Column():
                with gr.Row(): 
                    gr.Markdown("#### Cfg", min_width=50)
                    dm_cfg_min = gr.Number(label="cfg_Min", value=5, step=0.1, min_width=100)
                    dm_cfg_max = gr.Number(label="cfg_Max", value=15, step=0.1, min_width=100)
                    dm_cfg_cad = gr.Number(label="SmoothCfg", value=1, step=1, min_width=100)
        with gr.Row():
            dm_prompt = gr.Textbox(label="Prompts", show_label=True, lines=7, placeholder="Prompts (each from new line)",value="Autumn,  golden hour. Maple leaves are swirling in the wind. thunderstorm, swirling motion, wind's playful touch. White, snowy mountain range, majestic peaks, scattered across the sky. Warm hues of orange and red.  Keywords: Autumn, storm, apple tree, snow.\nWinter, evening. Snowflakes are swirling in the wind. A serene lake reflects the vibrant colors of the scene. In the foreground, a quaint wooden bridge arches gracefully over the water. The bridge's steel frame is weathered by time and use, yet maintains an elegant allure. A lantern with a warm glow hangs nearby, casting dancing shadows on the water.\nSpring, bloom. Rose petals swirl in a dance, xtial Spring emerges, xtial Summer emerges,  pure summer afterset. Vibrant colors burst, summer flowers bloom, summer's warm hues take center stage. Spring's sweet fragrance wafts through the air,  A clear, tranquil scene unfolds as the first light of summer envelops the garden. A gentle breeze rustles the leaves, carrying the sweet scent of blossoms."
        with gr.Row(): 
            dm_out = gr.Textbox(label="Result")
        with gr.Row():
            dm_run_btn = gr.Button("Run",variant='primary')
            dm_run_btn.click(fn=deforum_music.calculate, inputs=[dm_base_settings, dm_result_settings, dm_audio,
                     dm_x_min, dm_x_max, dm_x_cad,
                     dm_y_min, dm_y_max, dm_y_cad,
                     dm_z_min, dm_z_max, dm_z_cad,
                     dm_3dX_min, dm_3dX_max, dm_3dX_cad,
                     dm_3dY_min, dm_3dY_max, dm_3dY_cad,
                     dm_3dZ_min, dm_3dZ_max, dm_3dZ_cad,
                     dm_str_min, dm_str_max, dm_str_cad,
                     dm_cfg_min, dm_cfg_max, dm_cfg_cad,
                     dm_prompt], outputs=dm_out)
            dm_reset_btn = gr.Button("Reset")
            dm_reset_btn.click(fn=reset_values, inputs=[],
            outputs=[dm_base_settings, dm_result_settings, dm_audio,
                     dm_x_min, dm_x_max, dm_x_cad,
                     dm_y_min, dm_y_max, dm_y_cad,
                     dm_z_min, dm_z_max, dm_z_cad,
                     dm_3dX_min, dm_3dX_max, dm_3dX_cad,
                     dm_3dY_min, dm_3dY_max, dm_3dY_cad,
                     dm_3dZ_min, dm_3dZ_max, dm_3dZ_cad,
                     dm_str_min, dm_str_max, dm_str_cad,
                     dm_cfg_min, dm_cfg_max, dm_cfg_cad,
                     dm_prompt])       

    return [(tab, "Deforum Music", "deforum_music")]

script_callbacks.on_ui_tabs(on_ui_tabs)