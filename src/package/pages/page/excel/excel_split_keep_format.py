from pathlib import Path
from typing import Any

import flet as ft
from openpyxl import load_workbook

from .excel_split_v2 import ExcelSplitPageV2
from ....components.progress_ring_components import ProgressRingComponent
from ....enums.progress_status_enums import ProgressStatus


class ExcelSplitKM:
    class ExcelSplitConfig:
        def __init__(self):
            self.split_model: int = 0
            self.split_sub_model: str = ""
            self.split_config: list[dict[str, Any]] = []

    def __init__(self, progress: ProgressRingComponent):
        self.progress: ProgressRingComponent = progress

    def split_keep_format(self, excel: ExcelSplitPageV2.ExcelObject, excel_split_config: ExcelSplitConfig,
                          output_folder_path: str) -> bool:
        # model-0:simply split model-1:split_multiple_headers
        if excel_split_config.split_model == 0:
            if excel_split_config.split_sub_model == 'sheet':
                return self._split_file_by_sheet(excel, output_folder_path)
            elif excel_split_config.split_sub_model == 'col':
                pass
            pass
        elif excel_split_config.split_model == 1:
            if excel_split_config.split_sub_model == 'single':
                pass
            elif excel_split_config.split_sub_model == 'multiple':
                pass
            pass

        pass

    def _split_file_by_sheet(self, excel: ExcelSplitPageV2.ExcelObject, output_folder_path: str) -> bool:
        try:
            from openpyxl import load_workbook, Workbook

            self.progress.update_status(ProgressStatus.LOADING, '开始按Sheet拆分并保持格式')
            original_wb = load_workbook(excel.file_path)
            file_name = Path(excel.file_path).stem
            for sheet_name in excel.sheets.keys():
                self.progress.update_status(ProgressStatus.LOADING, f'生成格式化文件: {sheet_name}')

                # Create new workbook with single sheet
                new_wb = Workbook()
                new_ws = new_wb.active
                new_ws.title = sheet_name

                # Copy the original sheet content and formatting
                original_ws = original_wb[sheet_name]
                _copy_worksheet_complete(original_ws, new_ws)

                # Save the new file
                output_file = Path(output_folder_path, f"{file_name}_{sheet_name}.xlsx")
                new_wb.save(output_file)
                new_wb.close()

            original_wb.close()
            self.progress.update_status(ProgressStatus.SUCCESS, '按Sheet格式保持拆分完成')
            return True

        except Exception as e:
            self.progress.update_status(ProgressStatus.ERROR, f'按Sheet格式保持拆分失败: {str(e)}')
            return False

    def _split_with_format_preserved(excel: ExcelSplitPageV2.ExcelObject, output_folder_path_text: ft.TextField,
                                     sheet_name: str, column_name: str,
                                     progress: ProgressRingComponent):
        """
        Split Excel file while preserving original formatting using openpyxl.

        This method creates separate Excel files for each unique value in the specified column
        while maintaining all the original formatting including fonts, colors, borders,
        column widths, row heights, and merged cells.

        Args:
            output_folder_path_text (ft.TextField): Text field containing output folder path
            sheet_name (str): Name of the sheet to split
            column_name (str): Name of the column to group by for splitting
            progress (ProgressRingComponent): Progress indicator component
        """
        try:

            progress.update_status(ProgressStatus.LOADING, '开始格式保持拆分')

            # Load the original workbook with openpyxl to preserve formatting
            original_wb = load_workbook(excel.file_path)
            original_ws = original_wb[sheet_name]

            # Get the data for splitting
            df = excel.sheets[sheet_name].df_data
            file_name = Path(excel.file_path).stem

            # Find the column index for the split column
            split_column_idx = None
            for idx, col in enumerate(df.columns):
                if col == column_name:
                    split_column_idx = idx + 1  # openpyxl uses 1-based indexing
                    break

            if split_column_idx is None:
                raise ValueError(f"Column '{column_name}' not found in sheet '{sheet_name}'")

            # Group the data by the specified column
            grouped = df.groupby(column_name)

            for group_value, group_data in grouped:
                progress.update_status(ProgressStatus.LOADING, f'生成格式化文件: {group_value}')

                # Create a new workbook by copying the original
                new_wb = load_workbook(excel.file_path)
                new_ws = new_wb[sheet_name]

                # Clear existing data while keeping formatting structure
                _clear_worksheet_data(new_ws)

                # Insert new data while preserving formatting
                _insert_data_with_format(new_ws, group_data, original_ws)

                # Save the new file
                output_file = Path(output_folder_path_text.value, f"{file_name}_{group_value}.xlsx")
                new_wb.save(output_file)
                new_wb.close()

            original_wb.close()
            progress.update_status(ProgressStatus.SUCCESS, '格式保持拆分完成')

            if checkBox.value:
                open_folder_in_explorer(output_folder_path_text.value)

        except Exception as e:
            progress.update_status(ProgressStatus.ERROR, f'格式保持拆分失败: {str(e)}')


def _clear_worksheet_data(self, worksheet):
    """
    Clear data from worksheet while preserving formatting structure.

    Args:
        worksheet: openpyxl worksheet object
    """
    # Find the data range (skip header row if exists)
    max_row = worksheet.max_row
    max_col = worksheet.max_column

    # Clear data starting from row 2 (assuming row 1 is header)
    for row in range(2, max_row + 1):
        for col in range(1, max_col + 1):
            cell = worksheet.cell(row=row, column=col)
            cell.value = None


def _insert_data_with_format(self, worksheet, dataframe, original_worksheet):
    """
    Insert dataframe data into worksheet while preserving original formatting.

    Args:
        worksheet: Target openpyxl worksheet
        dataframe: pandas DataFrame containing the data to insert
        original_worksheet: Original worksheet for format reference
    """
    from openpyxl.utils.dataframe import dataframe_to_rows

    # Insert data starting from row 2 (assuming row 1 is header)
    start_row = 2

    for r_idx, row in enumerate(dataframe_to_rows(dataframe, index=False, header=False)):
        for c_idx, value in enumerate(row):
            target_cell = worksheet.cell(row=start_row + r_idx, column=c_idx + 1)
            target_cell.value = value

            # Copy formatting from original if within bounds
            original_row = start_row + r_idx
            if original_row <= original_worksheet.max_row:
                original_cell = original_worksheet.cell(row=original_row, column=c_idx + 1)
                _copy_cell_format(original_cell, target_cell)


def _copy_cell_format(self, source_cell, target_cell):
    """
    Copy formatting from source cell to target cell.

    Args:
        source_cell: Source openpyxl cell
        target_cell: Target openpyxl cell
    """
    if source_cell.has_style:
        # Copy font
        target_cell.font = source_cell.font.copy()
        # Copy border
        target_cell.border = source_cell.border.copy()
        # Copy fill
        target_cell.fill = source_cell.fill.copy()
        # Copy number format
        target_cell.number_format = source_cell.number_format
        # Copy alignment
        target_cell.alignment = source_cell.alignment.copy()
        # Copy protection
        target_cell.protection = source_cell.protection.copy()


def _copy_worksheet_complete(self, source_ws, target_ws):
    """
    Complete copy of worksheet including data, formatting, and structure.

    Args:
        source_ws: Source openpyxl worksheet
        target_ws: Target openpyxl worksheet
    """
    # Copy cell data and formatting
    for row in source_ws.iter_rows():
        for cell in row:
            target_cell = target_ws.cell(row=cell.row, column=cell.column)
            target_cell.value = cell.value

            # Copy all formatting
            if cell.has_style:
                target_cell.font = cell.font.copy()
                target_cell.border = cell.border.copy()
                target_cell.fill = cell.fill.copy()
                target_cell.number_format = cell.number_format
                target_cell.protection = cell.protection.copy()
                target_cell.alignment = cell.alignment.copy()

    # Copy column dimensions
    for col in source_ws.column_dimensions:
        target_ws.column_dimensions[col].width = source_ws.column_dimensions[col].width

    # Copy row dimensions
    for row in source_ws.row_dimensions:
        target_ws.row_dimensions[row].height = source_ws.row_dimensions[row].height

    # Copy merged cells
    for merged_range in source_ws.merged_cells.ranges:
        target_ws.merge_cells(str(merged_range))

    # Copy sheet properties
    if hasattr(source_ws, 'sheet_properties') and hasattr(target_ws, 'sheet_properties'):
        target_ws.sheet_properties.tabColor = source_ws.sheet_properties.tabColor


def _format_preserved_simple_split_excel(self, output_folder_path_text: ft.TextField):
    """
    Enhanced simple split function with format preservation option.

    Args:
        output_folder_path_text (ft.TextField): Output folder path text field

    Returns:
        ft.Column: UI column component for format-preserved splitting
    """

    def redio_on_change(mode: ft.RadioGroup, button: ft.ElevatedButton, sheet_dropdown: ft.Dropdown,
                        columns_dropdown: ft.Dropdown):
        if mode.value == '0':
            sheet_dropdown.value = None
            columns_dropdown.value = None
            sheet_dropdown.options = []
            columns_dropdown.options = []
            sheet_dropdown.disabled = True
            columns_dropdown.disabled = True
            button.disabled = False  # Sheet splitting doesn't need column selection
            sheet_dropdown.update()
            columns_dropdown.update()
            page.update()
        else:
            if excel:
                sheet_dropdown.options = []
                sheet_dropdown.options = [ft.DropdownOption(value) for value in excel.sheets.keys()]
                sheet_dropdown.disabled = False
                columns_dropdown.disabled = False
                button.disabled = True  # Will be enabled after selections
                sheet_dropdown.update()
                page.update()

    def sheet_dropdown_changed(selector: ft.Dropdown, columns_selector: ft.Dropdown, button: ft.ElevatedButton):
        if columns_selector.value is not None:
            columns_selector.value = None
            columns_selector.visible = False
            sleep(0.01)
            columns_selector.visible = True
        columns_selector.options = [ft.DropdownOption(value) for value in excel.sheets[selector.value].columns]
        columns_selector.update()
        button.disabled = False
        page.update()

    def format_preserved_business_logic(
            mode: ft.RadioGroup,
            sheet_selector: ft.Dropdown,
            columns_selector: ft.Dropdown,
            folder_path_text: ft.TextField,
            progress: ProgressRingComponent
    ):
        try:
            if excel is None:
                raise RuntimeError('未提供待拆分文件或输出文件夹')

            # 根据列拆分（保持格式）
            if mode.value == '1':
                _split_with_format_preserved(
                    folder_path_text,
                    sheet_selector.value,
                    columns_selector.value,
                    progress
                )
            # 根据Sheet拆分（保持格式）
            elif mode.value == '0':
                _split_sheets_with_format_preserved(folder_path_text, progress)

        except Exception as e:
            progress.update_status(ProgressStatus.ERROR, str(e))

    # GUI Components
    sheet_selector = ft.Dropdown(
        label='请选择Sheet页',
        on_change=lambda _: sheet_dropdown_changed(sheet_selector, columns_selector, split_button),
        options=[],
        width=200,
        disabled=disable,
    )

    columns_selector = ft.Dropdown(
        label='请选择拆分列',
        options=[],
        width=300,
        disabled=disable,
    )

    # Split mode selection
    mode = ft.RadioGroup(
        ft.Row(
            [
                ft.Radio(value="0", label="根据Sheet拆分（保持格式）"),
                ft.Radio(value="1", label="根据列拆分（保持格式）"),
            ]
        ),
        value="0",
        on_change=lambda _: redio_on_change(mode, None, sheet_selector, columns_selector)
    )

    # Progress indicator
    handel_progress = ProgressRingComponent()

    # Split button
    split_button = ft.ElevatedButton(
        text='开始格式保持拆分',
        on_click=lambda _: format_preserved_business_logic(
            mode,
            sheet_selector,
            columns_selector,
            output_folder_path_text,
            handel_progress
        )
    )

    return ft.Column(
        controls=[
            ft.Row([ft.Text('选择格式保持拆分模式:'), mode], spacing=15),
            ft.Row([sheet_selector, columns_selector], alignment=ft.MainAxisAlignment.CENTER, expand=True),
            ft.Row([split_button], alignment=ft.MainAxisAlignment.CENTER, expand=True),
            handel_progress
        ],
        spacing=30,
    )
