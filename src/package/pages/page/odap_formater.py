import re
from pathlib import Path
from typing import Any

import Levenshtein
import flet as ft
import pandas as pd
from pandas import DataFrame
from pypinyin import lazy_pinyin

from ..toolbox_page import ToolBoxPage
from ...util import json_loader
from ...util.resource_path import resource_path


class ODAPFormater(ToolBoxPage):
    def __init__(self, page: ft.Page):
        self.page = page

    def gui(self):
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                file_path.value = e.files[0].path
                self.page.update()

        file_picker = ft.FilePicker(on_result=on_file_selected)
        file_path = ft.TextField(label="待增加英文表头的文件", read_only=True, expand=True)
        self.page.overlay.append(file_picker)

        def on_dir_selected(e: ft.FilePickerResultEvent):
            if e.path:
                dir_path.value = e.path
                self.page.update()

        dir_path_picker = ft.FilePicker(on_result=on_dir_selected)
        dir_path = ft.TextField(label="选择输出文件夹", read_only=True, expand=True)
        self.page.overlay.append(dir_path_picker)

        check_box = ft.Checkbox(label="启用缩写模式", value=False)

        # 进度条相关控件
        progress_ring = ft.ProgressRing(visible=False)
        finished_icon = ft.Icon(ft.Icons.DONE, color="green", visible=False)
        error_icon = ft.Icon(ft.Icons.ERROR, color="red", visible=False)
        progress_text = ft.Text(value="")
        return ft.Column(
            [
                # 文件选择
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.UPLOAD_FILE,
                            style=ft.ButtonStyle(shape=ft.CircleBorder()),  # 让按钮变成圆形
                            on_click=lambda _: file_picker.pick_files()
                        ),
                        file_path,
                    ],
                    expand=True
                ),
                # 输出文件夹选择
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.OUTPUT_ROUNDED,
                        style=ft.ButtonStyle(shape=ft.CircleBorder()),  # 让按钮变成圆形
                        on_click=lambda _: dir_path_picker.get_directory_path()
                    ),
                    dir_path
                ],
                    expand=True
                ),
                # 缩写功能
                check_box,
                # 开始按钮及进度条
                ft.Column(
                    [
                        ft.ElevatedButton("开始加工",
                                          on_click=lambda _: self.business_logic(file_path.value, dir_path.value, self.page,
                                                                            check_box, progress_ring, finished_icon,
                                                                            error_icon, progress_text)),
                        ft.Row([progress_ring, finished_icon, error_icon], alignment=ft.MainAxisAlignment.CENTER,
                               spacing=0),
                        progress_text
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # 垂直居中
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 水平居中
                    spacing=30,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # 整个页面内容垂直居中
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # 整个页面内容水平居中
            spacing=20,  # 让 Column 撑满屏幕
        )

    def business_logic(self,file_path: str,
                   out_put_path: str,
                   page: ft.Page,
                   check_box: ft.Checkbox,
                   ft_progress_ring: ft.ProgressRing,
                   ft_finished_icon: ft.Icon,
                   ft_error_icon: ft.Icon,
                   ft_text: ft.Text):
        try:
            ft_progress_ring.visible = True
            # 检查传入参数合法性
            if not file_path or not out_put_path:
                raise RuntimeError("未选择待加工文件或输出文件夹")
            if Path(file_path).suffix.lower() not in {'.xlsx'}:
                raise RuntimeError("非xlsx文件，无法加工！")
            ft_finished_icon.visible = False
            ft_error_icon.visible = False
            page.update()
            ft_text.value = "开始获取文件表头"
            page.update()
            col_dic = self.get_translation_columns_map(file_path)
            ft_text.value = "开始翻译表头"
            page.update()
            cn_en_map = self.en_col_processing(col_dic, check_box.value)
            ft_text.value = "开始生成数据"
            page.update()
            df = self.change_col(file_path, cn_en_map)
            ft_text.value = f"开始写入文件:EN_{Path(file_path).stem}"
            page.update()
            self.df_writer(df, Path(file_path).stem, out_put_path)
            ft_finished_icon.visible = True
            ft_text.value = "处理完成！"
            page.update()

        except Exception as e:
            ft_error_icon.visible = True
            ft_text.value = str(e)
        finally:
            ft_progress_ring.visible = False
            page.update()


    def get_translation_columns_map(self,file_path: str) -> dict[str, list[str] | Any]:
        raw_columns = pd.read_excel(file_path, engine='openpyxl', nrows=1).columns.to_list()
        col_map = {}
        for col in raw_columns:
            need_pinyin = True
            max_similarity = 0.0
            cleaned_col = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', col)
            en_cn_dict = json_loader.loader(resource_path("assets/data/odap/en_cn_dic.json"))
            # 字典匹配优先，若匹配不上则使用拼音
            for key in en_cn_dict.keys():
                distance = Levenshtein.distance(cleaned_col, key)
                similarity = 1 - (distance / max(len(cleaned_col), len(key)))
                if similarity > max_similarity:
                    max_similarity = similarity
                if max_similarity > 0.8:
                    col_map[cleaned_col] = en_cn_dict[key]
                    need_pinyin = False
                    break
            if need_pinyin:
                col_map[cleaned_col] = lazy_pinyin(cleaned_col)
        return col_map


    def en_col_processing(self,cn_en_map: dict, abbreviation_switch: bool = False) -> dict:
        for k, v in cn_en_map.items():
            en_col = ''
            first_iteration = True
            if isinstance(v, list):
                for i in v:
                    if abbreviation_switch:
                        en_col = en_col + str(i)[0].upper()
                    else:
                        if first_iteration:
                            en_col = en_col + str(i).upper()
                            first_iteration = False
                        else:
                            en_col = en_col + '_' + str(i).upper()
            else:
                en_col = v
            if re.match(r"^\d+", en_col):
                en_col = f"F{en_col}"
            cn_en_map[k] = en_col
        return cn_en_map


    def change_col(self, file_path: str, cn_en_map: dict) -> DataFrame:
        df = pd.read_excel(file_path, engine='openpyxl')
        # 格式化时间列
        # 使用正则表达式匹配列名
        pattern = re.compile(r"(日期|时间)")  # 匹配列名包含“日期”或“时间”的列
        date_cols = [col for col in df.columns if pattern.search(col)]
        # 转换匹配到的日期列格式
        df[date_cols] = df[date_cols].apply(lambda x: pd.to_datetime(x, errors="coerce").dt.strftime("%Y%m%d"))

        # 去除特殊符号
        cleaned_col = [re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', col) for col in df.columns]
        bilingual_headers = [cleaned_col, [cn_en_map[col] for col in cleaned_col]]
        df.columns = pd.MultiIndex.from_arrays(bilingual_headers)
        return df


    def df_writer(self,df: pd.DataFrame, file_name: str, out_put_path: str, force_csv=False):
        if force_csv or len(df.columns) >= 30 or df.shape[0] > 20000:
            df.to_csv(Path(out_put_path, 'ODAP_' + file_name + '.csv'),encoding='utf-8',index=False)
        else:
            with pd.ExcelWriter(Path(out_put_path, 'ODAP_' + file_name + '.xlsx'), engine='openpyxl') as writer:
                pd.DataFrame([df.columns.get_level_values(0)]).to_excel(writer, startrow=0, index=False, header=False)
                pd.DataFrame([df.columns.get_level_values(1)]).to_excel(writer, startrow=1, index=False, header=False)
                df_tmp = df.copy()
                df_tmp.columns = ['_'.join(map(str, col)) for col in df_tmp.columns]
                df_tmp.to_excel(writer, startrow=2, index=False, header=False)
