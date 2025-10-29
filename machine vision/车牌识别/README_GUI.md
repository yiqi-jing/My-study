车牌识别可视化 GUI

说明:
- 新增 `cs2_gui.py`：基于 Tkinter 的简单可视化界面。界面可选择一个图片文件夹，点击“加载并识别”会在后台调用 `cs2.py` 中的 `batch_process(folder)` 函数进行识别，并把识别结果（图片缩略图 + 车牌信息）平铺显示。

依赖（可选但推荐）:
- Pillow（用于加载与显示图片缩略图）
  安装：

```powershell
python -m pip install --user pillow
```

使用方法:
1. 确保 `cs2.py` 与 `cs2_gui.py` 在同一目录（`f:\My-study\machine vision\车牌识别`）。
2. 在 PowerShell 中运行：

```powershell
C:/Users/yelan/AppData/Local/Microsoft/WindowsApps/python3.8.exe "f:\My-study\machine vision\车牌识别\cs2_gui.py"
```

注意:
- GUI 会在后台调用 `batch_process`，该函数会遍历指定文件夹下的图片并返回包含识别信息的列表。
- 如果没有安装 Pillow，则界面仍可运行，但只会显示图片文件名而非缩略图。
- 若 `cs2.py` 有错误或导入失败，GUI 会弹窗提示。

后续改进建议:
- 在图像上显示识别框（需要 `recognize_plate` 返回 bbox 信息），点击缩略图可弹出大图并叠加 bbox。
- 添加筛选/分页、按识别状态过滤、导出 CSV。